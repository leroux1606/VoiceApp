"""Helper utility functions."""

import hashlib
import json
from typing import Any, Dict, List, Optional
from datetime import datetime


def calculate_token_estimate(text: str) -> int:
    """
    Estimate token count for a text string.

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    # Rough estimate: 1 token ≈ 4 characters
    return len(text) // 4


def calculate_cost(tokens: int, price_per_1k_tokens: float) -> float:
    """
    Calculate cost based on token count.

    Args:
        tokens: Number of tokens
        price_per_1k_tokens: Price per 1000 tokens

    Returns:
        Total cost
    """
    return (tokens / 1000) * price_per_1k_tokens


def generate_message_id() -> str:
    """
    Generate a unique message ID.

    Returns:
        Unique message ID string
    """
    timestamp = datetime.now().isoformat()
    hash_obj = hashlib.md5(timestamp.encode())
    return hash_obj.hexdigest()[:16]


def chunk_text(text: str, chunk_size: int, overlap: int = 0) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Input text to chunk
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        text: Input text
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    # Remove null bytes
    text = text.replace("\x00", "")

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]

    return text.strip()


def format_tool_output(tool_name: str, result: Any, error: Optional[str] = None) -> Dict[str, Any]:
    """
    Format tool execution output.

    Args:
        tool_name: Name of the tool
        result: Tool execution result
        error: Optional error message

    Returns:
        Formatted output dictionary
    """
    return {
        "tool": tool_name,
        "result": result,
        "error": error,
        "timestamp": datetime.now().isoformat(),
        "success": error is None
    }


def merge_metadata(base: Dict[str, Any], additional: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge metadata dictionaries, with additional taking precedence.

    Args:
        base: Base metadata dictionary
        additional: Additional metadata to merge

    Returns:
        Merged metadata dictionary
    """
    merged = base.copy()
    merged.update(additional)
    return merged

