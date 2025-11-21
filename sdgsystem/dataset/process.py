"""
Filter out data suitable for the task and convert the format
"""

import re
import json
from typing import Dict

# from ..configs.constants import DEFAULT_WEB_TASK_INPUT_FORMAT, DEFAULT_WEB_TASK_OUTPUT_FORMAT
from ..models import ModelClient
from ..prompts import FIELD_FILTER_PROMPT, INSTRUCTION_JUDGE_PROMPT, SOLVABLE_JUDGE_PROMPT, FORMAT_CONVERSION_PROMPT


# Filter out data or texts
class DataFilter:
    def __init__(self, llm: ModelClient) -> None:
        self.llm = llm

    def field_filter(self, 
        row: str, 
        legal_keys
    ) -> Dict[str, str]:
        prompt = FIELD_FILTER_PROMPT.format(row=row, legal_keys=legal_keys)

        output: str = self.llm.generate(prompt)
        match = re.search(r'\{.*\}', output, re.S)
        if match:
            json_str = match.group().strip()
            try:
                return json.loads(json_str)
            except:
                return {"input": None, "output": None}
        return {"input": None, "output": None}

    def instruction_judge(self, 
        task_description: str, 
        instruction_sample: Dict[str, str]
    ) -> Dict[str, int]:
        prompt = INSTRUCTION_JUDGE_PROMPT.format(task_description=task_description, instruction_sample=instruction_sample)

        output: str = self.llm.generate(prompt)
        match = re.search(r'\{.*\}', output, re.S)
        if match:
            try:
                return json.loads(match.group().strip())
            except:
                return {"Relevance": 5, "Correctness": 5, "Helpfulness": 5, "Clarity": 5, "Difficulty": 5}
        return {"Relevance": 5, "Correctness": 5, "Helpfulness": 5, "Clarity": 5, "Difficulty": 5}

    def solvable_judge(self, 
        instruction_sample: Dict[str, str]
    ) -> bool:
        solve_prompt = f"Please think step by step and answer this question.\n{instruction_sample['input']}"
        solution: str = self.llm.generate(solve_prompt)

        judge_prompt = SOLVABLE_JUDGE_PROMPT.format(instruction_sample=instruction_sample, solution=solution)
        judge_output: str = self.llm.generate(judge_prompt)

        return "true" in judge_output.lower()


# Convert format
class Formatter:
    def __init__(self, 
        llm: ModelClient, 
        # input_format: str = DEFAULT_WEB_TASK_INPUT_FORMAT, 
        # output_format: str = DEFAULT_WEB_TASK_OUTPUT_FORMAT
    ) -> None:
        self.llm = llm
        # self.input_format = input_format
        # self.output_format = output_format

    def format_conversion(self, 
        input: str, 
        output: str, 
        input_format: str,
        output_format: str
    ) -> Dict[str, str]:
        prompt = FORMAT_CONVERSION_PROMPT.format(input=input, output=output, input_format=input_format, output_format=output_format)

        output_text: str = self.llm.generate(prompt)
        match = re.search(r'\{.*\}', output_text, re.S)
        if match:
            try:
                return json.loads(match.group().strip())
            except:
                return {"input": None, "output": None}
        return {"input": None, "output": None}