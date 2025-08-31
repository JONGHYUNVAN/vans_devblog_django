"""
Content Parsing Utilities

Provides functions to parse structured content, such as JSON from a rich text editor,
into plain text.
"""
from typing import Any, Dict, List, Union

def _extract_text_from_nodes(nodes: List[Dict[str, Any]]) -> str:
    """
    Recursively traverses a list of content nodes and extracts all text.
    """
    text_parts = []
    if not isinstance(nodes, list):
        return ""

    for node in nodes:
        if node.get("type") == "text" and "text" in node:
            text_parts.append(node.get("text", ""))
        
        if "content" in node and isinstance(node["content"], list):
            text_parts.append(_extract_text_from_nodes(node["content"]))
            
    # Join parts with space to prevent words from sticking together
    return " ".join(filter(None, text_parts))

def parse_rich_text_json(content: Union[Dict[str, Any], Any]) -> str:
    """
    Parses a structured JSON object (from a rich text editor) into a plain text string.

    Args:
        content: The JSON object, typically with a 'type: doc' and 'content' array.

    Returns:
        A plain text representation of the content, or the original content
        if it's not a recognized format.
    """
    if isinstance(content, dict) and content.get("type") == "doc" and "content" in content:
        try:
            # Start the recursive extraction and clean up whitespace
            plain_text = _extract_text_from_nodes(content["content"])
            return ' '.join(plain_text.split())
        except Exception:
            # In case of unexpected structure, return a safe value
            return "[Content could not be parsed]"

    # If it's not the expected JSON structure (e.g., already a string), return it as is.
    if isinstance(content, str):
        return content
        
    return ""
