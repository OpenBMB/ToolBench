import json
import argparse
import os
from tqdm import tqdm

# 创建参数解析器并添加参数
parser = argparse.ArgumentParser()
parser.add_argument('query_file', help='The name of the query file')
parser.add_argument('index_file', help='The name of the index file')

# 解析命令行参数
args = parser.parse_args()

# 读取query文件
with open(args.query_file, 'r') as f:
    query_data = json.load(f)

# 读取index文件
with open(args.index_file, 'r') as f:
    test_index_data = json.load(f)

# 通过集合操作，创建测试集index的集合
test_index_set = set(map(int, test_index_data.keys()))

# 初始化训练集和测试集的列表
query_train = []
query_test = []

# 根据index，将query_data的数据分配到训练集和测试集
for index, item in tqdm(enumerate(query_data)):
    if index in test_index_set:
        query_test.append(item)
    else:
        query_train.append(item)

# 创建输出文件的名字
output_file_base = os.path.splitext(args.query_file)[0]
train_file = output_file_base + '_train.json'
test_file = output_file_base + '_test.json'

# 将训练集和测试集写入到对应的json文件中
with open(train_file, 'w') as f:
    json.dump(query_train, f)

with open(test_file, 'w') as f:
    json.dump(query_test, f)