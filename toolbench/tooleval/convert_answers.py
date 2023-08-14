from convert_to_answer_format import process_invalid_data,process_valid_data
import json
from glob import glob
import os

save_dir = 'path/to/save/dir'

groups_dirs = ['path/to/dataset/eval/result/folders']

for groups_dir in groups_dirs:
    method = os.path.split(groups_dir)[1]
    print(method)
    groups_save_dir = os.path.join(save_dir,method)
    os.makedirs(groups_save_dir,exist_ok=True)
    groups = [os.path.split(g)[1] for g in glob(groups_dir+'/*')]
    full_answer = {}
    for g in groups:
        print(g)
        answer_dict = {}
        files = glob(os.path.join(groups_dir,g,'*.json'))
        for file in files:
            qid = os.path.split(file)[1].split('_')[0]
            try:
                data = json.load(open(file))
            except:
                print('Read error: ',file)
                continue
            if not data['answer_generation']['valid_data']:
                answer_dict[qid] = process_invalid_data(method,data)
            else:
                answer_dict[qid] = process_valid_data(method,data['answer_generation'])
        json.dump(answer_dict,open(os.path.join(groups_save_dir,f'{g}.json'),'w'))
        full_answer.update(answer_dict)
    # json.dump(full_answer,open(os.path.join(groups_save_dir,f'fullanswer.json'),'w'))