import math
import random
from pprint import pprint

BLACK = 1
WHITE = -1
EMPTY = 0
STONE = {BLACK: '●', WHITE: '○', EMPTY: '.'}

ITER = 100
PRINT_INTERVAL = 10

WIN_POINT = 10
LOSE_POINT = 0
DRAW_POINT = 3


class Node:
    def __init__(self, board, parent=None):
        """

        :param board:
        :param parent:
        """
        self.board = board

        # 플레이어 1, 2 모두 둘 곳이 없는 경우
        if self.board.is_end():
            self.is_terminal = True
        else:
            self.is_terminal = False

        # init is fully expanded flag
        self.is_fully_expanded = self.is_terminal

        # init parent node if available
        self.parent = parent

        # init the number of node visits
        self.visits = 0

        # init the total score of the node
        self.score = 0

        # init current node's children
        # key : 8*8의 2차원 리스트의 string ex) str(board.position)
        # value : [Node, action]
        # action : (row, col)
        self.children = {}


class MCTS:

    def __init__(self):
        self.root = None
        self.exploration_constant = math.sqrt(2)
        self.selected_child_node = None

    def search(self, initial_board):
        self.selected_child_node = None
        self.root = Node(initial_board, None)

        for iteration in range(ITER):
            node = self.select(self.root)

            # score = self.rollout(node.board)
            result = self.rollout(node.board)

            # self.backpropagate(node, score)
            self.backpropagate(node, result)
            if iteration % PRINT_INTERVAL == 0:
                print(f"iter : {iteration}")
                # print(f"child의 개수 : {len(self.root.children)}") # debug


        print("-------------------------------------")
        print(f"child 개수 : {len(self.root.children)}")
        for key, val in self.root.children.items():
            print("방문횟수 : ", end="")
            print(val[0].visits)
            print("UCT 값 : ", end="")
            print(self.get_uct(val[0]))
            val[0].board.show_state()
            print()
        print("-------------------------------------")

        self.selected_child_node = self.get_best_move(self.root)
        return self.selected_child_node

    def select(self, node):
        while not node.is_terminal:
            if node.is_fully_expanded:
                node = self.get_best_move(node)
            else:
                expanded_node = self.expand(node)
                if expanded_node is not None:
                    return expanded_node
                else:
                    node.board.swap_player()

        return node

    def expand(self, node):
        """
        플레이어 1의 turn인 경우, 가능한 child를 하나 확장한다
        만약 모든 child node가 확장된 경우 -> is_fully_expanded를 True로 수정
        :param node: 확장할 노드
        :return: 확장한 child node
        """
        # print(f"현재 노드의 차례 : {node.board.this_turn}") # debug
        all_child_boards, actions = node.board.generate_boards()

        # 해당 턴에 둘 곳이 없는 경우
        if len(all_child_boards) == 0:
            return None
        # print(f"type : {type(all_child_boards)}, len : {len(all_child_boards)}")  # debug

        for board, action in zip(all_child_boards, actions):
            if str(board.position) not in node.children:
                new_node = Node(board, node)

                node.children[str(board.position)] = [new_node, action]

                if len(all_child_boards) == len(node.children):
                    node.is_fully_expanded = True

                # print(f"찾은 state의 개수 : {len(all_child_boards)}, 현재 노드의 child개수{len(node.children)}")  # debug
                # board.show_state()  # debug
                # print()
                return new_node

    def rollout(self, board):
        while not board.is_end():
            try:
                next_boards = board.generate_boards()[0]
                # print(next_turn, end="")
                board = random.choice(next_boards)
            except:
                return 0

        # 방금 직전에 둔 돌은 player_2의 색깔
        # 게임이 종료되었다는 의미는 player_2가 두고나서 게임이 끝났다는 의미

        # draw
        if board.who_is_win() == 0:
            score = DRAW_POINT
            result = 'DRAW'
        # 게임에서 이긴 색깔이 root node의 색과 같다면 승리한 것으로 판단
        elif board.who_is_win() == self.root.board.this_turn:
            score = WIN_POINT
            result = 'WIN'
        else:
            score = LOSE_POINT
            result = 'LOSE'

        return result

    def backpropagate(self, node, result):
        while node is not None:
            if result == 'DRAW':
                node.score += DRAW_POINT
            else:
                # root와 같은 차례의 노드에 게임결과를 반영
                if node.board.this_turn == self.root.board.this_turn:
                    if result == 'WIN':
                        node.score += WIN_POINT
                    else:
                        node.score += LOSE_POINT
                # root노드와 다른 차례의 노드에는 게임결과의 반대를 반영
                else:
                    if result == 'WIN':
                        node.score += LOSE_POINT
                    else:
                        node.score += WIN_POINT
            node.visits += 1
            node = node.parent

    def get_best_move(self, node):
        best_score = float('-inf')
        best_moves = []

        for child_data in node.children.values():
            # move_score = child_node.score / child_node.visits \
            #              + self.exploration_constant * math.sqrt(math.log(node.visits) / child_node.visits)
            child_node = child_data[0]
            move_score = self.get_uct(child_node)

            if move_score > best_score:
                best_score = move_score
                best_moves = [child_node]

            # found as good move as already available
            elif move_score == best_score:
                best_moves.append(child_node)

        # return one of the best moves randomly
        # 가장 좋은 move들 중 랜덤한게 한 노드를 반환
        return random.choice(best_moves)

    def get_uct(self, node):
        return node.score / node.visits \
                         + self.exploration_constant * math.sqrt(math.log(node.parent.visits) / node.visits)

    def get_data(self):
        # data = [8*8 list, [child의 uct값], [[r,c,n], [r,c,n], ...], reward, turn(1 or -1)]
        data = []
        data.append(self.root.board.position)
        data.append(self.get_uct(self.selected_child_node))
        child_list = []
        for child_node, action in self.root.children.values():
            child_list.append([action[0], action[1], child_node.visits])
        data.append(child_list)
        data.append(self.selected_child_node.score)
        data.append(self.root.board.this_turn)

        return data






