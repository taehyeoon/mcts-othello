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

    def __init__(self, board_to_copy=None, turn=0):
        self.player_1 = BLACK  # 흑
        self.player_2 = WHITE  # 백
        self.empty_square = EMPTY

        if turn == 0:
            raise Exception("Board의 turn 변수를 1또는 -1로 초기화 해야합니다")
        self.this_turn = turn

        self.position = [[EMPTY] * 8 for i in range(8)]
        self.position[3][3] = WHITE
        self.position[4][4] = WHITE
        self.position[3][4] = BLACK
        self.position[4][3] = BLACK

        if board_to_copy is not None:
            self.__dict__ = deepcopy(board_to_copy.__dict__)

    def swap_player(self):
        self.this_turn = BLACK if self.this_turn == WHITE else WHITE

    def make_move(self, row, col):
        # 현재 보드와 동일한 임시 보드 생성
        result_board = Board(board_to_copy=self, turn=self.this_turn)
        # print(f"make_move에서 턴 정보 : {self.this_turn}") # debug
        # available, next_state = Utils.check_set(result_board.position, row, col, self.player_1)
        available, next_state = Utils.check_set(result_board.position, row, col, self.this_turn)
        # print(f"make_move에서 avaiable의 값 : {available}") # debug
        if available:
            # row, col 자리에 돌을 두고, 뒤집고 난 후의 판을 업데이트 한다
            result_board.position = next_state
        else:
            raise Exception(f"func : make_move : ({row}, {col})은 {STONE[self.this_turn]}가 둘수 없는 자리입니다")


        # print("swap 실행") # debug
        # swap players
        # (result_board.player_1, result_board.player_2) = (result_board.player_2, result_board.player_1)
        # self.this_turn = self.player_1 if self.this_turn == self.player_2 else self.player_2
        # self.swap_player()
        result_board.swap_player()

        return result_board

    def who_is_win(self):
        """
        BLACK이 이기면 1
        WHITE이 이기면 -1
        비기면 0
        :return:
        """
        black_score, white_score = 0, 0

        for row in range(8):
            for col in range(8):
                if self.position[row][col] == BLACK:
                    black_score += 1
                elif self.position[row][col] == WHITE:
                    white_score += 1

        if black_score > white_score:
            return BLACK
        elif black_score < white_score:
            return WHITE
        else:
            return 0
    # 오직 is_end()에서만 사용하기 때문에 직접 구현하는 방식으로 수정
    # def hasPossiblePoint(self, player_num=1):
    #     """
    #     플레이어 1 또는 2 가 둘 수 있는 위치가 있는지 여부 확인
    #     :param player_num: 1 or -1
    #     :return: True / False
    #     """
    #     if player_num == 1:
    #         player = self.player_1
    #     else:
    #         player = self.player_2
    #
    #     for row in range(8):
    #         for col in range(8):
    #             available, available_points = Utils.check_able(self.position, player)
    #             if available:
    #                 # player가 둘 곳이 있는 경우 true
    #                 return True
    #
    #     return False

    def generate_boards(self):
        """
        현재 state에서 player가 둘 수 있는 action들을 구하고 해당 위치에 두었을 떄의 state를 리스트로 반환한다
        :param player_num: 1 , 2
        :return:
        """

        next_states = []
        # next_turn = BLACK if self.this_turn == WHITE else WHITE
        # availale, availale_pos_list = Utils.check_able(self.position, self.player_1)
        availale, availale_pos_list = Utils.check_able(self.position, self.this_turn)
        if availale:
            # print(f"착수 가능한 포지션 {availale_pos_list}, 현재 차례 : {self.this_turn}") # debug
            for row, col in availale_pos_list:
                next_states.append(self.make_move(row, col))

            return next_states

    def is_end(self):
        end = False
        can_black_put = Utils.check_able(self.position, self.player_1)[0]
        can_white_put = Utils.check_able(self.position, self.player_2)[0]

        return not can_black_put and not can_white_put
        # return not self.hasPossiblePoint(player_num=1) and not self.hasPossiblePoint(player_num=2)

    def game_loop(self):
        print("OTHELLO GAME")
        print("TYPE \'exit\' to quit game")
        print('Move format [x,y]: 1,2 where 1 is column and 2 is row')
        print("\n\n")

        mcts = MCTS()

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

                    possible_to_put, flip_list = Utils.check_set(self.position, row, col, BLACK)
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

            # best_move는 Node형식
            best_move = mcts.search(self)
            try:
                self = best_move.board
            except:
                pass

            # 플레이어 1,2 모두 둘 곳이 없는 경우
            if self.is_end():
                result = self.who_is_win()
                if result == 1:
                    print("BLACK is win")
                    break
                elif result == -1:
                    print("WHITE is win")
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
    board = Board(turn=BLACK)
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
            
# 임의의 게임 state            
self.position = [
                [BLACK, WHITE, BLACK, WHITE, WHITE, WHITE, WHITE, WHITE],
                [WHITE, BLACK, EMPTY, BLACK, BLACK, WHITE, WHITE, WHITE],
                [BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, WHITE, WHITE],
                [BLACK, WHITE, BLACK, WHITE, BLACK, BLACK, EMPTY, WHITE],
                [BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, WHITE],
                [BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, EMPTY, WHITE],
                [BLACK, WHITE, BLACK, BLACK, WHITE, WHITE, WHITE, EMPTY],
                [BLACK, EMPTY, BLACK, WHITE, WHITE, BLACK, WHITE, BLACK]
            ]
    
"""
