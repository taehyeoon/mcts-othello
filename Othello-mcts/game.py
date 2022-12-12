from copy import deepcopy
from OthelloNN import Othello_utils as Utils
from mcts import *
import json
import time

BLACK = 1
WHITE = -1
EMPTY = 0
STONE = {BLACK: '●', WHITE: '○', EMPTY: '.'}


class Board:
    def __init__(self, board_to_copy=None, turn=0):

        if turn == 0:
            raise Exception("Board의 turn 변수를 1또는 -1로 초기화 해야합니다")
        self.this_turn = turn

        self.position = [[EMPTY] * 8 for _ in range(8)]
        self.position[3][3] = WHITE
        self.position[4][4] = WHITE
        self.position[3][4] = BLACK
        self.position[4][3] = BLACK

        if board_to_copy is not None:
            self.__dict__ = deepcopy(board_to_copy.__dict__)

    def swap_player(self):
        self.this_turn = BLACK if self.this_turn == WHITE else WHITE

    def make_move(self, row, col):
        result_board = Board(board_to_copy=self, turn=self.this_turn)
        available, next_state = Utils.check_set(result_board.position, row, col, self.this_turn)

        if available:
            result_board.position = next_state
        else:
            raise Exception(f"func : make_move : ({row}, {col})은 {STONE[self.this_turn]}가 둘수 없는 자리입니다")

        result_board.swap_player()

        return result_board

    def who_is_win(self):
        """
        게임 결과 계산
        :return:
        BLACK wins 1
        WHITE wins -1
        DRAW 0
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

    def generate_boards(self):
        """
        현재 state에서 player가 둘 수 있는 action들을 구하고 해당 위치에 두었을 떄의 state를 리스트로 반환한다
        :return:
        """
        next_boards = []
        actions = []

        availale, availale_pos_list = Utils.check_able(self.position, self.this_turn)
        if availale:
            for row, col in availale_pos_list:
                next_boards.append(self.make_move(row, col))
                actions.append((row, col))

        return next_boards, actions

    def is_end(self):
        """
        흑, 백이 둘 곳이 있는지 확인
        :return:
        흑, 백이 모두 둘 곳이 없다면 True
        """
        can_black_put = Utils.check_able(self.position, BLACK)[0]
        can_white_put = Utils.check_able(self.position, WHITE)[0]

        return not can_black_put and not can_white_put

    def game_loop(self):
        print("OTHELLO GAME")
        print("TYPE \'exit\' to quit game")
        print('Move format [x,y]: 1,2 where 1 is column and 2 is row')
        print("\n")

        mcts = MCTS()
        # 게임 기록에 관한 데이터를 저장
        history = []

        while True:
            print("BLACK") if self.this_turn == BLACK else print("WHITE")  # debug
            print(Utils.check_able(self.position, self.this_turn)[1])
            self.show_state()

            # 현재 차례가 둘 곳이 없는 경우 스킵
            if not Utils.check_able(self.position, self.this_turn)[0]:
                self.swap_player()
                continue

            best_move = mcts.search(self)
            self = best_move.board
            history.append(mcts.get_data())

            # 흑, 백 모두 둘 곳이 없는 경우
            if self.is_end():
                break

        self.show_state()
        result = self.who_is_win()
        if result == 1:
            print("BLACK is win")
        elif result == -1:
            print("WHITE is win")
        else:
            print("DRAW")

        # JSON에 저장되는 데이터 리스트
        data_to_be_stored = []
        for idx, data in enumerate(history):
            move = dict()
            move['state'] = data[0]
            if idx == 0:
                move['uct'] = 0
            else:
                move['uct'] = history[idx-1][1]

            actions = []
            for val in data[2]:
                action_data = dict()
                action_data['action'] = str(val[0]) + "," + str(val[1])
                action_data['count'] = val[2]
                actions.append(action_data)
            move['actions'] = actions

            move['reward'] = data[3]
            move['turn'] = data[4]
            data_to_be_stored.append(move)

        filename = 'game1.json'
        with open(filename, 'w', encoding='utf-8') as make_file:
            json.dump(data_to_be_stored, make_file, indent='\t')

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
    start = time.time()
    board = Board(turn=BLACK)
    board.game_loop()
    print("소요시간(초) : ", time.time() - start)

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
                [BLACK, WHITE, BLACK, WHITE, WHITE, WHITE, WHITE, EMPTY],
                [WHITE, BLACK, EMPTY, BLACK, BLACK, WHITE, WHITE, WHITE],
                [BLACK, BLACK, BLACK, BLACK, EMPTY, BLACK, WHITE, WHITE],
                [BLACK, WHITE, BLACK, WHITE, BLACK, BLACK, EMPTY, WHITE],
                [BLACK, EMPTY, BLACK, BLACK, BLACK, BLACK, BLACK, WHITE],
                [EMPTY, BLACK, BLACK, EMPTY, BLACK, BLACK, EMPTY, WHITE],
                [BLACK, WHITE, BLACK, BLACK, WHITE, WHITE, WHITE, EMPTY],
                [BLACK, EMPTY, BLACK, WHITE, WHITE, BLACK, WHITE, BLACK]
            ]
"""
