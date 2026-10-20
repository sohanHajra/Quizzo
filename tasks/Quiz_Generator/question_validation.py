"""Validate model-generated quiz questions without importing cloud dependencies."""

import json
import re
from collections.abc import Mapping

_KEYS = ("A", "B", "C", "D")


def parse_question(raw: str) -> dict:
    """Parse a strict question schema; reject malformed structures."""
    if not isinstance(raw, str):
        raise ValueError("The model response must be text.")
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE).strip()
    try:
        question = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("The model returned invalid JSON.") from exc
    if not isinstance(question, Mapping):
        raise ValueError("Expected one JSON object.")
    if not isinstance(question.get("question"), str) or not question["question"].strip():
        raise ValueError("Missing question text.")
    choices = question.get("choices")
    if not isinstance(choices, list) or len(choices) != 4:
        raise ValueError("Expected four answer choices.")
    keys = []
    for choice in choices:
        if not isinstance(choice, Mapping) or not isinstance(choice.get("value"), str) or not choice["value"].strip():
            raise ValueError("Each choice must contain a nonempty value.")
        keys.append(choice.get("key"))
    if tuple(keys) != _KEYS:
        raise ValueError("Answer choices must be labeled A through D in order.")
    if question.get("answer") not in _KEYS:
        raise ValueError("Answer must refer to one of the four choices.")
    if not isinstance(question.get("explanation"), str) or not question["explanation"].strip():
        raise ValueError("Missing explanation.")
    return {
        "question": question["question"].strip(),
        "choices": [{"key": c["key"], "value": c["value"].strip()} for c in choices],
        "answer": question["answer"],
        "explanation": question["explanation"].strip(),
    }


def _trigrams(text: str) -> set[tuple[str, ...]]:
    tokens = re.findall(r"\b\w+\b", text.casefold())
    if len(tokens) < 3:
        return {tuple(tokens)} if tokens else set()
    return {tuple(tokens[i:i + 3]) for i in range(len(tokens) - 2)}


def is_distinct(candidate: str, existing: list[str], *, max_similarity: float = 0.60) -> bool:
    """Filter near-duplicate wording using token-trigram Jaccard similarity."""
    normalized = " ".join(candidate.casefold().split())
    new = _trigrams(candidate)
    if not new:
        return False
    for previous in existing:
        if normalized == " ".join(previous.casefold().split()):
            return False
        old = _trigrams(previous)
        overlap = len(new & old) / len(new | old) if old else 0.0
        if overlap >= max_similarity:
            return False
    return True
