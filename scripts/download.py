from transformers import AutoModel

AutoModel.from_pretrained("vinai/phobert-base", cache_dir="./phobert-base")
