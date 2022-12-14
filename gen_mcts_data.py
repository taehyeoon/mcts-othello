import torch
from multiprocessing import Process, Pool, freeze_support

import os
import tqdm
import time

from OthelloMCTS.game import Board
from OthelloNN import OthelloNNet

BLACK = 1
WHITE = -1



if __name__ == '__main__':
    freeze_support()
    mcts_num=1
    process_num=4
    board = Board(turn=BLACK)
    # one_game=board.game_loop()
    path = "H:/내 드라이브/OSSP2/games/"
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = OthelloNNet.ConnectNet().to(device)
    if os.path.isfile('model.pth'):
        checkpoint = torch.load('model.pth',map_location=torch.device(device))
        model.load_state_dict(checkpoint['model_state_dict'])

    progress_bar = tqdm.tqdm(total=mcts_num*process_num)
    progress_bar.set_description('MCTS데이터 생성중')
    for mn in range(mcts_num):
        p_list =[]
        for pn in range(mn*process_num,(mn+1)*process_num):
            p = Process(target=board.game_loop, args=(path+"game"+str(pn)+'.json',model,))
            p.daemon = True
            p_list.append(p)
            p_list[-1].start()
        for pp in p_list:
            pp.join()
        progress_bar.update(process_num)
    progress_bar.close()
    
    print(os.listdir('games'))