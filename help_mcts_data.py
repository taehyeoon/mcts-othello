import torch
from multiprocessing import Process, Pool, freeze_support

import os
import tqdm
import time
import uuid

from OthelloMCTS.game import Board
from OthelloNN import OthelloNNet

BLACK = 1
WHITE = -1
MACINE_NAME = 'DESKTOP-'+str(uuid.uuid4())
GAMEPATH = "games/"
MODELPATH = "model/"

if __name__ == '__main__':
    freeze_support()
    process_num=10
    board = Board(turn=BLACK)
    # one_game=board.game_loop()
    path = "H:/내 드라이브/OSSP2/games/"
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = OthelloNNet.ConnectNet().to(device)

    mcts_num=0
    
    while True:
        #파일 존재 여부
        p_list =[]
        if os.path.isfile(MODELPATH+'model.pth') and len(os.listdir(GAMEPATH))==0:
            checkpoint = torch.load(MODELPATH+'model.pth',map_location=torch.device(device))
            model.load_state_dict(checkpoint['model_state_dict'])
            mcts_num=checkpoint['MCTSNUM']

            game_gen_end=False
            while True:
                print('\r 게임수: '+str(len(os.listdir(GAMEPATH)))+'/'+str(mcts_num),end='')
                cnt=0
                if len(os.listdir(GAMEPATH))<mcts_num:
                    for pn in range(process_num):
                        p = Process(target=board.game_loop, args=(GAMEPATH+MACINE_NAME+"_game"+str(process_num*cnt+pn)+'.json',model,True))
                        p.daemon = True
                        p_list.append(p)
                        p_list[-1].start()
                    
                    
                    while True:
                        ck=True
                        print('\r 게임수: '+str(len(os.listdir(GAMEPATH)))+'/'+str(mcts_num),end='')
                        time.sleep(1)
                        if not os.path.isfile(MODELPATH+'model.pth') or len(os.listdir(GAMEPATH))>=mcts_num:
                            game_gen_end=True
                            break
                        for pp in p_list:
                            if pp.is_alive():
                                ck=False
                                break
                        if ck:
                            break
                    for pp in p_list:
                        pp.kill()
                    cnt+=1
                if game_gen_end:
                    break
        else:
            cnt=0
            print('\r 대기중                                         ',end='')
            time.sleep(1)
        
        # for mn in range(mcts_num):
        #     p_list =[]
        #     for pn in range(mn*process_num,(mn+1)*process_num):
        #         p = Process(target=board.game_loop, args=(path+MACINE_NAME+"_game"+str(pn)+'.json',model,))
        #         p.daemon = True
        #         p_list.append(p)
        #         p_list[-1].start()
        #     for pp in p_list:
        #         pp.join()


