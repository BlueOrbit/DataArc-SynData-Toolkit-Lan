from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
from tqdm import tqdm
from rank_bm25 import BM25Okapi
import json
import logging

from ..configs.config import RetrievalConfig
from ..utils import tokenize

logger = logging.getLogger(__name__)


class BaseRetriever(ABC):
    """
    Abstract base class of retriever
    """
    def __init__(self,
        config: RetrievalConfig,
        cache_corpus: bool = True
    ) -> None:
        self.passages_dir = config.passages_dir
        self.top_k = config.top_k
        self.cache_corpus = cache_corpus

        # Validate and get passages directory path
        self._validate_passages_dir(self.passages_dir)

        # Cache for loaded passages
        self._passages_cache: Optional[List[str]] = None

    def _validate_passages_dir(self, passages_dir: str) -> None:
        """
        Validate that passages_dir exists and contains JSONL files.

        Args:
            passages_dir: Directory containing JSONL passage files

        Raises:
            ValueError: If directory doesn't exist or contains no JSONL files
        """
        passages_path = Path(passages_dir)

        if not passages_path.exists():
            raise ValueError(f"Passages directory does not exist: {passages_dir}")

        if not passages_path.is_dir():
            raise ValueError(f"Passages path is not a directory: {passages_dir}")

        # Check for JSONL files
        jsonl_files = list(passages_path.glob("*.jsonl"))
        if not jsonl_files:
            raise ValueError(f"No JSONL files found in passages directory: {passages_dir}")

        logger.info(f"Found {len(jsonl_files)} JSONL file(s) in {passages_dir}")

    def _load_passages_from_jsonl(self, passages_dir: str) -> List[str]:
        """
        Load all passages from JSONL files in passages directory.

        Args:
            passages_dir: Directory path containing JSONL files

        Returns:
            List of passage texts
        """
        collected_passages = []
        passages_path = Path(passages_dir)

        # Find all JSONL files
        jsonl_files = list(passages_path.glob("*.jsonl"))

        for jsonl_file in tqdm(jsonl_files, desc=f"Loading passages from {passages_path.name}"):
            try:
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, start=1):
                        line = line.strip()
                        if not line:
                            continue

                        try:
                            data = json.loads(line)
                            # Get 'text' field from JSONL
                            if 'text' in data:
                                text = data['text']
                            else:
                                # Concatenate all values if 'text' not found
                                text = ' '.join(str(v) for v in data.values())

                            if text.strip():
                                collected_passages.append(text)

                        except json.JSONDecodeError as e:
                            logger.warning(f"Warning: Invalid JSON at {jsonl_file}:{line_num} - {e}")
                            continue

            except Exception as e:
                logger.error(f"Error reading file {jsonl_file}: {e}")

        return collected_passages

    def _get_passages(self) -> List[str]:
        """
        Get passages (from cache or load fresh).

        Returns:
            List of passage texts
        """
        if self.cache_corpus and self._passages_cache is not None:
            return self._passages_cache

        passages = self._load_passages_from_jsonl(self.passages_dir)

        if self.cache_corpus:
            self._passages_cache = passages

        return passages

    @abstractmethod
    def _search(self, 
        documents: List[str], 
        keywords: List[str]
    ) -> List[str]:
        return []

    def retrieve(self, 
        key_words: List[str], 
    ) -> List[str]:
        documents = self._get_passages()
        relevant_passages = self._search(documents, key_words)
        
        return relevant_passages

    def clear_cache(self):
        """Clear cached passages to free memory."""
        self._passages_cache = None


class BM25Retriever(BaseRetriever):
    """
    BM25-based retriever for finding relevant documents.

    Workflow:
    1. Load documents from corpus
    2. Rank documents using BM25
    3. Return top-k relevant passages
    """
    def __init__(self, 
        config: RetrievalConfig, 
        cache_corpus: bool = True
    ) -> None:
        super(BM25Retriever, self).__init__(config, cache_corpus)

    def _search(self, 
        documents: List[str], 
        keywords: List[str]
    ) -> List[str]:
        """
        Search documents using BM25 algorithm.

        Args:
            documents: List of document texts
            keywords: List of keywords for retrieval

        Returns:
            List of top-k ranked documents
        """
        # Tokenize documents
        logger.info("Tokenizing documents...")
        tokenized_docs = [tokenize(doc) for doc in tqdm(documents, desc="Tokenizing")]

        # Tokenize query keywords
        query_tokens = tokenize(" ".join(keywords))

        # Create BM25 index
        logger.info("Building BM25 index...")
        bm25 = BM25Okapi(tokenized_docs)

        # Calculate scores
        logger.info("Calculating relevance scores...")
        scores = bm25.get_scores(query_tokens)

        # Rank and return top-k
        logger.info(f"Selecting top {self.top_k} documents...")
        sorted_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )
        top_documents = [documents[i] for i in sorted_indices[:self.top_k]]

        return top_documents