"""
An example implementation of the abstract Node class for use in MCTS

If you run this file then you can play against the computer.

A othello board is represented as a list of 8 * 8 values, each either
0, 1, or -1, respectively meaning 'empty', 흑(O)', and '백(X)'.

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
0 0 0 1 -1 0 0 0
0 0 0 -1 1 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0

"""
from abc import ABC, abstractmethod
from collections import defaultdict
import math

class mcts(object):

    def __init__(self, game, exploration_weight=1):
        super().__init__()
        self.game = game
        self.move = (-1, -1) # Where to put the stone
        self.timeLimit = 3  # 3 seconds is the time limit for search
        self.debug = False  # True for debugging

        self.Q = defaultdict(int)  # total reward of each node ex. { node1: 11, node2: 23 }
        self.N = defaultdict(int)  # total visit count for each node ex. { node1: 2, node2: 3 }
        self.children = dict()  # children of each node ex. { node1: [node2, node3], node4: [node5] }
        self.actions = dict # action of each case { node1: [(3,2), (5,3)], node4:[(1,2)] }
        self.exploration_weight = exploration_weight

    def performMove(self):
        """
        현재 state에서 최적의 위치에 착수
        :return: None
        """
        tmpBoard = [row[:] for row in self.game.board]  # we don't want to make changes to the game board
        # self.move = self.miniMax(tmpBoard)

        # move에 ai가 돌을 둘 위치 반환
        self.move = self.tree(tmpBoard)

        # perform move (there must be an available move)
        # 실제로 돌을 둔다
        self.game.performMove(self.move[0], self.move[1])

    def tree(self, board):
        """

        :param board:
        :return:
        """
        for _ in range(50):
            self.rollout(board)
        return self.choose(board)


    def choose(self, node):
        """
        현재 state를 입력으로 받으면 mcts를 이용히여 최적의 좌표를 리턴한다
        :param node: 현재 state
        :return: 최적의 action 좌표
        """
        if node.is_terminal():
            raise RuntimeError(f"choose called on terminal node {node}")

        if node not in self.children:
            return node.find_random_child()

        def score(n):
            if self.N[n] == 0:
                return float("-inf")  # avoid unseen moves
            return self.Q[n] / self.N[n]  # average reward

        maxvalue = float("-inf")
        selectedAction = None
        for childnode, action in self.children[node], self.actions[node]:
            if score(childnode) > maxvalue:
                selectedAction = action

        # return max(self.children[node], key=score)
        # 최적의 판을 리턴하는 대신 좌표를 리턴
        return selectedAction

    def rollout(self, node):
        """
        expand -> simulate -> back propagate
        :param node: 현재 state
        :return: None
        """
        path = self.select(node)
        leaf = path[-1]
        self.expand(leaf)
        reward = self.simulate(leaf)
        self.backpropagate(path, reward)


    def select(self, node):
        """
        uct 기준으로 다음 노드 선택
        :param node: 현재 state
        :return: 현재 state에서 terminal state까지 탐색한 path(node list)
        """
        path = []
        while True:
            path.append(node)
            #  node가 자식노드 리스트에 없거나 OR 노드의 자식이 없는 경우(단말노드인 경우)
            if node not in self.children or not self.children[node]:
                # node is either unexplored or terminal
                return path
            unexplored = self.children[node] - self.children.keys()
            if unexplored:
                n = unexplored.pop()
                path.append(n)
                return path
            node = self._uct_select(node)  # descend a layer deeper


    def expend(self, node):
        """
        현재 state에서 child state 확장
        :param node: 현재 state
        :return: None
        """
        if node in self.children:
            return  # already expanded
        self.children[node] = node.find_children()
    def simulate(self, node):
        """
        input state에서 랜덤으로 게임이 종료될 때까지 무작위로 플레이한다
        :param node:
        :return: reward
        """
        invert_reward = True
        while True:
            if node.is_terminal():
                reward = node.reward()
                return 1 - reward if invert_reward else reward
            node = node.find_random_child()
            invert_reward = not invert_reward
    def backpropagate(self, path, node):
        """
        path에 N, Q update
        :param node:
        :return: None
        """
        for node in reversed(path):
            self.N[node] += 1
            self.Q[node] += reward
            reward = 1 - reward  # 1 for me is 0 for my enemy, and vice versa

    def uct_select(self, node):
        """
        child node 중 uct가 max인 node를 반환
        :param node:
        :return: child node 중 uct가 max인 node
        """
        assert all(n in self.children for n in self.children[node])

        log_N_vertex = math.log(self.N[node])

        def uct(n):
            "Upper confidence bound for trees"
            return self.Q[n] / self.N[n] + self.exploration_weight * math.sqrt(
                log_N_vertex / self.N[n]
            )

        return max(self.children[node], key=uct)

class Board:
    def __init__(self):
        self.board = [[0] * 8 for i in range(8)]
        self.turn = None
        self.winner = None
        self.terminal = False








