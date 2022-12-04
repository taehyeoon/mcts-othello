"""
An example implementation of the abstract Node class for use in MCTS

If you run this file then you can play against the computer.

A othello board is represented as a list of 8 * 8 values, each either
0, 1, or 2, respectively meaning 'empty', 흑(O)', and '백(X)'.

The board is indexed by row:
    0   1   2   3   4   5   6   7
0   -   -   -   -   -   -   -   -
1   -   -   -   -   -   -   -   -
2   -   -   -   -   -   -   -   -
3   -   -   -   O   X   -   -   -
4   -   -   -   X   O   -   -   -
5   -   -   -   -   -   -   -   -
6   -   -   -   -   -   -   -   -
7   -   -   -   -   -   -   -   -


For example, this game board
- - - - - - - -
- - - - - - - -
- - - - - - - -
- - - O X - - -
- - - X O - - -
- - - - - - - -
- - - - - - - -
- - - - - - - -
- - - - - - - -

corrresponds to this list:
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0
0 0 0 1 2 0 0 0
0 0 0 2 1 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0

"""
import copy
from abc import ABC, abstractmethod
from collections import defaultdict
import math
from pprint import pprint
from random import choice
import othello


class mcts(object):

    def __init__(self, game, exploration_weight=1):
        super().__init__()
        self.game = game
        self.move = (-1, -1)  # Where to put the stone
        self.timeLimit = 3  # 3 seconds is the time limit for search
        self.debug = False  # True for debugging

        self.Q = defaultdict(int)  # total reward of each node ex. { node1: 11, node2: 23 }
        self.N = defaultdict(int)  # total visit count for each node ex. { node1: 2, node2: 3 }
        self.children = dict()  # children of each node ex. { node1: [node2, node3], node4: [node5] }
        self.actions = dict()  # action of each case { node1: [(3,2), (5,3)], node4:[(1,2)] }
        self.exploration_weight = exploration_weight

    def performMove(self):
        """
        현재 state에서 최적의 위치에 착수
        :return: None
        """
        state = [row[:] for row in self.game.board]  # we don't want to make changes to the game board
        tmpBoard = Board(state, turn=2, winner=0, terminal=False, game=self.game)
        # self.move = self.miniMax(tmpBoard)
        # print("초기 상태")
        # pprint(state)
        # move에 ai가 돌을 둘 위치 반환
        self.move = self.tree(tmpBoard)

        # perform move (there must be an available move)
        # 실제로 돌을 둔다
        # print("실제로 돌을 두는 곳")
        # print(self.move)
        self.game.performMove(self.move[0], self.move[1])
        # print("돌 놓은 이후")
        # pprint(self.game.board)
    def tree(self, board):
        """

        :param board:
        :return: 착수할 x, y좌표
        """
        for _ in range(50):
            self.rollout(board)
        return self.choose(board)

    # ok
    def choose(self, board):
        """
        현재 state를 입력으로 받으면 mcts를 이용히여 최적의 좌표를 리턴한다
        :param board: 현재 state
        :return: 최적의 action 좌표
        """
        if board.is_terminal():
            raise RuntimeError(f"choose called on terminal node {board}")

        if board not in self.children:
            return board.find_random_child()

        def score(n):
            if self.N[n] == 0:
                return float("-inf")  # avoid unseen moves
            return self.Q[n] / self.N[n]  # average reward

        maxvalue = float("-inf")
        selectedAction = None
        # print(type(self.actions[board]))
        for idx, childnode in enumerate(self.children[board]):
            if score(childnode) > maxvalue:
                selectedAction = self.actions[board][idx]
        # for childnode, action in self.children[board], self.actions[board]:
        #     if score(childnode) > maxvalue:
        #         selectedAction = action
        # print("#############action################################")
        # print(type(selectedAction))
        # print("#############action################################")

        # return max(self.children[node], key=score)
        # 최적의 판을 리턴하는 대신 좌표를 리턴
        return selectedAction

    # ok
    def rollout(self, board):
        """
        확장, 무작위 게임진행, 역전파 순서로 실행
        expand -> simulate -> back propagate
        :param board: 현재 state
        :return: None
        """
        path = self.select(board)
        leaf = path[-1]
        self.expand(leaf)
        reward = self.simulate(leaf)
        self.backpropagate(path, reward)

    # no
    def select(self, board):
        """
        uct 기준으로 다음 노드 선택
        :param board: 현재 state
        :return: 현재 state에서 terminal state까지 탐색한 path(node list)
        """
        path = []
        while True:
            path.append(board)
            #  node가 자식노드 리스트에 없거나 OR 노드의 자식이 없는 경우(단말노드인 경우)
            if board not in self.children or not self.children[board]:
                # node is either unexplored or terminal
                return path
            unexplored = self.children[board] - self.children.keys()
            if unexplored:
                n = unexplored.pop()
                path.append(n)
                return path
            board = self.uct_select(board)  # descend a layer deeper

    # ok
    def expand(self, board):
        """
        현재 state에서 child state 확장
        :param board: 현재 state
        :return: None
        """

        if board in self.children:
            return  # already expanded
        # print(board.find_children())
        # print("#######################################")
        self.children[board], self.actions[board] = board.find_children()

    # ok
    def simulate(self, board):
        """
        input state에서 랜덤으로 게임이 종료될 때까지 무작위로 플레이한다
        :param board:
        :return: reward
        """
        invert_reward = True
        while True:
            if board.is_terminal():
                reward = board.reward()
                return 1 - reward if invert_reward else reward
            # 랜덤한 다음 자식 노드 선택
            board = board.find_random_child()
            invert_reward = not invert_reward

    # ok
    def backpropagate(self, path, reward):
        """
        path에 N, Q update
        :param reward:
        :param path:
        :return: None
        """
        for board in reversed(path):
            self.N[board] += 1
            self.Q[board] += reward
            reward = 1 - reward  # 1 for me is 0 for my enemy, and vice versa

    def uct_select(self, board):
        """
        child node 중 uct가 max인 node를 반환
        :param board:
        :return: child node 중 uct가 max인 node
        """
        assert all(n in self.children for n in self.children[board])

        log_N_vertex = math.log(self.N[board])

        def uct(n):
            "Upper confidence bound for trees"
            return self.Q[n] / self.N[n] + self.exploration_weight * math.sqrt(
                log_N_vertex / self.N[n]
            )

        return max(self.children[board], key=uct)


