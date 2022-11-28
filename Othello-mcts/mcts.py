"""
An example implementation of the abstract Node class for use in MCTS

If you run this file then you can play against the computer.

A othello board is represented as a list of 8 * 8 values, each either
0, 1, or -1, respectively meaning 'empty', 흑(O)', and '백(X)'.

The board is indexed by row:
    0   1   2   3   4   5   6   7
0
1
2
3               O   X
4               X   O
5
6
7


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


class mcts(object):

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.move = (-1, -1) # Where to put the stone
        self.timeLimit = 3  # 3 seconds is the time limit for search
        self.debug = False  # True for debugging

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
        # 실제로 돌올을 둔다
        self.game.performMove(self.move[0], self.move[1])

    def tree(self, board):
        """

        :param board:
        :return:
        """

    def choose(self, node):
        """
        현재 state를 입력으로 받으면 mcts를 이용히여 최적의 좌표를 리턴한다
        :param node: 현재 state
        :return: 최적의 action 좌표
        """

    def rollout(self, node):
        """

        expand -> simulate -> backpropagate
        :param node: 현재 state
        :return: None
        """

    def select(self, node):
        """
        uct 기준으로 다음 노드 선택
        :param node: 현재 state
        :return: 현재 state에서 terminal state까지 탐색한 path(node list)
        """
    def expend(self, node):
        """
        현재 state에서 child state 확장
        :param node: 현재 state
        :return: None
        """

    def simulate(self, node):
        """
        input state에서 랜덤으로 게임이 종료될 때까지 무작위로 플레이한다
        :param node:
        :return: reward
        """
    def backpropagate(self, node):
        """
        path에 N, Q update
        :param node:
        :return: None
        """
    def uct_select(self, node):
        """
        child node 중 uct가 max인 node를 반환
        :param node:
        :return: child node 중 uct가 max인 node
        """











