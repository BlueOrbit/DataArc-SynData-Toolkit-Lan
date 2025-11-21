"""
Evaluator module for evaluating synthetic data with the working model.

This module provides evaluation logic for assessing the quality of synthetic
data by running inference with the base model and comparing predictions against
ground truth answers.
"""

from typing import List, Dict, Tuple
import logging
from tqdm import tqdm

from ..configs.config import EvaluationConfig, BaseComparisonConfig
from ..dataset.dataset import Dataset
from ..models import ModelClient, ModelUsageCounter
from .answer_comparison import AnswerComparer

logger = logging.getLogger(__name__)


class Evaluator:
    """
    Evaluator for assessing synthetic data quality with the working model.

    This class handles:
    1. Batch inference on synthetic data
    2. Answer comparison against ground truth

    Attributes:
        base_model: BaseModel instance for inference
        input_instruction: Instruction prepended to input
        output_instruction: Instruction for output format
        comparison_config: AnswerComparisonConfig for comparing answers
    """

    def __init__(
        self,
        base_model: ModelClient,
        llm: ModelClient,
        input_instruction: str,
        output_instruction: str,
        comparison_config: BaseComparisonConfig
    ):
        """
        Initialize the evaluator.

        Args:
            base_model: BaseModel instance for inference
            input_instruction: Instruction prepended to model input
            output_instruction: Instruction for output format
            answer_config: AnswerExtractionConfig instance
            comparison_config: AnswerComparisonConfig instance
        """
        self.base_model = base_model
        self.input_instruction = input_instruction
        self.output_instruction = output_instruction
        self.answer_comparer = AnswerComparer(
            config=comparison_config,
            llm=llm.get_model() if llm is not None else None
        )

    @classmethod
    def from_config(cls, base_model: ModelClient, llm: ModelClient, config: EvaluationConfig):
        """
        Create evaluator from configuration object.

        Args:
            base_model: BaseModel instance
            config: Config instance with evaluation settings

        Returns:
            Evaluator instance
        """
        return cls(
            base_model=base_model,
            llm=llm,
            input_instruction=config.input_instruction,
            output_instruction=config.output_instruction,
            comparison_config=config.answer_comparison_config
        )

    def evaluate(self, dataset: Dataset, **kwargs) -> Dict:
        """
        Evaluate, filter, and split samples from dataset

        Args:
            dataset: Dataset, samples with 'input' and 'output' keys

        Returns:
            Evaluation results of dataset, e.g.:
            {
                "scores": [s0, s1, ..., s_i, ...],
            }
            i is the index of sample in dataset
        """
        # intialize the usage counter for evaluator
        # estimate the token and time usage with each batch of samples
        usage_counter = ModelUsageCounter(total=len(dataset), name="Evaluator")  

        evaluated_samples = self.evaluate_samples(dataset.samples, usage_counter, **kwargs)
        evaluations: Dict[str, List] = {
            "scores": [s for s, _ in evaluated_samples]
        }
        return evaluations

    def evaluate_samples(
        self,
        samples: List[Dict[str, str]], 
        usage_counter: ModelUsageCounter = None, 
        batch_size: int = 100,
        temperature: float = 0.0,
        max_tokens: int = 1500,
        n: int = 1
    ) -> List[Tuple[float, Dict[str, str]]]:
        """
        Evaluate samples by running inference and comparing with ground truth.

        This method:
        1. Builds prompts from samples
        2. Runs batch inference with n samples per prompt
        3. Extracts answers from predictions
        4. Compares with ground truth
        5. Calculates score = correct_count / n
        6. Returns (score, sample_with_details) tuples

        Args:
            samples: List of samples with 'input' and 'output' keys
            batch_size: Batch size for inference
            temperature: Sampling temperature (0.0 for deterministic)
            max_tokens: Maximum tokens to generate
            n: Number of responses to generate per sample

        Returns:
            List of (score, sample) tuples where:
            - score: float (0.0 to 1.0) = correct_count / n
            - sample: dict with added 'score', 'correct_predictions', 'all_predictions'

            Note: When n=1, score will be either 0.0 or 1.0
        """
        results = []

        # Process in batches
        num_batches = (len(samples) + batch_size - 1) // batch_size

        # Determine description based on n
        desc = "Evaluating samples" if n == 1 else f"Scoring samples (n={n})"

        with tqdm(total=len(samples), desc=desc, unit="sample") as pbar:
            for batch_idx in range(num_batches):
                start_idx = batch_idx * batch_size
                end_idx = min((batch_idx + 1) * batch_size, len(samples))
                batch = samples[start_idx:end_idx]

                if not batch:
                    continue

                # Build prompts
                batch_prompts = [
                    self._build_prompt(sample['input'])
                    for sample in batch
                ]

                # Run inference with n responses per sample
                predictions = self.base_model.generate(
                    batch_prompts,
                    n=n,
                    usage_counter=usage_counter,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                # Evaluate each sample
                for sample, responses in zip(batch, predictions):
                    ground_truth = sample['output']

                    # Ensure responses is a list
                    if not isinstance(responses, list):
                        responses = [responses]

                    # Evaluate each of the n responses
                    eval_results = []
                    for pred in responses:
                        is_correct = self._evaluate_single(
                            sample['input'],
                            ground_truth,
                            pred
                        )
                        eval_results.append(is_correct)

                    # Calculate score as average
                    score = sum(eval_results) / len(eval_results)

                    # Store correct predictions
                    correct_preds = [pred for pred, res in zip(responses, eval_results) if res]

                    # Create sample with score info
                    sample_with_score = {
                        **sample,
                        'score': score,
                        'correct_predictions': correct_preds,
                        'all_predictions': responses
                    }

                    results.append((score, sample_with_score))

                    # Update progress bar with status in postfix
                    if n == 1:
                        status = "✓" if score == 1 else "✗"
                    else:
                        status = "✓" if score == 1 else "◐" if score > 0 else "✗"

                    pbar.set_postfix_str(f"Last: {status}")
                    pbar.update(1)

                # estimate the token and time usage for each batch
                if usage_counter:
                    usage_counter.estimate_usage(n=len(batch))

        return results

    @staticmethod
    def print_scoring_summary(
        solved: List[Dict],
        learnable: List[Dict],
        unsolved: List[Dict]
    ):
        """
        Print a summary of scoring results.

        Args:
            solved: List of solved samples (score == 1.0)
            learnable: List of learnable samples (0 < score < 1.0)
            unsolved: List of unsolved samples (score == 0.0)
        """
        total = len(solved) + len(learnable) + len(unsolved)

        if total == 0:
            logger.warning("No samples to summarize")
            return

        logger.info(f"\n{'='*60}")
        logger.info("Scoring Summary:")
        logger.info(f"  Total samples: {total}")
        logger.info(f"  Solved (score==1.0): {len(solved)} ({len(solved)/total*100:.1f}%)")
        logger.info(f"  Learnable (0<score<1): {len(learnable)} ({len(learnable)/total*100:.1f}%)")
        logger.info(f"  Unsolved (score==0.0): {len(unsolved)} ({len(unsolved)/total*100:.1f}%)")
        logger.info(f"{'='*60}\n")

    def _build_prompt(self, sample_input: str) -> str:
        """
        Build prompt from sample input and instructions.

        Args:
            sample_input: The input/question from sample

        Returns:
            Complete prompt for model inference
        """
        prompt = str(sample_input)

        # Use format_prompts to combine output_instruction with answer_config
        if self.output_instruction:
            formatted_instruction = self.base_model.answer_extractor.format_prompts(
                self.output_instruction
            )
            prompt += " " + formatted_instruction

        return prompt

    def _evaluate_single(
        self,
        sample_input: str,
        ground_truth: str,
        prediction: str, 
        usage_counter: ModelUsageCounter = None, 
    ) -> bool:
        """
        Evaluate a single prediction against ground truth.

        Args:
            sample_input: Original input/question
            ground_truth: Ground truth answer
            prediction: Model prediction

        Returns:
            True if prediction matches ground truth, False otherwise
        """
        # Extract answer from ground truth
        gt_answer = self.base_model.answer_extractor.extract_answers(ground_truth)
        gt_extracted = gt_answer is not None

        # Extract answer from prediction
        pred_answer = self.base_model.answer_extractor.extract_answers(prediction)
        pred_extracted = pred_answer is not None

        # Decision logic: if both succeed, compare extracted; if either fails, compare full texts
        if gt_extracted and pred_extracted:
            # Both extractions succeeded - compare extracted answers
            logger.debug(f"Both extracted - GT: {gt_answer}, Pred: {pred_answer}")
        else:
            # At least one extraction failed - compare full texts for fairness
            gt_answer = ground_truth.strip()
            pred_answer = prediction.strip()
            if not gt_extracted and not pred_extracted:
                logger.debug(f"Both extraction failed - comparing full texts")
            elif not gt_extracted:
                logger.debug(f"GT extraction failed - comparing full texts")
            else:  # not pred_extracted
                logger.debug(f"Prediction extraction failed - comparing full texts")

        # Compare answers using configured method
        is_correct = self.answer_comparer.compare_answers(
            predicted=pred_answer,
            ground_truth=gt_answer, 
            usage_counter=usage_counter, 
            question=sample_input,
        )

        return is_correct
