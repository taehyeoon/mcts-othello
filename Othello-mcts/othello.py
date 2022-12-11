import ai
import mcts

class IllegalMove(Exception):
    def __init__(self, message):
        self.message = message


class Othello(object):
    # 0 - Empty
    # 1 - Black (Player 1)
    # 2 - White (Player 2)

    def __init__(self):
        super().__init__()

        self.player = 1
        self.victory = 0  # 0 - ongoing | 1 - black win | 2 - white win | (-1) - draw
        self.whiteTiles = 2
        self.blackTiles = 1

        self.board = [[0 for x in range(8)] for x in range(8)]
        self.board[3][3] = 1
        self.board[3][4] = 2
        self.board[4][3] = 2
        self.board[4][4] = 1
        # set useAI = False to disable AI opponent - two-player mode
        self.useAI = True

        # set up AI - player-computer mode
        # self.ai = ai.GameAI(self)
        self.ai = mcts.mcts(self)

        self.changed = True
        self.AIReadyToMove = False

        self.debug = False  # True for debugging

    def playerMove(self, x, y):
        # if the game is over or not player's turn
        # 게임 종료 or (ai를 사용하고 사용자의 턴이 아닌경우)
        if self.victory != 0 or (self.useAI and self.player != 1):
            return

        self.performMove(x, y)

        # AI's turn and AI is ready to move
        if self.useAI and self.player == 2:
            self.AIReadyToMove = True
            if self.debug:
                print("AI is ready to move!")

    def performMove(self, x, y):
        if self.debug:
            print("Check whether move (" + str(x) + ", " + str(y) + ") is legal or not ...")

        # check whether the block has been occupied
        if self.board[x][y] != 0:
            raise IllegalMove(" - Block has already been occupied!")
        else:
            # place the piece and flip necessary pieces
            numFlipped = self.placePiece(self.board, x, y, self.player, PLAYMODE=True)
            if self.debug:
                print("Flipped " + str(numFlipped) + " pieces!")
            self.changed = True

            # check game ending
			# 현재 판의 빈곳, 흑돌, 백돌 개수 계산
            allTiles = [item for sublist in self.board for item in sublist]
            emptyTiles = sum(1 for tile in allTiles if tile == 0)
            whiteTiles = sum(1 for tile in allTiles if tile == 2)
            blackTiles = sum(1 for tile in allTiles if tile == 1)
            print("[Console MSG] Current state - empty: " + str(emptyTiles) + " white: " + str(
                whiteTiles) + " black: " + str(blackTiles))

            if self.debug:
                for x in range(0, 8):
                    for y in range(0, 8):
                        print(str(self.board[x][y]) + " ", end='')
                    print('')

            # no moves left to make
			# 백돌이 아예없거나, 흑돌이 아예없거나 빈자리가 없는 경우
            if whiteTiles < 1 or blackTiles < 1 or emptyTiles < 1:
                self.endGame(whiteTiles, blackTiles)
                return

            # check available moves of its opponent
            movesFound = self.moveCanBeMade(self.board, 3 - self.player)
            # 상대방이 둘 곳이 없는 경우
            if not movesFound:
                if self.debug:
                    print("Player " + str(3 - self.player) + " cannot move!")
                # opponent cannot move, do not alternate
                movesFound = self.moveCanBeMade(self.board, self.player)
                # 현재 플레이어도 둘 곳이 없는 경우
                if not movesFound:
                    # this player cannot move either, end game
                    if self.debug:
                        print("Player " + str(self.player) + "cannot move either!")
                    self.endGame(whiteTiles, blackTiles)
                    return
                # 현재 플레이어는 둘 곳이 있는 경우
                else:
                    if self.debug:
                        print("Player " + str(self.player) + " can move, then move!")
                    if self.useAI and self.player == 2:
                        self.ai.performMove()
                    # this player can move, move
                    self.changed = True
            # 상대방이 둘 곳이 있는 경우
            else:
                # opponent can move, alternate between player 1 and 2
                self.player = 3 - self.player
                self.changed = True

    def moveCanBeMade(self, board, playerID):
        """
        현재 판에서 playerID가 착수 할수 있는 위치가 있는지 확인
        :param board: state
        :param playerID: 플레이어 번호
        :return: 착수할수 있는 곳이 있는지 여부 true false
        """
        movesFound = False
        for row in range(0, 8):
            for col in range(0, 8):
                if movesFound:
                    continue
                elif board[row][col] == 0:
                    numAvailableMoves = self.placePiece(board, row, col, playerID, PLAYMODE=False)
                    if numAvailableMoves > 0:
                        movesFound = True
        return movesFound

    def AIMove(self):
        self.ai.performMove()
        self.AIReadyToMove = False

    def endGame(self, whiteTiles, blackTiles):
        if whiteTiles > blackTiles:
            self.victory = 2
        elif whiteTiles < blackTiles:
            self.victory = 1
        else:
            self.victory = -1
        self.changed = True
        self.whiteTiles = whiteTiles
        self.blackTiles = blackTiles

    """ return: the number of flips given that (row, col) will be occupied by player.
		param: PLAYMODE: 
		- True for board flipping after a piece is put by the player
		- False for available number of moves checking
	"""

    def placePiece(self, board, row, col, playerID, PLAYMODE=True):
        # row 좌상단 기준으로 오른쪽으로 떨어진 거리
        # col 좌상단 기준으로 아래로 떨어진 거리

        if PLAYMODE:
            board[row][col] = self.player
        count = 0  # record number of flips

        # record current row and column
        # row col을 기준으로 세로
        __column = board[row]
        # row col을 기준으로 가로
        __row = [board[i][col] for i in range(0, 8)]

        # check up direction
        if playerID in __column[:col]:
            changes = []
            searchCompleted = False

            # (row,col) 좌표에서 한칸 위부터 시작해서 위로 끝까지 한칸씩 탐색
            for i in range(col - 1, -1, -1):
                if searchCompleted:
                    continue
                piece = __column[i]
                # 빈칸이 나오면 탐색 종료
                if piece == 0:
                    changes = []
                    searchCompleted = True
                # 지금 현재 플레이어와 같은 색이 나오면 탐색 종료
                elif piece == playerID:
                    searchCompleted = True
                # 뒤집을 돌을 리스트에 추가
                else:
                    changes.append(i)

            # perform flippings
            if searchCompleted:
                count += len(changes)
                # 실제로 게임이 진행중에 placePiece함수가 호출되었다면 뒤집음
                if PLAYMODE:
                    for i in changes:
                        board[row][i] = self.player

        # check down direction
        if playerID in __column[col:]:
            changes = []
            searchCompleted = False

            for i in range(col + 1, 8, 1):
                if searchCompleted:
                    continue
                piece = __column[i]
                if piece == 0:
                    changes = []
                    searchCompleted = True
                elif piece == playerID:
                    searchCompleted = True
                else:
                    changes.append(i)

            # perform flippings
            if searchCompleted:
                count += len(changes)
                if PLAYMODE:
                    for i in changes:
                        board[row][i] = self.player

        # check left direction
        if playerID in __row[:row]:
            changes = []
            searchCompleted = False

            for i in range(row - 1, -1, -1):
                if searchCompleted:
                    continue
                piece = __row[i]
                if piece == 0:
                    changes = []
                    searchCompleted = True
                elif piece == playerID:
                    searchCompleted = True
                else:
                    changes.append(i)

            # perform flippings
            if searchCompleted:
                count += len(changes)
                if PLAYMODE:
                    for i in changes:
                        board[i][col] = self.player

        # check right direction
        if playerID in __row[row:]:
            changes = []
            searchCompleted = False

            for i in range(row + 1, 8, 1):
                if searchCompleted:
                    continue
                piece = __row[i]
                if piece == 0:
                    changes = []
                    searchCompleted = True
                elif piece == playerID:
                    searchCompleted = True
                else:
                    changes.append(i)

            # perform flippings
            if searchCompleted:
                count += len(changes)
                if PLAYMODE:
                    for i in changes:
                        board[i][col] = self.player

        # check along diagonal directions
        # upper-left direction
        i = 1
        ulDiagonal = []
        while row - i >= 0 and col - i >= 0:
            ulDiagonal.append(board[row - i][col - i])
            i += 1
        if playerID in ulDiagonal:
            changes = []
            searchCompleted = False

            for i in range(0, len(ulDiagonal)):
                piece = ulDiagonal[i]
                if searchCompleted:
                    continue
                if piece == 0:
                    changes = []
                    searchCompleted = True
                elif piece == playerID:
                    searchCompleted = True
                else:
                    changes.append((row - (i + 1), col - (i + 1)))

            # perform flippings
            if searchCompleted:
                count += len(changes)
                if PLAYMODE:
                    for i, j in changes:
                        board[i][j] = self.player

        # upper-right direction
        i = 1
        urDiagonal = []
        while row + i < 8 and col - i >= 0:
            urDiagonal.append(board[row + i][col - i])
            i += 1
        if playerID in urDiagonal:
            changes = []
            searchCompleted = False

            for i in range(0, len(urDiagonal)):
                piece = urDiagonal[i]
                if searchCompleted:
                    continue
                if piece == 0:
                    changes = []
                    searchCompleted = True
                elif piece == playerID:
                    searchCompleted = True
                else:
                    changes.append((row + (i + 1), col - (i + 1)))

            # perform flippings
            if searchCompleted:
                count += len(changes)
                if PLAYMODE:
                    for i, j in changes:
                        board[i][j] = self.player

        # lower-left direction
        i = 1
        llDiagonal = []
        while row - i >= 0 and col + i < 8:
            llDiagonal.append(board[row - i][col + i])
            i += 1
        if playerID in llDiagonal:
            changes = []
            searchCompleted = False

            for i in range(0, len(llDiagonal)):
                piece = llDiagonal[i]
                if searchCompleted:
                    continue
                if piece == 0:
                    changes = []
                    searchCompleted = True
                elif piece == playerID:
                    searchCompleted = True
                else:
                    changes.append((row - (i + 1), col + (i + 1)))

            # perform flippings
            if searchCompleted:
                count += len(changes)
                if PLAYMODE:
                    for i, j in changes:
                        board[i][j] = self.player

        # lower-right direction
        i = 1
        lrDiagonal = []
        while row + i < 8 and col + i < 8:
            lrDiagonal.append(board[row + i][col + i])
            i += 1
        if playerID in lrDiagonal:
            changes = []
            searchCompleted = False

            for i in range(0, len(lrDiagonal)):
                piece = lrDiagonal[i]
                if searchCompleted:
                    continue
                if piece == 0:
                    changes = []
                    searchCompleted = True
                elif piece == playerID:
                    searchCompleted = True
                else:
                    changes.append((row + (i + 1), col + (i + 1)))

            # perform flippings
            if searchCompleted:
                count += len(changes)
                if PLAYMODE:
                    for i, j in changes:
                        board[i][j] = self.player

        if count == 0 and PLAYMODE:
            board[row][col] = 0
            raise IllegalMove("Placing piece at (" + str(row) + ", " + str(col) + ") does not have any flips!")

        return count
