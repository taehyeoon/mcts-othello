import torch
from multiprocessing import Process, Pool, freeze_support

import os
import time

from OthelloMCTS.game import Board

BLACK = 1
WHITE = -1



if __name__ == '__main__':
    freeze_support()
    board = Board(turn=BLACK)
    # board.game_loop(3)

    start = time.time()
    for pn in range(3):
        p = Process(target=board.game_loop, args=(pn,))
        p.daemon = True
        p.start()

    for pn in range(3):
        p.join()
    print(time.time() - start)
    
    print(os.listdir('games'))