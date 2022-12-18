import math
import time
import copy
import torch
import numpy as np
from OthelloNN import OthelloNNet
from OthelloNN import Othello_utils
	

class GameAI(object):
	def __init__(self, game,model_path):
		super().__init__()
		self.game = game
		self.move = (-1,-1)
		self.timeLimit = 3  # 3 seconds is the time limit for search
		self.debug = False  # True for debugging
		model = OthelloNNet.ConnectNet()
		self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
		if model_path is not None:
			checkpoint = torch.load('model.pth', map_location=self.device)
			model.load_state_dict(checkpoint['model_state_dict'])
		self.model = model
		self.model.to(self.device)
		self.model.eval()

	# AI perform move (there must be an available move due to the pre-move check)
	def performMove(self,history):
		# Iterative Deepening MiniMax Search with Alpha-Beta Pruning
		# tmpBoard = [ [0 for _ in range(8)] for _ in range(8)] # we don't want to make changes to the game board
		now_turn = 1 if history[-1]['turn']==1 else -1
		now_state = history[-1]['state']
		for i in range(8):
			for j in range(8):
				if now_state[i][j]==2:
					now_state[i][j]=-1
		b=[]
		w=[]

		for state in history[::-1]:
			if state['turn'] ==1:
				b.append(state['state'])
				for i in range(8):
					for j in range(8):
						if state['state'][i][j]==2:
							b[-1][i][j]=-1
			elif state['turn'] ==2:
				w.append(state['state'])
				for i in range(8):
					for j in range(8):
						if state['state'][i][j]==2:
							w[-1][i][j]=-1
			if len(b)>8 and len(w)>8:
				break
		
		input = [[[0 for _ in range(8)] for _ in range(8)] for _ in range(16)]
		for i, bs in enumerate(b[:8]):
			input[i] = bs
		for i, ws in enumerate(w[:8]):
			input[i+8] = ws
		input.append([[ now_turn for _ in range(8)] for _ in range(8)])
		
		input = torch.tensor(input).float().to(self.device)
		pi,v=self.model(input)
		_, able_list=Othello_utils.check_able(now_state,now_turn)
		able_p_list=[]
		for action in able_list:
			able_p_list.append(pi[0][action[0]*8+action[1]].item())
		
		able_p_list = np.array(able_p_list)
		able_p_list = able_p_list/np.sum(able_p_list)
		
		self.move = able_list[np.random.choice(len(able_list),p=able_p_list)]
		
		print(able_list)
		print(able_p_list)
		print(self.move)
		# perform move (there must be an available move)
		self.game.performMove(self.move[0], self.move[1])

if __name__ == '__main__':
	if __package__ is None:
		import sys
		from os import path
		print(path.dirname( path.dirname( path.abspath(__file__) ) ))
		sys.path.append(path.dirname( path.dirname( path.abspath(__file__) ) ))
		from OthelloNN import OthelloNNet
		from OthelloNN import Othello_utils
	else:
		from ..OthelloNN import OthelloNNet
		from ..OthelloNN import Othello_utils
	
	# board=[
	# 	[0,0,0,0,0,0,0,0],
	# 	[0,0,0,0,0,0,0,0],
	# 	[0,0,0,0,0,0,0,0],
	# 	[0,0,0,1,-1,0,0,0],
	# 	[0,0,0,-1,1,0,0,0],
	# 	[0,0,0,0,0,0,0,0],
	# 	[0,0,0,0,0,0,0,0],
	# 	[0,0,0,0,0,0,0,0],]

	# Othello_utils.show_state(board)
	# Othello_utils.show_chosen(board,4,2)
