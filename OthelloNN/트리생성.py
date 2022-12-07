import json
import tqdm
import Othello_utils

f=open('기보데이터/raw_data.txt','r')
raw_datas = f.read().split('\n')
f.close()
datas={}

progress = tqdm.tqdm(total=len(raw_datas))

for data in raw_datas:
    data = list(map(''.join, zip(*[iter(data)]*2)))
    
    state = [
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,-1,1,0,0,0],
            [0,0,0,1,-1,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            ]
    turn = 1
    temp_datas = []
    name=''
    for step in data:
        x,y=ord(step[0])-ord('a'),int(step[1])-1
        
        str_state = Othello_utils.state2str(state)
        temp_datas.append({'name':name,'state':str_state,'next_name':name+step,'x':x,'y':y, 'turn':turn})

        _,state=Othello_utils.check_set(state,x,y,turn)
        res,_=Othello_utils.check_able(state,turn*(-1))
        if res:
            turn *= -1
        # Othello_utils.show_state(state)
        name+=step
    str_state = Othello_utils.state2str(state)
    # print(temp_datas)
    game_result = 0
    if str_state.count('b') > str_state.count('w'):
        game_result = 1
    elif str_state.count('b') < str_state.count('w'):
        game_result = -1
    else:
        game_result = 0

    for i,temp_data in enumerate(temp_datas):
        if temp_data['name'] not in datas.keys():
            datas[temp_data['name']] = {'state':temp_data['state'],'value':[game_result*temp_data['turn'],1], 'actions': [{'name':temp_data['next_name'],'x':temp_data['x'],'y':temp_data['y'],'turn':temp_data['turn'],'count':1}]}
        else:
            datas[temp_data['name']]['value'][0] += game_result*temp_data['turn']
            datas[temp_data['name']]['value'][1] += 1
            temp_ck=True
            for j,action in enumerate(datas[temp_data['name']]['actions']):
                if action['name'] == temp_data['next_name']:
                    datas[temp_data['name']]['actions'][j]['count'] += 1
                    temp_ck=False
                    break
            if temp_ck:
                datas[temp_data['name']]['actions'].append({'name':temp_data['next_name'],'x':temp_data['x'],'y':temp_data['y'],'turn':temp_data['turn'],'count':1})
    progress.update(1)
progress.close()
with open('tree_datas.json', 'w', encoding='utf-8') as make_file:
    json.dump(dict(sorted(datas.items(), key=lambda x: len(x[0]))), make_file, ensure_ascii=False, indent="\t")
