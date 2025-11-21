"""
SDG Synthetic data generator for distillation pipeline.

This module provides a simple LLM-based generator that creates synthetic training
data based on task instructions and optional demonstration examples.
"""

import logging
from typing import List, Dict, Optional
from tqdm import tqdm

from ..models import ModelClient, ModelUsageCounter
from ..configs.config import DistillTaskConfig
from ..prompts import SDG_DISTILL_BATCH_GENERATION_PROMPT, PATTERN_GENERATION_PROMPT
from .base import *

logger = logging.getLogger(__name__)


class SDGDistillation(BaseDistillation):
    """
    SDG Generator for creating synthetic training data using LLMs.

    This generator creates synthetic question-answer pairs based on:
    - Task instruction (required)
    - Input/output format instructions (optional)
    - Demonstration examples (optional)

    No passage retrieval - pure instruction-based generation.
    Uses batch generation with patterns for better diversity.
    """

    def __init__(
        self,
        model: ModelClient,
        config: DistillTaskConfig
    ):
        """
        Initialize the synthetic data generator.

        Args:
            model: ModelClient instance
            config: DistillTaskConfig instance containing task configuration
        """
        super().__init__(model, config)

        self.input_instruction = config.input_instruction
        self.output_instruction = config.output_instruction

    def generate(
        self,
        demo_examples: Optional[List[Dict]] = None,
        max_tokens: int = 4096
    ) -> List[Dict]:
        """
        Generate synthetic data samples using batch generation.

        Args:
            demo_examples: Optional list of demo examples (dict with 'input', 'output')
            max_tokens: Maximum tokens per generation

        Returns:
            List of generated samples, each a dict with 'input' and 'output' keys
        """
        # Get parameters from config
        num_samples = self.config.num_samples
        temperature = self.config.temperature
        batch_size = self.config.batch_size
        results = []

        # Calculate total iterations: 1 (pattern extraction if demos) + num_batches
        num_batches = (num_samples + batch_size - 1) // batch_size
        total_iterations = (1 if demo_examples else 0) + num_batches
        usage_counter = ModelUsageCounter(total=total_iterations, name="Distillation-Generation")

        # Extract patterns from demo examples if provided
        patterns = ""
        if demo_examples:
            patterns = self.generate_patterns(demo_examples, usage_counter)

        logger.info(f"Generating {num_samples} synthetic samples in batches of {batch_size}...")

        with tqdm(total=num_samples, desc="Generating samples", unit="sample") as pbar:
            for batch_idx in range(num_batches):
                # Calculate batch size for this iteration
                remaining = num_samples - len(results)
                current_batch_size = min(batch_size, remaining)

                logger.info(f"Batch {batch_idx + 1}/{num_batches}: Generating {current_batch_size} samples...")

                # Build prompt for batch generation (provide all demo examples to every batch)
                prompt = self._build_batch_prompt(
                    demo_examples=demo_examples,
                    patterns=patterns,
                    batch_size=current_batch_size
                )

                # Generate using model client
                try:
                    response = self.model.generate(
                        prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        n=1,
                        usage_counter=usage_counter
                    )

                    # Parse batch response
                    batch_samples = self._parse_batch_response(response)

                    if batch_samples:
                        results.extend(batch_samples[:current_batch_size])
                        logger.info(f"Successfully generated {len(batch_samples)} samples in this batch")
                        pbar.update(len(batch_samples))
                    else:
                        logger.warning(f"Failed to parse batch {batch_idx + 1}, skipping")

                except Exception as e:
                    logger.error(f"Error generating batch {batch_idx + 1}: {e}")

                # Report usage after each batch (1 iteration = 1 batch)
                usage_counter.estimate_usage(1)

        logger.info(f"Successfully generated {len(results)}/{num_samples} samples")

        return results[:num_samples]

    def generate_patterns(self, demo_examples: List[Dict], usage_counter: ModelUsageCounter = None) -> str:
        """
        Extract general patterns from demonstration examples.

        Args:
            demo_examples: List of demo examples
            usage_counter: Optional ModelUsageCounter for tracking token usage

        Returns:
            Pattern summary as string
        """
        if not demo_examples:
            return ""

        logger.info("Extracting patterns from demonstration examples...")

        # Format demo examples for pattern extraction
        demo_text = ""
        for idx, example in enumerate(demo_examples, 1):
            demo_text += f"Example {idx}:\n"
            demo_text += f"Input: {example.get('input', '')}\n"
            demo_text += f"Output: {example.get('output', '')}\n\n"

        # Build pattern extraction prompt
        prompt = PATTERN_GENERATION_PROMPT.format(
            task_instruction=self.task_instruction,
            input_instruction=self.input_instruction or "No specific format",
            output_instruction=self.output_instruction or "No specific format",
            demo_examples=demo_text
        )

        try:
            response, _ = self.model.generate(
                prompt,
                temperature=0.3,
                max_tokens=1024,
                n=1,
                usage_counter=usage_counter
            )

            # Report usage for pattern extraction (1 iteration)
            if usage_counter:
                usage_counter.estimate_usage(1)

            logger.info("Pattern extraction completed")
            return response.strip()

        except Exception as e:
            logger.error(f"Error extracting patterns: {e}")
            return ""

    

    def _build_batch_prompt(
        self,
        demo_examples: Optional[List[Dict]],
        patterns: str,
        batch_size: int
    ) -> str:
        """Build prompt for batch generation."""

        # Build input instruction section
        if self.input_instruction:
            input_section = f"""## Input Format Instruction
{self.input_instruction}
You MUST follow this input format strictly!
"""
        else:
            input_section = ""

        # Build output instruction section
        if self.output_instruction:
            # Use format_prompts to combine output_instruction with answer_config
            formatted_output = self.model.answer_extractor.format_prompts(self.output_instruction)
            output_section = f"""## Output Format Instruction
{formatted_output}
You MUST follow this output format strictly!
"""
        else:
            output_section = ""

        # Build pattern section
        if patterns:
            pattern_section = f"""## Extracted Patterns
Based on the demonstration examples, here are the general patterns to follow:
{patterns}

Use these patterns as guidance to create diverse examples.
"""
        else:
            pattern_section = ""

        # Build demo examples section (show all demo examples if provided)
        if demo_examples:
            demo_section = "## Demonstration Examples\n"
            demo_section += "Here are example inputs and outputs for reference:\n\n"
            for idx, example in enumerate(demo_examples, 1):
                demo_section += f"Example {idx}:\n"
                demo_section += f"Input: {example.get('input', '')}\n"
                demo_section += f"Output: {example.get('output', '')}\n\n"
            demo_section += "IMPORTANT: Do NOT copy or paraphrase these examples. Generate completely NEW and DIFFERENT examples!\n"
        else:
            demo_section = ""

        # Format the main prompt
        prompt = SDG_DISTILL_BATCH_GENERATION_PROMPT.format(
            task_instruction=self.task_instruction,
            input_instruction_section=input_section,
            output_instruction_section=output_section,
            pattern_section=pattern_section,
            demo_examples_section=demo_section,
            batch_size=batch_size
        )

        return prompt
