import traceback
from copy import deepcopy
from pprint import pprint
from OthelloNN import Othello_utils as Utils
from mcts import *

BLACK = 1
WHITE = -1
EMPTY = 0
STONE = {BLACK: '●', WHITE: '○', EMPTY: '.'}


class Board:

    def __init__(self, board=None):
        self.player_1 = BLACK  # 흑
        self.player_2 = WHITE  # 백
        self.empty_square = EMPTY

        self.position = [[EMPTY] * 8 for i in range(8)]
        self.position[3][3] = WHITE
        self.position[4][4] = WHITE
        self.position[3][4] = BLACK
        self.position[4][3] = BLACK

        if board is not None:
            self.__dict__ = deepcopy(board.__dict__)

    def make_move(self, row, col):
        # 현재 보드와 동일한 임시 보드 생성
        board = Board(self)

        available, next_state = Utils.check_set(board.position, row, col, self.player_1)
        # row, col 자리에 돌을 두고, 뒤집고 난 후의 판을 업데이트 한다
        board.position = next_state

        # swap players
        (board.player_1, board.player_2) = (board.player_2, board.player_1)

        return board

    def who_is_win(self):
        """
        p1이 이기면 1
        p2이 이기면 -1
        비기면 0
        :return:
        """
        p1_score, p2_score = 0, 0

        for row in range(8):
            for col in range(8):
                if self.position[row][col] == self.player_1:
                    p1_score += 1
                elif self.position[row][col] == self.player_2:
                    p2_score += 1

        if p1_score > p2_score:
            return 1
        elif p1_score < p2_score:
            return -1
        else:
            return 0

    def hasPossiblePoint(self, player_num=1):
        """
        플레이어 1 또는 2 가 둘 수 있는 위치가 있는지 여부 확인
        :param player_num: 1 or -1
        :return: True / False
        """
        if player_num == 1:
            player = self.player_1
        else:
            player = self.player_2

        for row in range(8):
            for col in range(8):
                available, available_points = Utils.check_able(self.position, player)
                if available:
                    # player가 둘 곳이 있는 경우 true
                    return True

        return False

    def generate_states(self):
        """
        현재 state에서 player가 둘 수 있는 action들을 구하고 해당 위치에 두었을 떄의 state를 리스트로 반환한다
        :param player_num: 1 , 2
        :return:
        """

        next_states = []
        availale, availale_pos_list = Utils.check_able(self.position, self.player_1)
        if availale:
            for row, col in availale_pos_list:
                next_states.append(self.make_move(row, col))

            return next_states

        """
        next_states = []
        next_turn = -1 # 초기값

        if player_num == 1:
            player = self.player_1
            next_turn = 2
        else:
            player = self.player_2
            next_turn = 1

        availale, availale_pos_list = Utils.check_able(self.position, player)
        if availale:
            for row, col in availale_pos_list:
                next_states.append(self.make_move(row, col))

            return next_states, next_turn

        else:
            # 플레이어를 반대 플레이어로 바꿔서 계산
            if player == self.player_1:
                player = self.player_2
                next_turn = 1
            else:
                player = self.player_1
                next_turn = 2

            availale_opponent, availale_pos_list_opponent = Utils.check_able(self.position, player)
            for row, col in availale_pos_list_opponent:
                next_states.append(self.make_move(row, col))

            return next_states, next_turn
            """

    def is_end(self):
        return not self.hasPossiblePoint(player_num=1) and not self.hasPossiblePoint(player_num=2)

    def game_loop(self):
        print("OTHELLO GAME")
        print("TYPE \'exit\' to quit game")
        print('Move format [x,y]: 1,2 where 1 is column and 2 is row')
        print("\n\n")


        mcts = MCTS()
        # self.position = [
        #     [EMPTY, EMPTY, BLACK, EMPTY, WHITE, WHITE, WHITE, WHITE],
        #     [EMPTY, EMPTY, EMPTY, BLACK, BLACK, WHITE, WHITE, WHITE],
        #     [BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, WHITE, WHITE],
        #     [BLACK, EMPTY, BLACK, WHITE, BLACK, BLACK, EMPTY, WHITE],
        #     [BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, WHITE],
        #     [BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, EMPTY, WHITE],
        #     [BLACK, EMPTY, BLACK, BLACK, EMPTY, EMPTY, EMPTY, EMPTY],
        #     [EMPTY, EMPTY, EMPTY, WHITE, WHITE, WHITE, EMPTY, EMPTY]
        # ]
        while True:
            can_put_stone, lll = Utils.check_able(self.position, BLACK)
            # print(lll)
            # 플레이어가 둘 곳이 있는 경우
            if can_put_stone:
                print("PLAYER TURN")
                self.show_state()
                user_input = input('> ')

                # escape condition
                if user_input == 'exit':
                    break

                # skip empty input
                if user_input == '':
                    continue

                try:

                    # parse user input (move format [col][row]: 1,2)
                    row = int(user_input.split(',')[1])
                    col = int(user_input.split(',')[0])

                    if self.position[row][col] != self.empty_square:
                        print("Illegal move!!")
                        continue

                    possible_to_put, flip_list = Utils.check_set(self.position,row,col,BLACK)
                    if possible_to_put:
                        self = self.make_move(row, col)
                    else:
                        print("놓을 수 있는 자리가 아닙니다.")
                        continue
                except Exception as e:
                    print('  Error:', e)
                    print(traceback.format_exc())
                    print('  Illegal command!')
                    print('  Move format [x,y]: 1,2 where 1 is column and 2 is row')

            self.show_state()
            print("AI TURN")

            best_move = mcts.search(self)
            try:
                self = best_move.board
            except:
                pass

            # 플레이어 1,2 모두 둘 곳이 없는 경우
            if self.is_end():
                result = self.who_is_win()
                if result == 1:
                    print("Player 1 is win")
                    break
                elif result == -1:
                    print("Player 2 is win")
                    break
                else:
                    print("draw")
                    break



    def show_state(self):
        print("\t", end="")
        for i in range(8):
            print(i, end=" ")
        print()

        for row in range(8):
            print(f"{row}\t", end="")
            for col in range(8):
                print(STONE[self.position[row][col]], end=" ")
            print()

if __name__ == "__main__":
    board = Board()
    board.game_loop()


"""
BLACK이 둘 곳이 없는 경우
self.position = [
                [EMPTY, EMPTY, BLACK, EMPTY, WHITE, WHITE, WHITE, WHITE],
                [EMPTY, EMPTY, EMPTY, BLACK, BLACK, WHITE, WHITE, WHITE],
                [BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, WHITE, WHITE],
                [BLACK, EMPTY, BLACK, WHITE, BLACK, BLACK, EMPTY, WHITE],
                [BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, WHITE],
                [BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, EMPTY, WHITE],
                [BLACK, EMPTY, BLACK, BLACK, EMPTY, EMPTY, EMPTY, EMPTY],
                [EMPTY, EMPTY, EMPTY, WHITE, WHITE, WHITE, EMPTY, EMPTY]
            ]
            
    
"""
