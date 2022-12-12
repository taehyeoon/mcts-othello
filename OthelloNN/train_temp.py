# train the model

import random
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
import json
import tqdm
import os

import OthelloNNet
import Othello_utils
import utils


# 기본 설정
device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')
print(device)

model = OthelloNNet.ConnectNet().to(device)
if os.path.isfile('model.pth') and False:
    print('load model')
    model.load_state_dict(torch.load('model.pth'))
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

criterion = utils.AlphaLoss()

iter = 1000
batch=1000
save_term = 50
data_num=100000

#샘플 데이터 가져오기
f= open('spr_list.json', 'r', encoding='utf-8')
raw_datas = json.load(f)
f.close()

class TensorData(Dataset):
    # 외부에 있는 데이터를 가져오기 위해 외부에서 데이터가 들어올 수 있도록, x_data, y_data 변수를 지정
    def __init__(self, states_data, p_data, v_data):
        #들어온 x는 tensor형태로 변환
        self.states_data = torch.FloatTensor(states_data)
        # tensor data의 형태는 (배치사이즈, 채널사이즈, 이미지 너비, 높이)의 형태임
        # 따라서 들어온 데이터의 형식을 permute함수를 활용하여 바꾸어주어야함.
        self.p_data = torch.FloatTensor(p_data)
        self.v_data = torch.FloatTensor(v_data)
        self.len = self.v_data.shape[0]

    # x,y를 튜플형태로 바깥으로 내보내기
    def __getitem__(self, index):
        return self.states_data[index], self.p_data[index], self.v_data[index]

    def __len__(self):
        return self.len

# states=np.empty((0,17,8,8),dtype=np.float32)
# pi=np.empty((0,64),dtype=np.float32)
# v=np.array([],dtype=np.float32)
states=[]
pi=[]
v=[]
print("Loading data")
data_list =raw_datas["sqrList"]
random.shuffle(data_list)
progress = tqdm.tqdm(total=len(data_list[:data_num]))

for data in data_list[:data_num]:

    # states=np.append(states,[np.array(data[0].split(',')).reshape(17,8,8).astype(np.float32)],axis=0)
    # pi=np.append(pi,[np.array(data[1].split(',')).astype(np.float32)],axis=0)
    # v=np.append(v,data[2])
    states.append(np.array(data[0].split(',')).reshape(17,8,8).astype(np.float32).tolist())
    pi.append(np.array(data[1].split(',')).astype(np.float32).tolist())
    v.append(data[2])
    progress.update(1)
    
progress.close()
train_data = TensorData(states, pi, v)

train_loader = DataLoader(train_data, batch_size=batch, shuffle=True)
progress = tqdm.tqdm(total=iter)
for iter in range(iter):
    #상태 기본 설정

    #MCTS 트리생성

    #(s,p,r) 생성

    #학습 데이터 생성
    
    
    #시작
    avg_loss = 0
    for batch_step, data in enumerate(train_loader):
        for i in range(len(data)):
            # print(data[1].shape)
            # print(data[1])
            # print(data[2].shape)
            # print(data[2])
            # print(data[0].shape)
            # print(data[1].shape)
            # print(data[2].shape)
            # break
            optimizer.zero_grad()
            # print(data[0].shape)
            # print(data[1].shape)
            # print(data[2].shape)
            # break
            pi, v = model(data[0][i].to(device))
            # print(pi.shape)
            # print(data[1].shape)
            # print(v.shape)
            # print(data[2].shape)
            # break
            loss = criterion(v, data[2][i].to(device), pi, data[1][i].to(device))
            loss.backward()
            avg_loss += loss.item()
            optimizer.step()
    avg_loss /= len(data)
    progress.set_description('%d | loss: %.3f' % (batch_step, loss.item()))
    progress.update(1)
    if iter%save_term==0:
        torch.save(model.state_dict(), 'model.pth')
    
progress.close()
torch.save(model.state_dict(), 'model.pth')







