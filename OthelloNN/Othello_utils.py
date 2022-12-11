#오델로 관련함수들

import copy

def str2state(str_staet):
    state = []
    for i in range(8):
        temp_list = []
        for j in range(8):
            if str_staet[i*8+j] == 'e':
                temp_list.append(0)
            elif str_staet[i*8+j] == 'w':
                temp_list.append(-1)
            elif str_staet[i*8+j] == 'b':
                temp_list.append(1)
        state.append(temp_list)
    return state
def state2str(state):
    str_state = ''
    for i in range(8):
        for j in range(8):
            if state[i][j] == 0:
                str_state += 'e'
            elif state[i][j] == -1:
                str_state += 'w'
            elif state[i][j] == 1:
                str_state += 'b'
    return str_state           

# 8 x 8 짜리 배열을 받아 오델로 판을 출력해주는 함수
def show_state(state):
    output = "ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ\n"
    for i in range(len(state)):
        output += '|'
        for j in range(len(state[i])):
            if state[i][j] == -1:
                output += " ○ "
            elif state[i][j] == 1:
                output += " ● "
            elif state[i][j] == 0:
                output += "   "
            output+='|'
        output += "\nㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ\n"
    print(output)
def show_chosen(state,x,y):
    output = "ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ\n"
    for i in range(len(state)):
        output += '|'
        for j in range(len(state[i])):
            if i == x and j == y:
                output += " X "
            elif state[i][j] == -1:
                output += " ○ "
            elif state[i][j] == 1:
                output += " ● "
            elif state[i][j] == 0:
                output += "   "
            output+='|'
        output += "\nㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ\n"
    print(output)
def show_chosens(state,list_able):
    output = "ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ\n"
    for i in range(len(state)):
        output += '|'
        for j in range(len(state[i])):
            if [i,j] in list_able:
                output += " X "
            elif state[i][j] == -1:
                output += " ○ "
            elif state[i][j] == 1:
                output += " ● "
            elif state[i][j] == 0:
                output += "   "
            output+='|'
        output += "\nㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ\n"
    print(output)

# x,y 자리에 놓았을때 바뀌는 자리를 반환 / 잘못된 x,y를 입력할경우 False 와 None을 반환
def check_set(state,x,y,turn):
    last = turn
    changes=[[x,y]]
    temp_list = []
    result  = False
    if state[x][y] != 0:
        return False, None
    
    #가로 검사
    for i in range(x+1,8):
        # show_chosen(state,i,y)
        # print(i,y)
        if state[i][y] == turn*(-1):
            last = turn*(-1)
            temp_list.append([i,y])
            continue
        elif state[i][y] == turn:
            if last == turn:
                break
            else:
                changes.extend(temp_list)
                result  = True
                break
        elif state[i][y] == 0:
            break
    
    last = turn
    temp_list = []
    for i in range(x-1,-1,-1):
        # show_chosen(state,i,y)
        # print(i,y)
        if state[i][y] == turn*(-1):
            last = turn*(-1)
            temp_list.append([i,y])
            continue
        elif state[i][y] == turn:
            if last == turn:
                break
            else:
                changes.extend(temp_list)
                result  = True
                break
        elif state[i][y] == 0:
            break
    
    last = turn
    temp_list = []

    #세로 검사
    for i in range(y+1,8):
        # show_chosen(state,i,y)
        # print(x,i)
        if state[x][i] == turn*(-1):
            last = turn*(-1)
            temp_list.append([x,i])
            continue
        elif state[x][i] == turn:
            if last == turn:
                break
            else:
                changes.extend(temp_list)
                result  = True
                break
        elif state[x][i] == 0:
            break
    last = turn
    temp_list = []

    for i in range(y-1,-1,-1):
        # show_chosen(state,i,y)
        # print(x,i)
        if state[x][i] == turn*(-1):
            last = turn*(-1)
            temp_list.append([x,i])
            continue
        elif state[x][i] == turn:
            if last == turn:
                break
            else:
                changes.extend(temp_list)
                result  = True
                break
        elif state[x][i] == 0:
            break
    last = turn
    temp_list = []

    #대각 검사
    k,l=x,y 
    if x<y:
        k=x 
        l=y
    else:
        k=y 
        l=x
    # 오른쪽 아래
    i=0
    while True:
        i+=1
        # show_chosen(state,i,y)
        # print(x+i,y+i)
        if x+i > 7 or y+i > 7:
            break
        if state[x+i][y+i] == turn*(-1):
            last = turn*(-1)
            temp_list.append([x+i,y+i])
            continue
        elif state[x+i][y+i] == turn:
            if last == turn:
                break
            else:
                changes.extend(temp_list)
                result  = True
                break
        elif state[x+i][y+i] == 0:
            break
    last = turn
    temp_list = []

    # 왼쪽 위
    i=0
    while True:
        i+=1
        # show_chosen(state,i,y)
        # print(x-i,y-i)
        if x-i < 0 or y-i < 0:
            break
        if state[x-i][y-i] == turn*(-1):
            last = turn*(-1)
            temp_list.append([x-i,y-i])
            continue
        elif state[x-i][y-i] == turn:
            if last == turn:
                break
            else:
                changes.extend(temp_list)
                result  = True
                break
        elif state[x-i][y-i] == 0:
            break
    last = turn
    temp_list = []

    # 왼쪽 아래
    i=0
    while True:
        i+=1
        # show_chosen(state,i,y)
        # print(x+i,y-i)
        if x+i > 7 or y-i < 0:
            break
        if state[x+i][y-i] == turn*(-1):
            last = turn*(-1)
            temp_list.append([x+i,y-i])
            continue
        elif state[x+i][y-i] == turn:
            if last == turn:
                break
            else:
                changes.extend(temp_list)
                result  = True
                break
        elif state[x+i][y-i] == 0:
            break
    last = turn
    temp_list = []

    # 오른쪽 위
    i=0
    while True:
        i+=1
        # show_chosen(state,i,y)
        # print(x-i,y+i)
        if x-i < 0 or y+i > 7:
            break
        if state[x-i][y+i] == turn*(-1):
            last = turn*(-1)
            temp_list.append([x-i,y+i])
            continue
        elif state[x-i][y+i] == turn:
            if last == turn:
                break
            else:
                changes.extend(temp_list)
                result  = True
                break
        elif state[x-i][y+i] == 0:
            break
    
    if result:
        temp_state = copy.deepcopy(state)
        for change in changes:
            temp_state[change[0]][change[1]] = turn
        # show_state(temp_state)
        return True, temp_state
    else:
        return False, None

# 놓을 수 있는 곳을 찾는 함수
def check_able(state,turn):
    temp_ck = False
    temp_list = []
    for i in range(8):
        for j in range(8):
            if state[i][j] == 0:
                temp_rs, _  = check_set(state,i,j,turn)
                if temp_rs:
                    temp_ck=True
                    temp_list.append([i,j])
    # show_chosens(state,temp_list)
    return temp_ck, temp_list