class Board:
    def __init__(self, state, turn, winner, terminal, game):
        """
        :param state: 2차원 리스트
        :param turn: 1 : black, 2 : white
        :param winner: 1 : black win, 2 : white win, 0 : no winner, -1 : draw
        :param terminal: true / false
        """
        self.state = state
        self.turn = turn
        self.winner = winner
        self.terminal = terminal
        self.game = game

    def find_children(self):
        if self.terminal:  # If the game is finished then no moves can be made
            return set()

        child_board_list = []
        child_action_list = []
        for y, rows in enumerate(self.state):
            for x, cell in enumerate(rows):
                if self.game.placePiece(self.state, x, y, self.turn, PLAYMODE=False):
                    child_board_list.append(self.make_move(x, y))
                    child_action_list.append([x, y])

        return child_board_list, child_action_list

    def find_random_child(self):
        if self.terminal:
            return None

        possible_pos_list = []
        for i in range(8):
            for j in range(8):
                if self.game.placePiece(self.state, i, j, self.turn, PLAYMODE=False) > 0:
                    possible_pos_list.append((i, j))

        if len(possible_pos_list) == 0:
            print("possible_pos_list is empty")
            pprint(self.state)
        rand_x, rand_y = choice(possible_pos_list)
        return self.make_move(rand_x, rand_y)

    def reward(self):
        if not self.terminal:
            raise RuntimeError("reward called on nonterminal board")

        if self.winner is self.turn:
            raise RuntimeError("It's your turn and you've already won. Should be impossible.")

        # 상대방이 이긴 경우
        if self.turn + self.winner == 3:
            return 0

        # 비긴 경우
        if self.winner == -1:
            return 0.5

        raise RuntimeError("board has unknoen winner")

    def is_terminal(self):
        return self.terminal

    def make_move(self, dx, dy):

        state_copy = copy.deepcopy(self.state)
        self.game.placePiece(state_copy, dx, dy, self.turn, PLAYMODE=True)
        state_prime = state_copy
        turn = 3 - self.turn

        allTiles = [item for sublist in state_prime for item in sublist]
        emptyTiles = sum(1 for tile in allTiles if tile == 0)
        whiteTiles = sum(1 for tile in allTiles if tile == 2)
        blackTiles = sum(1 for tile in allTiles if tile == 1)

        if whiteTiles < 1 or blackTiles < 1 or emptyTiles < 1:
            if whiteTiles > blackTiles:
                winner = 2
            elif blackTiles > whiteTiles:
                winner = 1
            else:
                # draw
                winner = -1
        else:
            winner = 0

        is_terminal = False if winner == 0 else True
        return Board(state_prime, turn, winner, is_terminal, self.game)
