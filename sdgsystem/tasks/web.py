import logging
from tqdm import tqdm

from .base import *
from ..huggingface import HFCrawler
from ..dataset.process import DataFilter, Formatter


class WebTaskExecutor(BaseTaskExecutor):
    def __init__(self, 
        config: WebTaskConfig, 
        llm: ModelClient,
    ) -> None:
        super(WebTaskExecutor, self).__init__(config, llm)

        self.config = config
        self.crawler = HFCrawler(self.config.huggingface_token)
        self.filter = DataFilter(llm)
        self.formatter = Formatter(llm)

    def crawl_execute(self) -> List:
        task_keywords = self.extract_keywords(task_definition=self.config.task_instruction)
        logging.info(f"🔑 Extracted {len(task_keywords)} keywords: {task_keywords}")
        
        crawl_dataset = []
        for task_keyword in tqdm(task_keywords, desc="🔍 Searching keywords", unit="keyword"):
            # Searching datasets on Huggingface
            task_datasets = self.crawler.search_datasets(query=task_keyword, limit=self.config.dataset_limit)
            if not task_datasets:
                continue
            
            for task_dataset in tqdm(task_datasets, desc=f"📦 {task_keyword}", leave=False, unit="dataset"):
                # Basic info of HF datasets
                dataset_id = task_dataset.id
                logging.info(f"Loading dataset: {dataset_id}")
                dataset_info = self.crawler.get_info(dataset_id)
                logging.info(f"Loaded dataset info for {dataset_id}")
                dataset_splits = self.crawler.get_splits(dataset_id)
                logging.info(f"Available splits for {dataset_id}: {dataset_splits}")
                first_rows = self.crawler.get_first_rows(dataset_id, dataset_splits, self.config.sample_limit)
                logging.info(f"Available {len(first_rows)} rows for {dataset_id}")
                # collect all examples
                for row in first_rows:
                    crawl_dataset.append({
                        "keyword": task_keyword,
                        "id": dataset_id,
                        "info": dataset_info,
                        "row": row
                    })
                    
        return crawl_dataset
    
    def process_sample(self, sample):
        row = sample["row"]
        legal_keys = row.keys()
        
        # Check which field maps "Input" and "Output"
        fields = self.filter.field_filter(row=row, legal_keys=legal_keys)

        if fields["input"] is None or fields["output"] is None:
            logging.info("Skipping row due to missing input/output fields.")
            return None
        
        # Get the original Input text and Output text
        input_text = row.get(fields["input"])
        output_text = row.get(fields["output"])
        if input_text is None or output_text is None:
            logging.info("Skipping row due to None input/output values.")
            return None
        
        # Judge the original sample and keep the score > 8 for each metric
        sample_scores = self.filter.instruction_judge(self.config.task_instruction, f"input: {input_text}\noutput: {output_text}")
        for criteria, score in sample_scores.items():
            if int(score) < 6:
                logging.info(f"Skipping row due to low score on {criteria}: {score}")
                return None
            
        # convert the format
        formatted_sample = self.formatter.format_conversion(
            input_text,
            output_text,
            self.config.input_instruction,
            self.config.output_instruction
        )
        if formatted_sample.get("input") is None or formatted_sample.get("output") is None:
            logging.info("Skipping row due to None formatted input/output values.")
            return None
        
        sample["original_input"] = input_text
        sample["original_output"] = output_text
        sample["scores"] = sample_scores
        sample["input"] = formatted_sample["input"]
        sample["output"] = formatted_sample["output"]
        return sample

    def process_dataset(self, crawl_dataset):
        total = len(crawl_dataset)
        logging.info(f"🚀 Launching {total} sync sample-processing tasks...")

        processed_samples = []

        for i, sample in enumerate(crawl_dataset, start=1):
            result = self.process_sample(sample)
            processed_samples.append(result)
            self.llm.report_token_usage(i, total)

        processed_dataset = Dataset()
        processed_dataset.add_samples(samples=processed_samples)

        logging.info(f"✅ Finished processing {len(processed_dataset)} valid samples.")
        return processed_dataset

    def execute(self) -> Dataset:
        """
        Execute the full web task pipeline:
        1. Crawl HuggingFace datasets based on the task instruction.
        2. Process and filter each sample.
        3. Return the final processed dataset.
        """
        logging.info("🚀 Starting WebTaskExecutor pipeline...")

        # Step 1: Crawl datasets from HuggingFace
        logging.info("📡 Crawling datasets from HuggingFace...")
        crawl_dataset = self.crawl_execute()
        logging.info(f"📦 Collected {len(crawl_dataset)} raw samples from HuggingFace.")

        if len(crawl_dataset) == 0:
            logging.warning("❌ No datasets found for the given keywords.")
            return Dataset()

        # Step 2: Process dataset
        logging.info("⚙️ Processing and filtering dataset samples...")
        processed_dataset = self.process_dataset(crawl_dataset)

        # Step 3: Return the final dataset after filtering and formatting
        logging.info(f"✅ WebTaskExecutor finished. Final dataset size: {len(processed_dataset)} samples.")
        return processed_dataset