import os
from abc import ABC, abstractmethod
from typing import List, Dict, Union, Tuple
from tqdm import tqdm

from ..configs.config import BaseRewriteConfig, DifficultyAdjustRewriteConfig
from ..dataset.dataset import Dataset
from ..models import ModelClient, ModelUsageCounter
from ..prompts import HARDER_SAMPLE_PROMPT, SIMPLER_SAMPLE_PROMPT
from ..parallel import ParallelExecutor
from ..buffer import TaskBuffer
from .base import BaseGenerator


class BaseRewriter(ABC, BaseGenerator):
    """
    Base class for rewrite synthetic training data
    """
    def __init__(self,
        model: ModelClient,
        config: BaseRewriteConfig,
        buffer_dir: str = "buffer"
    ) -> None:
        """Initialize the Rewriter"""
        super(BaseRewriter, self).__init__(model, config, buffer_dir)
        self.config = config

    @abstractmethod
    def _rewrite_batch(self,
        batch_start_end: Tuple[int, int],
        samples: List[Dict],
        usage_counter: ModelUsageCounter = None
    ) -> List[Union[Dict, str]]:
        """
        Rewrite a batch of samples.

        Args:
            batch_start_end: Tuple of (start_index, end_index) for the batch
            samples: Full list of samples to extract batch from
            usage_counter: Optional usage counter

        Returns:
            List of rewritten samples (dict for learnable, str for others)
        """
        return []

    @abstractmethod
    def _process_dataset_by_evaluations(self, dataset: Dataset, evaluations: Dict) -> List[Dict]:
        """
        transform samples in dataset to the samples which rewriting demands, according to the evaluations
        """
        return []

    @staticmethod
    def get_specific_rewriter(llm: ModelClient, config: BaseRewriteConfig) -> "BaseRewriter":
        if isinstance(config, DifficultyAdjustRewriteConfig):
            return DifficultyAdjustRewriter(llm, config)

        raise Exception(f"Rewriter with method {config.method} is not supported.")

    def rewrite(self,
        dataset: Dataset,
        evaluations: Dict,
        parallel_executor: ParallelExecutor = None,
        reporter=None
    ) -> Dataset:
        """
        Rewrite dataset based on evaluation results.

        Args:
            dataset: Original dataset
            evaluations: Evaluation results
            parallel_executor: Optional parallel executor
            reporter: Optional progress reporter for SSE updates

        Returns:
            Rewritten dataset
        """
        rewrite_dataset = Dataset()

        # process dataset according to the evaluation results
        samples = self._process_dataset_by_evaluations(dataset, evaluations)

        # batch rewrite samples
        batch_size = getattr(self.config, 'batch_size', 5)
        batch_idxes: List[Tuple[int, int]] = []
        for batch_start in range(0, len(samples), batch_size):
            batch_end = min(batch_start + batch_size, len(samples))
            batch_idxes.append((batch_start, batch_end))

        # Update reporter
        if reporter:
            reporter.update_step(
                message=f"Rewriting {len(samples)} samples...",
                batch_current=0,
                batch_total=len(batch_idxes),
                batch_size=batch_size
            )

        # initialize the usage counter and buffer for rewriter-generation
        usage_counter_gen = ModelUsageCounter(total=len(batch_idxes), name="Rewriter-Generation")
        buffer_gen = TaskBuffer(total=len(batch_idxes), save_dir=os.path.join(self.buffer_dir, "rewrite-generation"))

        # rewrite in batches
        rewrite_batches: List[List[Union[Dict, str]]] = []

        if parallel_executor and parallel_executor.n_workers > 1:
            # set up progress callback for parallel processing
            if reporter:
                def on_rewrite_progress(uc: ModelUsageCounter):
                    reporter.update_step(
                        message=f"Rewritten batch {uc.completed}/{uc.total}",
                        batch_current=uc.completed,
                        batch_total=uc.total,
                        batch_size=batch_size,
                        tokens=uc.token,
                        time_elapsed=uc.time,
                        estimated_remaining_tokens=uc.estimated_remaining_tokens,
                        estimated_remaining_time=uc.estimated_remaining_time,
                    )
                usage_counter_gen.set_on_update(on_rewrite_progress)

            # parallel processing
            rewrite_batches: List[List[Union[Dict, str]]] = parallel_executor.execute(
                iterable_inputs=batch_idxes,
                process_function=self._rewrite_batch,
                samples=samples,
                usage_counter=usage_counter_gen,
                n=1,
                buffer=buffer_gen
            )
        else:
            # sequential processing
            rewrite_batches: List[List[Union[Dict, str]]] = buffer_gen.load(usage_counter_gen)
            for batch_idx, (batch_start, batch_end) in enumerate(tqdm(batch_idxes, desc="Rewriting batches", unit="batch")):
                if buffer_gen and buffer_gen.detail_progress[batch_idx]:
                    continue

                batch_results = self._rewrite_batch(
                    batch_start_end=(batch_start, batch_end),
                    samples=samples,
                    usage_counter=usage_counter_gen
                )
                rewrite_batches.append(batch_results)

                usage_counter_gen.estimate_usage(n=1)
                buffer_gen.add_progress([batch_idx])
                buffer_gen.save(rewrite_batches, usage_counter_gen)

                # Report progress
                if reporter:
                    reporter.update_step(
                        message=f"Rewritten batch {batch_idx + 1}/{len(batch_idxes)}",
                        batch_current=batch_idx + 1,
                        batch_total=len(batch_idxes),
                        batch_size=batch_size,
                        tokens=usage_counter_gen.token,
                        time_elapsed=usage_counter_gen.time,
                        estimated_remaining_tokens=usage_counter_gen.estimated_remaining_tokens,
                        estimated_remaining_time=usage_counter_gen.estimated_remaining_time,
                    )

        # Flatten batches
        rewrite_sample_strings: List[Union[Dict, str]] = []
        for batch in rewrite_batches:
            rewrite_sample_strings.extend(batch)

        if reporter:
            reporter.complete_step({"rewritten": len(rewrite_sample_strings)})

        # Validate rewritten samples
        if reporter:
            reporter.start_step(
                "rewrite_validation", "Validating Rewritten Samples",
                message="Validating samples...",
                total=len(rewrite_sample_strings), 
                unit="samples"
            )

        # initialize usage counter and buffer for rewriter-validate
        usage_counter_val = ModelUsageCounter(total=len(rewrite_sample_strings), name="Rewriter-Validation")
        buffer_val = TaskBuffer(total=len(rewrite_sample_strings), save_dir=os.path.join(self.buffer_dir, "rewrite-validation"))

        # parse and validate
        rewrite_samples: List[Dict] = self.parse_and_validate_samples(
            response_strings=rewrite_sample_strings,
            output_instruction=self.config.output_instruction,
            usage_counter=usage_counter_val,
            parallel_executor=parallel_executor,
            buffer=buffer_val,
            reporter=reporter
        )
        rewrite_dataset.add_samples(rewrite_samples)

        if reporter:
            reporter.complete_step({"valid": len(rewrite_samples), "invalid": len(rewrite_sample_strings) - len(rewrite_samples)})

        return rewrite_dataset


