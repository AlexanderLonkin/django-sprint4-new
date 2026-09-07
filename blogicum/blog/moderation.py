from functools import lru_cache

import torch

from core.constants import TOXICITY_THRESHOLD

MODEL_NAME = 'cointegrated/rubert-tiny-toxicity'


@lru_cache(maxsize=1)
def _get_model_components():
    """Лениво загрузить и закешировать токенизатор и модель."""
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()
    return tokenizer, model


def get_toxicity_score(text):
    """Вернуть оценку токсичности текста от нуля до единицы."""
    tokenizer, model = _get_model_components()
    inputs = tokenizer(
        text,
        return_tensors='pt',
        truncation=True,
        padding=True,
    )
    with torch.inference_mode():
        logits = model(**inputs).logits
        probabilities = torch.sigmoid(logits)[0]
    return (1 - probabilities[0]).item()


def is_toxic(text):
    """Определить, превышает ли токсичность допустимый порог."""
    return get_toxicity_score(text) >= TOXICITY_THRESHOLD
