import os
import json
from typing import Dict, List, Optional


# utils for text
def tokenize(text: str) -> List[str]:
    """
    Simple tokenization: lowercase and split by spaces.

    Args:
        text: Input text

    Returns:
        List of tokens
    """
    return text.lower().split()


# utils for file
def check_dir(path: str):
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)

def load_json(path: str):
    assert path.endswith(".json")
    with open(path, "r") as fr:
        datas = json.load(fr)
    return datas

def load_jsonl(path: str) -> List:
    assert path.endswith(".jsonl")
    datas: List = []
    with open(path, "r") as fr:
        for line in fr:
            if line:
                data = json.loads(line.strip())
                datas.append(data)
    return datas

def save_json(obj, path: str):
    assert path.endswith(".json")
    check_dir(path)
    with open(path, "w", encoding="utf-8") as fw:
        json.dump(obj, fw, ensure_ascii=False, indent=4)

def save_jsonl(obj: List, path: str):
    assert path.endswith(".jsonl")
    check_dir(path)
    check_dir(path)
    with open(path, "w", encoding="utf-8") as fw:
        for data in obj:
            fw.write(json.dumps(data, ensure_ascii=False) + "\n")