"""
Translator module for translating generated datasets to target languages.

Supports English-to-Arabic translation using Hala-1.2B-EN-AR-Translator model.
"""

import torch
from typing import Dict, Any
import logging

from ..configs.config import TranslationConfig
from ..dataset.dataset import Dataset

logger = logging.getLogger(__name__)


class Translator:
    """Translator for converting datasets to target language"""

    def __init__(self, config: TranslationConfig):
        """
        Initialize the Translator.

        Args:
            config: TranslationConfig instance containing language, model_path, and other settings

        Raises:
            ValueError: If language is not English but model_path is not specified
        """
        self.config = config
        self.model = None
        self.tokenizer = None
        self.pipe = None

        # Validate: if language is not English, model_path must be provided
        if config.language.lower() != "english" and not config.model_path:
            raise ValueError(
                f"Translation to '{config.language}' requires a model_path to be specified in the configuration."
            )

    def _load_model(self):
        """
        Load translation model on first use (lazy loading).

        Uses cuda:0 which is automatically remapped to the correct physical GPU
        by CUDA_VISIBLE_DEVICES set earlier by vLLM or MinerU.
        """
        if self.pipe is not None:
            return  # Already loaded

        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

        logger.info(f"Loading translation model from {self.config.model_path}...")

        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_path,
            torch_dtype="auto",
            device_map="auto"
        )
        self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

        logger.info(f"Translation model loaded successfully")

    def translate_text(self, text: str, source_lang: str = "English", target_lang: str = "Arabic") -> str:
        """
        Translate a single text from source language to target language.

        Args:
            text: Text to translate
            source_lang: Source language (default: "English")
            target_lang: Target language (default: "Arabic")

        Returns:
            Translated text
        """
        # Lazy load model
        self._load_model()

        # Prepare the prompt using chat template
        messages = [
            {"role": "user", "content": f"Translate the following text from {source_lang} to {target_lang}:\n\n{text}"}
        ]

        # Apply chat template
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # Generate translation
        outputs = self.pipe(
            prompt,
            max_new_tokens=self.config.max_tokens,
            do_sample=False,  # Disable sampling for consistent translation
            return_full_text=False
        )

        translated_text = outputs[0]["generated_text"].strip()
        return translated_text

    def translate_dataset(self, dataset: Dataset, target_lang: str = "Arabic") -> Dataset:
        """
        Translate all samples in a dataset to the target language.

        Args:
            dataset: Dataset to translate
            target_lang: Target language (default: "Arabic")

        Returns:
            New Dataset with translated samples
        """
        logger.info(f"Translating dataset to {target_lang}...")

        translated_dataset = Dataset()
        total_samples = len(dataset.samples)

        for idx, sample in enumerate(dataset.samples):
            translated_sample = self._translate_sample(sample, target_lang)
            translated_dataset.add_sample(translated_sample)
            print(f"    Translated {idx+1}/{total_samples}", end='\r')

        logger.info(f"\nTranslation completed: {total_samples} samples translated")
        return translated_dataset

    def _translate_sample(self, sample: Dict[str, Any], target_lang: str) -> Dict[str, Any]:
        """
        Translate a single sample.

        Translates the 'input' and 'output' fields of the sample.

        Args:
            sample: Sample dictionary
            target_lang: Target language

        Returns:
            Translated sample dictionary
        """
        translated_sample = sample.copy()

        # Translate input field
        if "input" in sample and sample["input"]:
            translated_sample["input"] = self.translate_text(sample["input"], target_lang=target_lang)

        # Translate output field
        if "output" in sample and sample["output"]:
            translated_sample["output"] = self.translate_text(sample["output"], target_lang=target_lang)

        return translated_sample

    def cleanup(self):
        """Release model and free GPU memory"""
        if self.model is not None:
            logger.info("Cleaning up translation model...")
            del self.model
            del self.tokenizer
            del self.pipe
            self.model = None
            self.tokenizer = None
            self.pipe = None

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
            logger.info("Translation model cleanup completed")
