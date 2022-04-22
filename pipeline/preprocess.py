# add python root folder to os path
import sys

sys.path.append(r".")


from data.preprocess import Preprocess
from typing import List
import json

articles: List[dict] = []
with open("pipeline/tmp/articles.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

assert articles

stopword_list = []
with open("data/vietnamese-stopwords-dash.txt", encoding="utf-8") as f:
    stopword_list = f.read().split("\n")


class PreprocessedArticle:
    def __init__(
        self,
        id: str,
        source: str,
        title: str,
        title_segmented_tokens: List[str],
        excerpt_segmented_tokens: List[str] = None,
        excerpt_segmented_sentences: str = None,
        content_segmented_tokens: List[str] = None,
        content_segmented_sentences: str = None,
    ) -> None:
        self.id = id
        self.source = source
        self.title = title
        self.title_segmented_tokens = title_segmented_tokens
        self.excerpt_segmented_tokens = excerpt_segmented_tokens
        self.excerpt_segmented_sentences = excerpt_segmented_sentences
        self.content_segmented_tokens = content_segmented_tokens
        self.content_segmented_sentences = content_segmented_sentences


processed_articles = []

# Stopword list used for excerpt to remove news source signature
stopword_list_for_excerpt = stopword_list + ["TTO", "Dân_trí", "VnExpress"]

for article in articles:
    excerpt_segmented = Preprocess.segmentize(
        article["excerpt"], stopword_list=stopword_list_for_excerpt
    )
    content_segmented = Preprocess.segmentize(
        article["content"], stopword_list=stopword_list
    )
    title_segmented = Preprocess.segmentize(
        article["title"], do_sentences=False, stopword_list=stopword_list
    )
    processed_articles.append(
        PreprocessedArticle(
            article["id"],
            article["source"],
            article["title"],
            title_segmented["tokens"],
            excerpt_segmented["tokens"],
            excerpt_segmented["sentences"],
            content_segmented["tokens"],
            content_segmented["sentences"],
        )
    )

# dump processed_articles to json
with open("pipeline/tmp/preprocessed_articles.json", "w", encoding="utf-8") as f:
    json.dump(
        [a.__dict__ for a in processed_articles],
        f,
        indent=2,
        default=str,
        ensure_ascii=False,
    )
