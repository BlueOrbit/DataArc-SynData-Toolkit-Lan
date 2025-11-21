from pydantic import BaseModel, Field
from typing import List, Dict, Union


class BaseProcessorArgs(BaseModel):
    enable: bool = Field(default=False)


class MajorityVotingArgs(BaseProcessorArgs):
    """
    Additional arguments for majority_voting
    """
    samples: Union[Dict, List[Dict]] = Field(...)


class AnswerExtractionArgs(BaseProcessorArgs):
    """
    Additional arguments for extract_answers
    """


class ProcessorArgs(BaseModel):
    majority_voting: MajorityVotingArgs = Field(default=None)
    answer_extraction: AnswerExtractionArgs = Field(default=None)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Dict]) -> "ProcessorArgs":
        answer_extraction: AnswerExtractionArgs = None
        majority_voting: MajorityVotingArgs = None

        for method, arguments in config_dict.items():
            if method == "answer_extraction":
                enable: bool = arguments.get("enable", True)
                answer_extraction = AnswerExtractionArgs(enable=enable)
            elif method == "majority_voting":
                samples: Union[Dict, List[Dict]] = arguments.get("samples")
                majority_voting = MajorityVotingArgs(enable=True, samples=samples)
                # majority_voting need extract answers from LLM response, so enable answer_extraction at the same time
                answer_extraction = AnswerExtractionArgs(enable=True)
            else:
                raise Exception(f"No process method named {method}.")
        
        return cls(
            majority_voting=majority_voting, 
            answer_extraction=answer_extraction
        )
