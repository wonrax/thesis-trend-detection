import torch
from transformers import RobertaForSequenceClassification, AutoTokenizer

model = RobertaForSequenceClassification.from_pretrained("wonrax/phobert-base-vietnamese-sentiment", cache_dir="models/phobert-base-vietnamese-sentiment")

tokenizer = AutoTokenizer.from_pretrained("wonrax/phobert-base-vietnamese-sentiment", use_fast=False, cache_dir="models/phobert-base-vietnamese-sentiment")

# Just like PhoBERT: INPUT TEXT MUST BE ALREADY WORD-SEGMENTED!
sentence = 'Đây là mô_hình rất hay , phù_hợp với điều_kiện và như cầu của nhiều người .'  

input_ids = torch.tensor([tokenizer.encode(sentence)])

with torch.no_grad():
    out = model(input_ids)
    print(out.logits.softmax(dim=-1).tolist())
    # Output:
    # [[0.002, 0.988, 0.01]]
    #     ^      ^      ^
    #    NEG    POS    NEU