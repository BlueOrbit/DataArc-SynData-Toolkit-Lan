from typing import List, Dict
from abc import ABC, abstractmethod

from ..prompts import KEYWORD_EXTRACTION_PROMPT
from ..models import ModelClient, ModelUsageCounter
from ..dataset.dataset import Dataset
from ..configs.config import *
from ..configs.constants import DEFAULT_KEYWORDS_EXTRACT_EXAMPLES


class KeywordExtractor:
    """
    Extracts domain keywords using LLM based on task instruction and demo examples.
    """

    def __init__(self, llm: ModelClient):
        """
        Initialize keyword extractor.

        Args:
            llm_function: Function that takes a prompt string and returns LLM response
        """
        self.llm = llm

    def extract_keywords(
        self,
        task_instruction: str,
        demo_examples: List[Dict[str, str]] = DEFAULT_KEYWORDS_EXTRACT_EXAMPLES,
        usage_counter: ModelUsageCounter = None
    ) -> List[str]:
        """
        Extract multiple domain keywords by analyzing the task using LLM.

        Args:
            task_instruction: Task instruction text
            demo_examples: List of demo examples with 'input' and 'output' keys
            usage_counter: Optional usage counter to track token and time usage

        Returns:
            List of domain keywords (e.g., ["mathematics", "arithmetic", "algebra"])
        """
        prompt = KEYWORD_EXTRACTION_PROMPT.format(
            task_instruction=task_instruction,
            demo_examples=demo_examples
        )

        response: str = self.llm.generate(prompt, usage_counter=usage_counter)
        keywords = self._parse_keyword_list(response)

        if usage_counter:
            usage_counter.estimate_usage(n=1)

        return keywords

    def _parse_keyword_list(self, response: str) -> List[str]:
        """
        Parse LLM response to extract list of keywords.

        Args:
            response: LLM response text

        Returns:
            List of extracted keywords

        Raises:
            ValueError: If response format is invalid
        """
        try:
            # Find the list in the response
            start_idx = response.find('[')
            end_idx = response.find(']')

            if start_idx == -1 or end_idx == -1:
                raise ValueError("No list found in response")

            list_str = response[start_idx:end_idx + 1]

            # Evaluate as Python list
            keywords = eval(list_str)

            if not isinstance(keywords, list):
                raise ValueError("Parsed result is not a list")

            # Convert all to strings and clean
            return [str(kw).strip() for kw in keywords if kw]

        except (ValueError, SyntaxError) as e:
            raise ValueError(f"Invalid response format for extracting keywords: {e}")


class BaseTaskExecutor(ABC):
    def __init__(self, config: BaseTaskConfig, llm: ModelClient) -> None:
        self.config = config
        self.llm = llm
        self.keyword_extractor = KeywordExtractor(self.llm)

    def extract_keywords(self,
        task_definition: str,
        demo_examples: List[Dict[str, str]] = DEFAULT_KEYWORDS_EXTRACT_EXAMPLES,
        usage_counter: ModelUsageCounter = None
    ) -> List[str]:
        """
        Extracts domain keywords using LLM based on task instruction and demo examples.
        """
        domain = self.config.domain
 
        # Extract keywords using LLM
        keywords = self.keyword_extractor.extract_keywords(task_instruction=task_definition, demo_examples=demo_examples, usage_counter=usage_counter)
        
        # if domain is non-empty and not already in keywords, add it
        if domain and domain not in keywords:
            keywords.append(domain)

        return keywords

    @abstractmethod
    def execute(self, reporter=None) -> Dataset:
        pass

