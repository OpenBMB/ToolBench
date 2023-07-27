import json

# 需要合并的文件名
train_files = ['queryG1_train.json', 'queryG2_train.json', 'queryG3_train.json']
test_files = ['queryG1_test.json', 'queryG2_test.json', 'queryG3_test.json']

# 初始化空列表来保存所有的训练集和测试集数据
all_train = []
all_test = []

# 读取并合并训练集数据
for file in train_files:
    with open(file, 'r') as f:
        data = json.load(f)
        all_train.extend(data)

# 读取并合并测试集数据
for file in test_files:
    with open(file, 'r') as f:
        data = json.load(f)
        all_test.extend(data)

# 将合并后的数据写入到新的json文件中
with open('query_all_train.json', 'w') as f:
    json.dump(all_train, f)

with open('query_all_test.json', 'w') as f:
    json.dump(all_test, f)