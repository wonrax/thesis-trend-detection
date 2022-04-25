from mongoengine import *
from data.model.article import Article, Comment
from datetime import datetime


class CommentAnalysis(EmbeddedDocument):
    """Document that contains analysis on a comment."""

    comment_id = ObjectIdField(required=True, unique=True)
    id_source = StringField(required=True, null=False)
    sentiment = IntField(null=True, choices=(-1, 0, 1))  # NEG, NEU, POS
    replies = ListField(ReferenceField("self"), null=True)


class ArticleAnalysis(EmbeddedDocument):
    """Document that contains analysis on an article."""

    original_article = ReferenceField(Article, required=True, null=False)
    id_source = StringField(required=True, unique_with="source")
    source = StringField(required=True)
    comments_negative_rate = FloatField(null=True)
    comments_positive_rate = FloatField(null=True)
    comments_neutral_rate = FloatField(null=True)
    keywords = ListField(StringField(), null=True)
    comments = ListField(EmbeddedDocumentField(Comment), null=True)


class TopicAnalysis(EmbeddedDocument):
    """Document that contains analysis on a topic."""

    articles = ListField(EmbeddedDocumentField(ArticleAnalysis), required=True)
    keywords = ListField(StringField(), null=True)
    average_negative_rate = FloatField(null=True)
    average_positive_rate = FloatField(null=True)
    average_neutral_rate = FloatField(null=True)


class CategoryAnalysis(Document):
    """Document that contains analysed topics of a category (e.g. SUC_KHOE, PHAP_LUAT)."""

    topics = ListField(EmbeddedDocumentField(TopicAnalysis), required=True)
    category = StringField(required=True, null=False)
    creation_date = DateTimeField(required=True, default=datetime.utcnow)
