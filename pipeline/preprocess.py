from data.preprocess import Preprocess
from data.model.article import Article
from typing import List
from logger import get_common_logger
from typing import List
from bson.objectid import ObjectId

# Set up logger
logger = get_common_logger()


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
        excerpt_segmented_sentences: str = None,
        content_segmented_tokens: List[str] = None,
        content_segmented_sentences: str = None,
        comments: List[PreprocessedComment] = None,
    ) -> None:
        self.id_mongo = id_mongo
        self.id_source = id_source
        self.source = source
        self.title = title
        self.excerpt_segmented_tokens = excerpt_segmented_tokens
        self.excerpt_segmented_sentences = excerpt_segmented_sentences
        self.content_segmented_tokens = content_segmented_tokens
        self.content_segmented_sentences = content_segmented_sentences

        if comments is None:
            self.comments = []
        else:
            self.comments = comments


def tfidf_filter(tokenized_docs: List[List[str]], threshold: float = 0.1):
    from gensim.models import TfidfModel
    from gensim.corpora import Dictionary

    dct = Dictionary(tokenized_docs)  # fit dictionary
    corpus = [
        dct.doc2bow(line) for line in tokenized_docs
    ]  # convert corpus to BoW format
    model = TfidfModel(corpus)  # fit model

    filtered_docs = []
    for index, article in enumerate(tokenized_docs):
        filtered_doc = []
        for word_index, score in enumerate(model[corpus[index]]):
            if score[1] > threshold:
                filtered_doc.append(article[word_index])
        filtered_docs.append(filtered_doc)

    return filtered_docs


def preprocess_articles(articles: List[Article]):

    if not articles:
        return []

    logger.info(f"Started preprocessing {len(articles)} articles")

    stopword_list = []
    with open("data/vietnamese-stopwords-dash.txt", encoding="utf-8") as f:
        stopword_list = f.read().split("\n")

    processed_articles: List[PreprocessedArticle] = []

    # Stopword list used for excerpt to remove news source signature
    source_signatures = ["tto", "dân_trí", "vnexpress", "nlđo"]
    stopword_list_for_excerpt = stopword_list + source_signatures

    logger.info(f"Segmentizing...")
    for article in articles:
        excerpt_segmented = Preprocess.segmentize(
            article.excerpt,
            do_tokens=True,
            stopword_list=stopword_list_for_excerpt,
        )
        content_segmented = Preprocess.segmentize(
            article.content,
            stopword_list=stopword_list_for_excerpt,
            do_sentences=True,
        )
        processed_articles.append(
            PreprocessedArticle(
                id_mongo=article.id,
                id_source=article.id_source,
                source=article.source,
                title=article.title,
                excerpt_segmented_tokens=excerpt_segmented["tokens"],
                # excerpt_segmented_sentences=excerpt_segmented_sentences,
                content_segmented_sentences=content_segmented["sentences"],
                # content_segmented_tokens=content_segmented["tokens"],
            )
        )

    # Remove unimportant words using tfidf
    # logger.info(f"Removing unimportant words using tfidf...")
    # THRESHOLD = 0.05
    # tokenized_excerpts = [a.excerpt_segmented_tokens for a in processed_articles]
    # lower
    # tokenized_excerpts = [[word.lower() for word in line] for line in tokenized_excerpts]
    # filtered_excerpts = tfidf_filter(tokenized_excerpts, threshold=THRESHOLD)

    # logger.debug(f"Before TF-IDF: {tokenized_excerpts[:10]}")

    # for index, filtered_text in enumerate(filtered_excerpts):
    #     processed_articles[index].excerpt_segmented_tokens = filtered_text

    # logger.debug(f"After TF-IDF: {filtered_excerpts[:10]}")

    return processed_articles


# For testing purpose
def main():
    from common.constants import DATABASE_URL
    from mongoengine import connect
    from zoneinfo import ZoneInfo
    from data.model.category import Category
    import datetime
    import json

    assert DATABASE_URL
    connect(host=DATABASE_URL)

    end_date = datetime.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    start_date = end_date - datetime.timedelta(days=1.5)

    categories = [Category.SUC_KHOE]
    categories = [c for c in Category]
    categories.remove(Category.MOI_NHAT)

    articles = []
    for category in categories:
        articles += Article.objects.filter(
            category=str(category), date__gte=start_date, date__lte=end_date
        )

    processed_articles = preprocess_articles(articles)

    with open("pipeline/tmp/preprocessed_articles.json", "w", encoding="utf-8") as f:
        json.dump(
            [a.__dict__ for a in processed_articles],
            f,
            indent=2,
            default=str,
            ensure_ascii=False,
        )

    trend_category = Category.MOI_NHAT if len(categories) > 1 else categories[0]

    return processed_articles, trend_category


if __name__ == "__main__":
    main()
