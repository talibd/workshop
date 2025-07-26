import spacy
from collections import Counter
from typing import List


def extract_keywords(text: str, n: int = 5) -> List[str]:
    """Return the top `n` keywords (nouns and verbs) from the given text."""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    tokens = [
        token.lemma_.lower()
        for token in doc
        if token.pos_ in ("NOUN", "VERB") and not token.is_stop and token.is_alpha
    ]
    counts = Counter(tokens)
    return [word for word, _ in counts.most_common(n)]
