from flask import Flask, Response, stream_with_context, request
from flask_cors import CORS, cross_origin
from callbacks.ServerEventCallback import ServerEventCallback
import argparse
from toolbench.inference.Downstream_tasks.rapidapi import pipeline_runner
import subprocess
import concurrent.futures
import json
import signal
import time
from queue import Queue
import copy
import time
app = Flask(__name__)
cors = CORS(app)


class Model:
    def __init__(self, gpu=0):
        self.inuse = False
        print("Initializing...")
        starting_time = time.time()
        self.args = self.get_args()
        self.pipeline = pipeline_runner(self.args, add_retrieval=False, server=True)
        print("Loading model...")
        self.llm = self.pipeline.get_backbone_model()
        print("Model loaded in {} seconds".format(time.time() - starting_time))
        starting_time = time.time()
        print("Loading retriever...")
        self.retriever = self.pipeline.get_retriever()
        print("Retriever loaded in {} seconds".format(time.time() - starting_time))
        self.query_id = 0
        # self.process_num = self.args.process_num

        self.queue = Queue()
        self.callback = ServerEventCallback(self.queue)
        self.occupied = False

        print("Server ready")

    def run_pipeline(self, user_input, method, top_k):
        # empty the queue
        while not self.queue.empty():
            self.queue.get()
        self.query_id += 1
        temp_args = copy.deepcopy(self.args)
        temp_args.retrieved_api_nums = top_k
        temp_args.method = method
        data_dict = {
            "query": user_input,
        }
        self.pipeline.run_single_task(
            method=method,
            backbone_model=self.llm,
            query_id=self.query_id,
            data_dict=data_dict,
            output_dir_path=self.args.output_answer_file,
            retriever=self.retriever,
            args=temp_args,
            tool_des=None,
            callbacks=[self.callback]
        )

    def get_queue(self):
        while not self.queue.empty():
            yield self.queue.get()

    def get_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--corpus_tsv_path', type=str, default="your_retrival_corpus_path/", required=False,
                            help='')
        parser.add_argument('--retrieval_model_path', type=str, default="your_model_path/", required=False, help='')
        parser.add_argument('--retrieved_api_nums', type=int, default=5, required=False, help='')
        parser.add_argument('--backbone_model', type=str, default="toolllama", required=False,
                            help='chatgpt_function or davinci or toolllama')
        parser.add_argument('--openai_key', type=str, default="", required=False,
                            help='openai key for chatgpt_function or davinci model')
        parser.add_argument('--model_path', type=str, default="your_model_path/", required=True, help='')
        parser.add_argument('--tool_root_dir', type=str, default="your_tools_path/", required=True, help='')
        parser.add_argument("--lora", action="store_true", help="Load lora model or not.")
        parser.add_argument('--lora_path', type=str, default="your_lora_path if lora", required=False, help='')
        parser.add_argument('--max_observation_length', type=int, default=1024, required=False,
                            help='maximum observation length')
        parser.add_argument('--observ_compress_method', type=str, default="truncate", choices=["truncate", "filter", "random"], 
                            required=False, help='observation compress method')
        parser.add_argument('--method', type=str, default="CoT@1", required=False,
                            help='method for answer generation: CoT@n,Reflexion@n,BFS,DFS,UCT_vote')
        parser.add_argument('--input_query_file', type=str, default="", required=False, help='input path')
        parser.add_argument('--output_answer_file', type=str, default="", required=False, help='output path')
        parser.add_argument('--toolbench_key', type=str, default="", required=False, help='your toolbench key')
        parser.add_argument('--rapidapi_key', type=str, default="",required=False, help='your rapidapi key to request rapidapi service')
        parser.add_argument('--use_rapidapi_key', action="store_true", help="To use customized rapidapi service or not.")
        parser.add_argument('--api_customization', action="store_true", help="To use customized api or not.")

        args = parser.parse_args()
        return args

model = Model()


@app.route('/stream', methods=['GET', 'POST'])
@cross_origin()
def stream():
    data = json.loads(request.data)
    user_input = data["text"]
    top_k = data["top_k"]
    method = data["method"]
    print("Called stream")
    global model

    def generate(model):
        print("Called generate")
        if model.inuse:
            # send 409 error
            return Response(json.dumps({
                "method_name": "error",
                "error": "Model in use"
            }), status=409, mimetype='application/json')
            return
        model.inuse = True

        # run model.run_agent in the background
        with concurrent.futures.ThreadPoolExecutor() as executor:

            future = executor.submit(model.run_pipeline, user_input, method, top_k)
            # keep waiting for the queue to be empty
            while True:
                if model.queue.empty():
                    if future.done():
                        print("Finished with future")
                        break
                    time.sleep(0.01)
                    continue
                else:
                    obj = model.queue.get()
                if obj["method_name"] == "unknown": continue
                if obj["method_name"] == "on_request_end":
                    yield json.dumps(obj)
                    break

                try:
                    yield json.dumps(obj) + "\n"
                except Exception as e:
                    model.inuse = False
                    print(obj)
                    print(e)

            try:
                future.result()
            except Exception as e:
                model.inuse = False
                print(e)

        model.inuse = False
        return

    return Response(stream_with_context(generate(model)))

@app.route('/methods', methods=['GET'])
@cross_origin()
def methods():
    # return a list of available methods
    return Response(json.dumps({
        {
            "methods": ["DFS_woFilter_w2"]
        }
    }), status=200, mimetype='application/json')

def handle_keyboard_interrupt(signal, frame):
    global model
    exit(0)

signal.signal(signal.SIGINT, handle_keyboard_interrupt)

if __name__ == '__main__':
    app.run(use_reloader=False, host="0.0.0.0", debug=True, port=5000)
