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
optimizer = optim.Adam(model.parameters(), lr=0.01)
epoch=0
if os.path.isfile('model.pth'):
    print('load model')
    checkpoint = torch.load('model.pth')
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    epoch = checkpoint['epoch']
    loss = checkpoint['loss']
else:
  with open("loss.txt","w",encoding='utf-8') as ef:
    ef.write("")

criterion = utils.AlphaLoss()

# scheduler = optim.lr_scheduler.LambdaLR(optimizer=optimizer,
#                                         lr_lambda=lambda epoch: 0.95 ** epoch)
scheduler = optim.lr_scheduler.StepLR(optimizer,step_size = 50, gamma = 0.01)

iter = 10000
batch=64
save_term = 1
data_num=65536

#샘플 데이터 가져오기
f= open('spr_list.json', 'r', encoding='utf-8')
raw_datas = json.load(f)
f.close()

class TensorData(Dataset):
    def __init__(self, states_data, p_data, v_data):
        #들어온 x는 tensor형태로 변환
        self.states_data = torch.FloatTensor(states_data).to(device)
        self.p_data = torch.FloatTensor(p_data).to(device)
        self.v_data = torch.FloatTensor(v_data).to(device)
        self.len = self.v_data.shape[0]
    def __getitem__(self, index):
        return self.states_data[index], self.p_data[index], self.v_data[index]

    def __len__(self):
        return self.len
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
progress.update(epoch)
for iter in range((epoch),iter):
    model.train()
    for batch_step, data in enumerate(train_loader):
        
        avg_loss = 0
        cnt=0
        for i in range(len(data)):
            pi, v = model(data[0][i])
            loss = criterion(data[2][i],v, data[1][i], pi)
            loss.backward()
            avg_loss+=loss.item()
            cnt+=1
        optimizer.step()
        optimizer.zero_grad()
        progress.set_description('%d/%d | loss: %.3f' % (batch_step,data_num//batch, avg_loss/cnt))
    scheduler.step()
    progress.update(1)
    if iter%save_term==0:
        torch.save({
            'epoch': iter+1,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': loss,
            
            }, 'model.pth')
    
progress.close()
torch.save(model.state_dict(), 'model.pth')