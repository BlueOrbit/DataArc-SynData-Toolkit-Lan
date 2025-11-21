from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


# Abstract base class of chunker
class BaseChunker(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into chunks.

        Args:
            text: Text content to chunk

        Returns:
            List of chunk dicts with 'content' and 'metadata'
        """
        return []


# class of Recursive Chunker
class RecursiveChunker(BaseChunker):
    """
    Recursive text chunker using hierarchical separators.

    Workflow:
    1. Try splitting with separator hierarchy (paragraphs, sentences, words)
    2. Preserve natural text boundaries
    3. Maintain size constraints with overlap
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None
    ) -> None:
        """
        Initialize the recursive chunker.

        Args:
            chunk_size: Maximum characters per chunk (default: 512)
            chunk_overlap: Overlap between chunks for context (default: 50)
            separators: Separator priority list (default: ["\n\n", "\n", ". ", " "])
        """
        super(RecursiveChunker, self).__init__()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " "]

        # Validate parameters
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be > 0, got {chunk_size}")
        if chunk_overlap < 0:
            raise ValueError(f"chunk_overlap must be >= 0, got {chunk_overlap}")
        if chunk_overlap >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({chunk_overlap}) must be < chunk_size ({chunk_size})"
            )

        logger.info(f"RecursiveChunker initialized - size: {chunk_size}, overlap: {chunk_overlap}")

    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into chunks using recursive strategy.

        Args:
            text: Text content to chunk

        Returns:
            List of chunk dicts with 'content' and 'metadata'
        """
        if not text:
            return []

        # Split text using recursive strategy
        text_chunks = self._split_recursive(text, self.separators)

        # Convert to structured format
        result = []
        for i, chunk_content in enumerate(text_chunks):
            chunk_dict = {
                'content': chunk_content,
                'metadata': {
                    'chunk_index': i,
                    'character_count': len(chunk_content),
                    'strategy': 'recursive'
                }
            }
            result.append(chunk_dict)

        logger.info(f"Split text into {len(result)} chunks")
        return result

    def _split_recursive(self, text: str, separators: List[str]) -> List[str]:
        """
        Recursively split text using separator hierarchy.

        Args:
            text: Text to split
            separators: List of separators to try in order

        Returns:
            List of text chunks
        """
        # Base case: text already small enough
        if len(text) <= self.chunk_size:
            return [text]

        # No more separators to try, force character-level split
        if not separators:
            return self._force_split(text)

        # Try splitting with first separator
        sep = separators[0]
        parts = text.split(sep)

        # Separator didn't help (no split occurred), try next separator
        if len(parts) == 1:
            return self._split_recursive(text, separators[1:])

        # Build chunks by combining parts
        chunks = []
        current = ""

        for part in parts:
            if not part:
                continue

            # Try adding this part to current chunk
            test = current + sep + part if current else part

            if len(test) <= self.chunk_size:
                # Fits, keep accumulating
                current = test
            else:
                # Doesn't fit
                if current:
                    # Save current chunk first
                    chunks.append(current)

                # If part itself is too big, split it further
                if len(part) > self.chunk_size:
                    chunks.extend(self._split_recursive(part, separators[1:]))
                    current = ""
                else:
                    # Part fits, start new chunk with it
                    current = part

        # Add final chunk if any
        if current:
            chunks.append(current)

        return chunks

    def _force_split(self, text: str) -> List[str]:
        """Character-level split with overlap (last resort)."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start = end - self.chunk_overlap

        return chunks
