import json
import random
import time
import torch
import numpy as np
import os
import tqdm
from multiprocessing import Process, Pool, freeze_support

from OthelloMCTS import game
from OthelloNN import OthelloNNet
from OthelloNN import utils
from OthelloMCTS.game import Board

BLACK = 1
WHITE = -1
EMPTY = 0
STONE = {BLACK: '●', WHITE: '○', EMPTY: '.'}
GAMEPATH = "H:/내 드라이브/OSSP2/games/"
MODELPATH = "H:/내 드라이브/OSSP2/model/"
MCTSNUM=10
MACINE_NAME='Main'
torch.autograd.set_detect_anomaly(True)


if __name__ == '__main__':
    freeze_support()

    epochs=300
    batch_count=16

    process_num=10

    total_game=400

    for file in os.listdir(GAMEPATH):
        os.remove(GAMEPATH+file)
    for file in os.listdir(MODELPATH):
        os.remove(MODELPATH+file)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = OthelloNNet.ConnectNet().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    if os.path.isfile('model.pth'):
        checkpoint = torch.load('model.pth')
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    else:
        torch.save({
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        }, 'model.pth')
    
    
    for file in os.listdir(MODELPATH):
        os.remove(MODELPATH+file)

    # time.sleep(30)
    for g in range(10000):
        data_set = []
        print(str(g)+':번째 반복 || MCTS 게임:' + str(total_game) + '번')
        
        #mcts로 데이터생성
        board = Board(turn=BLACK)
        # one_game=board.game_loop()
        
        # progress_bar = tqdm.tqdm(total=mcts_num*process_num)
        # progress_bar.set_description('MCTS데이터 생성중')
        # for mn in range(mcts_num):
        #     p_list =[]
        #     for pn in range(mn*process_num,(mn+1)*process_num):
        #         p = Process(target=board.game_loop, args=(pn,model,))
        #         p.daemon = True
        #         p_list.append(p)
        #         p_list[-1].start()
        #     for pp in p_list:
        #         pp.join()
        #     progress_bar.update(process_num)
        # progress_bar.close()

        #폴더내 모든 파일 삭제
        for file in os.listdir(GAMEPATH):
            os.remove(GAMEPATH+file)
        for file in os.listdir(MODELPATH):
            os.remove(MODELPATH+file)
        
        
        model_name = MODELPATH+'model.pth'
        
        torch.save({
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'MCTSNUM':MCTSNUM,
        }, model_name)

        print('MCTS데이터 생성중')
        cnt=0
        start = time.time()
        while True:
            if len(os.listdir(GAMEPATH))>=MCTSNUM:
                break
            print('\r 게임수: '+str(len(os.listdir(GAMEPATH)))+'/'+str(MCTSNUM)+' || 소요시간:'+str(round(time.time()-start,3)),end='')
            # time.sleep(1)
            p_list=[]
            for pn in range(process_num):
                p = Process(target=board.game_loop, args=(GAMEPATH+MACINE_NAME+"_game"+str(process_num*cnt+pn)+'.json',model,True,))
                p.daemon = True
                p_list.append(p)
                p_list[-1].start()
            while True:
                print('\r 게임수: '+str(len(os.listdir(GAMEPATH)))+'/'+str(MCTSNUM)+' || 소요시간:'+str(round(time.time()-start,3)),end='')
                time.sleep(1)
                if len(os.listdir(GAMEPATH))>=MCTSNUM:
                    break
                ck=True
                for pp in p_list:
                    if pp.is_alive():
                        ck=False
                        break
                if ck:
                    for pp in p_list:
                        pp.join()
                    break
            for pp in p_list:
                pp.kill()
            cnt+=1
        print('\r 게임수: '+str(len(os.listdir(GAMEPATH)))+'/'+str(MCTSNUM)+' || 소요시간:'+str(round(time.time()-start,3)),end='')
        
        for file in os.listdir(MODELPATH):
            os.remove(MODELPATH+file)
        






        progress_bar = tqdm.tqdm(total=len(os.listdir(GAMEPATH)))
        progress_bar.set_description('MCTS데이터 변환중')
        for file in os.listdir(GAMEPATH):
            total_game+=1
            f=open(GAMEPATH+file,'r')
            one_game=json.load(f)
            f.close()
            bs = [[[0 for _ in range(8)] for _ in range(8)] for _ in range(8)]
            ws = [[[0 for _ in range(8)] for _ in range(8)] for _ in range(8)]
            for state in one_game:
                if state['turn'] == BLACK:
                    bs.append(state['state'])
                    bs.pop(0)
                else:
                    ws.append(state['state'])
                    ws.pop(0)
                input =[]
                input.extend(bs[::-1])
                input.extend(ws[::-1])
                input.extend([[[0 for _ in range(8)] for _ in range(8)]])

                pi = np.zeros(64)
                v=state['reward']
                for action in state['actions']:
                    x,y=action['action'] = action['action'].split(',')
                    pi[int(x)*8+int(y)] = action['count']
                if np.sum(pi) != 0:
                    v=v/np.sum(pi)
                    pi=pi/np.sum(pi)
                pi=pi.tolist()

                # print(input)
                # print(pi)
                # print(v)
                data_set.append([[input],pi,v])
            progress_bar.update(1)        
        progress_bar.close()
        print('샘플수: ',len(data_set))
        model.train()
        print('학습시작')


        
        progress_bar = tqdm.tqdm(total=epochs)
        for epoch in range(epochs):
            random.shuffle(data_set)
            states = torch.tensor([n[0] for n in data_set],dtype=torch.float32).to(device)
            pi_y = torch.tensor([n[1] for n in data_set],dtype=torch.float32).to(device)
            v_y = torch.tensor([[n[2]] for n in data_set],dtype=torch.float32).to(device)
            # print(states.shape)
            for batch in range(len(data_set)//batch_count):
                optimizer.zero_grad()
                pi,v = model(states[batch_count*batch:batch_count*(batch+1)])
                loss = (((v-v_y[batch_count*batch:batch_count*(batch+1)])**2).view(-1)+torch.sum((-pi* (1e-8 + pi_y[batch_count*batch:batch_count*(batch+1)].float()).float().log()), 1)).mean()

                loss.backward()
                optimizer.step()
                # break
            
                # print('epoch: {}, batch: {}, loss: {}'.format(epoch,batch,loss.item()))
                progress_bar.set_description('batch: {}, loss: {}'.format(batch,loss.item()))
            optimizer.zero_grad()
            try:
                torch.save({
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict()
                }, 'model.pth')
            except:
                pass
            progress_bar.update(1)
        progress_bar.close()

