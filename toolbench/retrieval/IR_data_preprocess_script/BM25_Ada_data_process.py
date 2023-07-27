import json
import argparse
from tqdm import tqdm

# 创建参数解析器，并添加输入文件和输出文件的参数
parser = argparse.ArgumentParser()
parser.add_argument("--train_query_files", nargs='+', help="The filenames of the train query files.")
parser.add_argument("--test_query_files", nargs='+', help="The filenames of the test query files.")
parser.add_argument("--output_doc_file", help="The filename of the output documents file.")
parser.add_argument("--output_query_file", help="The filename of the output query file.")
args = parser.parse_args()

documents = []
document_to_id = {}  # 用于记录文档内容到ID的映射，避免重复的文档
query_list = []

# 把 train_queries 和 test_queries 中的 api_list 转换为字符串，存储到 documents 中
doc_id = 0
for train_query_file, test_query_file in zip(args.train_query_files, args.test_query_files):
    with open(train_query_file, 'r') as file:
        train_queries = json.load(file)

    with open(test_query_file, 'r') as file:
        test_queries = json.load(file)

    for query_dict in [train_queries, test_queries]:
        for query in tqdm(query_dict):
            query_doc_ids = []
            for api in query['api_list']:
                # 把每个 api 的各个属性连接成一个字符串
                document = json.dumps(api)
                # 如果这个文档之前没出现过，添加到documents，否则直接使用之前的id
                if document not in document_to_id:
                    documents.append({'id': doc_id, 'text': document})
                    document_to_id[document] = doc_id
                    doc_id += 1
                query_doc_ids.append(document_to_id[document])

            # 如果当前query是测试query，把它的query和对应文档的id保存到query.json中
            if query_dict is test_queries:
                query_content = {
                    'query': query['query'],
                    'docs': query_doc_ids
                }
                query_list.append(query_content)

# 将处理后的数据保存到指定的输出文件中
with open(args.output_doc_file, 'w') as file:
    json.dump(documents, file)

with open(args.output_query_file, 'w') as file:
    json.dump(query_list, file)