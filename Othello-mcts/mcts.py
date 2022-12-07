import math
import random

BLACK = 1
WHITE = -1
EMPTY = 0
STONE = {BLACK: '●', WHITE: '○', EMPTY: '.'}

ITER = 500


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
        self.children = {}


class MCTS:

    def __init__(self):
        self.root = None

    def search(self, initial_state):
        self.root = Node(initial_state, None)

        for iteration in range(ITER):
            node = self.select(self.root)

            score = self.rollout(node.board)

            self.backpropagate(node, score)
            if iteration % 100 == 0:
                print(f"iter : {iteration}, score = {score}")
        try:
            return self.get_best_move(self.root, 2)
        except:
            pass

    def select(self, node):
        while not node.is_terminal:
            if node.is_fully_expanded:
                node = self.get_best_move(node, 2)
            else:
                return self.expand(node)

        return node

    def expand(self, node):
        """
        플레이어 1의 turn인 경우, 가능한 child를 하나 확장한다
        만약 모든 child node가 확장된 경우 -> is_fully_expanded를 True로 수정
        :param node: 확장할 노드
        :return: 확장한 child node
        """
        states = node.board.generate_states()

        for state in states:
            if str(state.position) not in node.children:
                new_node = Node(state, node)

                node.children[str(state.position)] = new_node

                if len(states) == len(node.children):
                    node.is_fully_expanded = True

                return new_node

    def rollout(self, board):
        # next_turn = 2  # AI차례를 우선적으로 계산
        while not board.is_end():
            try:
                next_states = board.generate_states()
                # print(next_turn, end="")
                board = random.choice(next_states)
            except:
                return 0

        # 방금 직전에 둔 돌은 player_2의 색깔
        # 게임이 종료되었다는 의미는 player_2가 두고나서 게임이 끝났다는 의미
        if board.who_is_win() == 0:
            return 0
        if board.who_is_win() == 1:
            return 1
        if board.who_is_win() == -1:
            return -1

    def backpropagate(self, node, score):
        while node is not None:
            node.visits += 1
            node.score += score
            node = node.parent

    def get_best_move(self, node, exploration_constant):
        best_score = float('-inf')
        best_moves = []

        for child_node in node.children.values():
            if child_node.board.player_2 == BLACK:
                current_player = BLACK
            elif child_node.board.player_2 == WHITE:
                current_player = WHITE

            move_score = current_player * child_node.score / child_node.visits + exploration_constant * math.sqrt(
                math.log(node.visits / child_node.visits))

            if move_score > best_score:
                best_score = move_score
                best_moves = [child_node]

            # found as good move as already available
            elif move_score == best_score:
                best_moves.append(child_node)

        # return one of the best moves randomly
        return random.choice(best_moves)
