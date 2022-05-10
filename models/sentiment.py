import torch
from transformers import RobertaForSequenceClassification, AutoTokenizer
from enum import Enum
import torch


class Sentiment(Enum):
    NEGATIVE = 0
    POSITIVE = 1
    NEUTRAL = 2
    UNSURE = 4


model = None
tokenizer = None

ID2SENTIMENT = {
    0: Sentiment.NEGATIVE,
    1: Sentiment.POSITIVE,
    2: Sentiment.NEUTRAL,
}


def get_sentiment(sentence: str, threshold = 0.9) -> Sentiment:
    global model
    global tokenizer

    if not model:
        model = RobertaForSequenceClassification.from_pretrained(
            "wonrax/phobert-base-vietnamese-sentiment",
            cache_dir="models/phobert-base-vietnamese-sentiment",
        )
    if not tokenizer:
        tokenizer = AutoTokenizer.from_pretrained(
            "wonrax/phobert-base-vietnamese-sentiment",
            use_fast=False,
            cache_dir="models/phobert-base-vietnamese-sentiment",
        )

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    model.to(device)

    input_ids = torch.tensor([tokenizer.encode(sentence, max_length=256)])
    input_ids = input_ids.to(device)

    with torch.no_grad():
        out = model(input_ids)
        probabilities = out.logits.softmax(dim=-1)
        max_index = torch.argmax(probabilities, dim=-1)[0]
        if probabilities[0][max_index] > threshold:
            return ID2SENTIMENT[int(max_index)]
        else:
            return Sentiment.UNSURE


# For testing
def main():
    sentence = (
        "Đây là mô_hình rất hay , phù_hợp với điều_kiện và như cầu của nhiều người ."
    )
    print(get_sentiment(sentence))


if __name__ == "__main__":
    main()
