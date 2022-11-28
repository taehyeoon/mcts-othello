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

        tmpBoard = [row[:] for row in self.game.board]  # we don't want to make changes to the game board
        # self.move = self.miniMax(tmpBoard)

        # move에 ai가 돌을 둘 위치 반환
        self.move = self.mctsearch(tmpBoard)

        # perform move (there must be an available move)
        # 실제로 돌올을 둔다
        self.game.performMove(self.move[0], self.move[1])

    def mctsearch(self, board):






