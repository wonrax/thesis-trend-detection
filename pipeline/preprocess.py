if __name__ == "__main__":
    import sys

    sys.path.append(".")

from data.preprocess import Preprocess
from typing import List
from data.model.article import Article
from pipeline.logger import get_common_logger
from typing import List
from bson.objectid import ObjectId

# Set up logger
logger = get_common_logger(__name__)


class PreprocessedComment:
    """Processed comment used for machine learning tasks."""

    def __init__(self, id_source: str, content: str, replies=None):
        self.id = id_source
        self.content = content

        if replies is None:
            self.replies = []
        else:
            self.replies = replies


class PreprocessedArticle:
    """Processed article used for machine learning tasks."""

    def __init__(
        self,
        id_mongo: ObjectId,
        id_source: str,
        source: str,
        title: str,
        excerpt_segmented_tokens: List[str] = None,
        content_segmented_tokens: List[str] = None,
        comments: List[PreprocessedComment] = None,
    ) -> None:
        self.id_mongo = id_mongo
        self.id_source = id_source
        self.source = source
        self.title = title
        self.excerpt_segmented_tokens = excerpt_segmented_tokens
        self.content_segmented_tokens = content_segmented_tokens

        if comments is None:
            self.comments = []
        else:
            self.comments = comments


def preprocess_articles(articles: List[Article]):

    if not articles:
        return []

    logger.info(f"Started preprocessing {len(articles)} articles")

    stopword_list = []
    with open("data/vietnamese-stopwords-dash.txt", encoding="utf-8") as f:
        stopword_list = f.read().split("\n")

    processed_articles: List[PreprocessedArticle] = []

    # Stopword list used for excerpt to remove news source signature
    stopword_list_for_excerpt = stopword_list + ["TTO", "Dân_trí", "VnExpress"]

    logger.info(f"Segmentizing...")
    for article in articles:
        excerpt_segmented = Preprocess.segmentize(
            article["excerpt"],
            stopword_list=stopword_list_for_excerpt,
            do_sentences=False,
        )
        processed_articles.append(
            PreprocessedArticle(
                id_mongo=article.id,
                id_source=article.id_source,
                source=article.source,
                title=article.title,
                excerpt_segmented_tokens=excerpt_segmented["tokens"],
            )
        )

    # Remove unimportant words using tfidf
    logger.info(f"Removing unimportant words using tfidf...")
    from gensim.models import TfidfModel
    from gensim.corpora import Dictionary

    THRESHOLD = 0.1

    tokens = [a.excerpt_segmented_tokens for a in processed_articles]
    dct = Dictionary(tokens)  # fit dictionary
    corpus = [dct.doc2bow(line) for line in tokens]  # convert corpus to BoW format
    model = TfidfModel(corpus)  # fit model

    for index, article in enumerate(tokens):
        filtered_doc = []
        for word_index, score in enumerate(model[corpus[index]]):
            if score[1] > THRESHOLD:
                filtered_doc.append(article[word_index])
        processed_articles[index].excerpt_segmented_tokens = filtered_doc

    return processed_articles


if __name__ == "__main__":
    from pipeline.constants import DATABASE_URL
    from mongoengine import connect
    from zoneinfo import ZoneInfo
    import datetime
    import json

    assert DATABASE_URL
    connect(host=DATABASE_URL)

    end_date = datetime.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    start_date = end_date - datetime.timedelta(days=1)

    articles = Article.objects.filter(date__gte=start_date, date__lte=end_date)
    processed_articles = preprocess_articles(articles)

    with open("pipeline/tmp/preprocessed_articles.json", "w", encoding="utf-8") as f:
        json.dump(
            [a.__dict__ for a in processed_articles],
            f,
            indent=2,
            default=str,
            ensure_ascii=False,
        )