class DifficultyAdjustRewriter(BaseRewriter):
    """
    class for rewrite synthetic data by adjust their difficulty
    """
    def __init__(self,
        llm: ModelClient,
        config: DifficultyAdjustRewriteConfig
    ) -> None:
        super(DifficultyAdjustRewriter, self).__init__(llm, config)
        self.config: DifficultyAdjustRewriteConfig
        self.harder_temperature: float = self.config.harder_temperature
        self.easier_temperature: float = self.config.easier_temperature

    def _process_dataset_by_evaluations(self,
        dataset: Dataset,
        evaluations: Dict
    ) -> List[Dict]:
        """
        transform samples in dataset to the samples which rewriting demands, according to the evaluations
        """
        samples: List[Dict] = []
        for sample, score in zip(dataset.samples, evaluations["scores"]):
            if score == 1.0:
                label = "solved"
            elif score == 0.0:
                label = "unsolved"
            else:
                label = "learnable"
            samples.append({"label": label, "sample": sample})
        return samples

    def _rewrite_batch(self,
        batch_start_end: Tuple[int, int],
        samples: List[Dict],
        usage_counter: ModelUsageCounter = None
    ) -> List[Union[Dict, str]]:
        """
        Rewrite a batch of samples. Learnable samples pass through unchanged,
        solved/unsolved samples are rewritten via LLM.

        Args:
            batch_start_end: Tuple of (start_index, end_index) for the batch
            samples: Full list of samples to extract batch from
            usage_counter: Optional usage counter

        Returns:
            List of results (dict for learnable, str for rewritten)
        """
        batch_start, batch_end = batch_start_end
        batch_samples = samples[batch_start:batch_end]

        results: List[Union[Dict, str]] = [None] * len(batch_samples)

        # Separate learnable from samples needing rewrite
        rewrite_indices: List[int] = []
        rewrite_prompts: List[str] = []
        rewrite_temps: List[float] = []

        # Use format_prompts to combine output_instruction with answer_config
        combined_output_instruction = self.model.answer_extractor.format_prompts(
            self.config.output_instruction
        )

        for idx, sample in enumerate(batch_samples):
            label = sample["label"]
            if label == "learnable":
                # Pass through unchanged
                results[idx] = sample["sample"]
            else:
                # Build prompt for rewriting
                is_harder = (label == "solved")
                prompt_template = HARDER_SAMPLE_PROMPT if is_harder else SIMPLER_SAMPLE_PROMPT
                temperature = self.harder_temperature if is_harder else self.easier_temperature

                prompt = prompt_template.format(
                    sample=sample["sample"],
                    input_instruction=self.config.input_instruction,
                    output_instruction=combined_output_instruction
                )
                rewrite_indices.append(idx)
                rewrite_prompts.append(prompt)
                rewrite_temps.append(temperature)

        # Batch generate for samples needing rewrite
        if rewrite_prompts:
            # Note: Using average temperature for batch (limitation of batch API)
            avg_temp = sum(rewrite_temps) / len(rewrite_temps)

            responses: List[str] = self.model.generate(
                prompts=rewrite_prompts,
                n=1,
                usage_counter=usage_counter,
                temperature=avg_temp
            )

            # Place responses back in correct positions
            for idx, response in zip(rewrite_indices, responses):
                results[idx] = response

        return results
