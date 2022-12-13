import json
import os

with open('games/game0.json', 'r') as f:
    data = json.load(f)
    total_reward = 0
    for i in data:
        print(i)
        actions = i['actions']
        count = 0
        for j in actions:
            count += j['count']
        if count != 0:
            total_reward += i['reward'] / count
        # else:
        #     total_reward += -1
    print(total_reward)