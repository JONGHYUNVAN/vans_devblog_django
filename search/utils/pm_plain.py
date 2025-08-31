# utils/pm_plain.py
import re
from html import unescape
from typing import Any

_TAG = re.compile(r"<[^>]+>")

def _strip_html(s: str) -> str:
    s = unescape(s)
    s = _TAG.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()

def pm_to_text(node: Any) -> str:
    if node is None: return ""
    if isinstance(node, list):
        return " ".join(filter(None, (pm_to_text(x) for x in node)))
    if isinstance(node, dict):
        if node.get("type") == "text":
            return _strip_html(node.get("text", ""))
        content = node.get("content") or []
        text = " ".join(filter(None, (pm_to_text(c) for c in content)))
        if node.get("type") in {"paragraph","heading","blockquote","listItem","codeBlock"}:
            return (text + " ").strip()
        if node.get("type") == "hardBreak":
            return " "
        return text
    if isinstance(node, str):
        return _strip_html(node)
    return ""

def tiptap_to_plain(doc: dict, max_len: int = 20000) -> str:
    root = doc.get("content") if isinstance(doc, dict) and doc.get("type") == "doc" else doc
    plain = pm_to_text(root or [])
    plain = re.sub(r"\s+,", ",", plain)
    return (plain[:max_len].rstrip() + " …") if max_len and len(plain) > max_len else plain
