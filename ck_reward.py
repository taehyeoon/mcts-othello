import json
import os

avg_reward = 0
folder_name= "sample27"
# folder_name= "games"
for fn, file in enumerate(os.listdir(folder_name)):
    with open(folder_name+'/'+file, 'r') as f:
        data = json.load(f)
        total_reward = 0
        for i in data:
            # print(i)
            actions = i['actions']
            count = 0
            for j in actions:
                count += j['count']
            if count != 0:
                total_reward += i['reward'] / count
            # else:
            #     total_reward += -1
    avg_reward+= total_reward
print(avg_reward/fn)
# a=[7.890000000000001,
# 5.1,
# 5.635000000000001,
# 4.195,
# 5.904999999999999,
# 5.059999999999999,
# 4.89,
# 6.204999999999999,
# 6.185,
# 4.965000000000001,
# 4.475,
# 5.474999999999999,
# 5.359999999999999]
# print(sum(a)/len(a))