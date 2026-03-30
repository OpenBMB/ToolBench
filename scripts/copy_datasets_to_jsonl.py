import json
import os
import argparse

def process_datasets(input_dir, output_file):
    print(f"Reading dataset files from {input_dir}")
    print(f"Writing parsed jsonl output to {output_file}")

    with open(output_file, 'w', encoding='utf-8') as outfile:
        # We will loop through directories G1_answer, G2_answer, G3_answer if available
        # or process exactly the directory passed
        if not os.path.exists(input_dir):
            print(f"Error: {input_dir} does not exist.")
            return

        total_lines_written = 0
        for root, dirs, files in os.walk(input_dir):
            for filename in files:
                if filename.endswith(".json"):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as infile:
                            data = json.load(infile)

                        if "answer_generation" in data:
                            answer_gen = data["answer_generation"]
                            if "train_messages" in answer_gen and answer_gen.get("valid_data", False):
                                # Extract useful training info
                                record = {
                                    "query": answer_gen.get("query", ""),
                                    "functions": answer_gen.get("function", []),
                                    "train_messages": answer_gen["train_messages"]
                                }
                                outfile.write(json.dumps(record, ensure_ascii=False) + '\n')
                                total_lines_written += 1
                    except Exception as e:
                        print(f"Error processing {filepath}: {e}")

        print(f"Successfully processed and wrote {total_lines_written} lines to {output_file}.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert ToolBench datasets to JSONL")
    parser.add_argument("--input_dir", type=str, default="data_example/answer", help="Input directory containing JSON files")
    parser.add_argument("--output_file", type=str, default="training_data.jsonl", help="Output JSONL file path")

    args = parser.parse_args()
    process_datasets(args.input_dir, args.output_file)
