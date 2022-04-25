if __name__ == "__main__":
    import sys

    sys.path.append(".")
    from common.constants import DATABASE_URL
    from mongoengine import connect

    assert DATABASE_URL
    connect(host=DATABASE_URL)

from flask import Flask
from flask_restful import Resource, Api
from data.model.category import Category
from data.model.topic import CategoryAnalysis
import dataclasses
from dataclasses import dataclass
from typing import List
from flask_cors import CORS
from datetime import timezone


category_mappings = {}
for category in Category:
    key = str(category).split(".")[-1].lower()
    category_mappings[key] = category

app = Flask(__name__)
api = Api(app)
cors = CORS(app)


@dataclass()
class RestfulArticle:
    id: str
    thumbnailUrl: str
    title: str
    articleUrl: str
    description: str
    publishDate: str
    sourceName: str
    sourceLogoUrl: str
    positiveRate: float
    negativeRate: float
    neutralRate: float


@dataclass()
class RestfulTopic:
    articles: List[RestfulArticle]
    keywords: List[str]
    averagePositiveRate: float
    averageNegativeRate: float
    averageNeutralRate: float


@dataclass()
class RestfulCategory:
    topics: List[RestfulTopic]
    creationDate: str
    categoryName: str


class TodoSimple(Resource):
    def get(self, category):
        if category.lower() in category_mappings:
            category_analysis = (
                CategoryAnalysis.objects.filter(
                    category=str(category_mappings[category.lower()])
                )
                .order_by("-creation_date")
                .first()
            )
            topics: List[RestfulTopic] = []
            for topic in category_analysis.topics:
                articles = []
                for article in topic.articles:
                    original_article = article.original_article
                    articles.append(
                        RestfulArticle(
                            id=str(original_article.id),
                            thumbnailUrl=original_article.img_url,
                            articleUrl=original_article.url,
                            description=original_article.excerpt,
                            negativeRate=article.comments_negative_rate,
                            positiveRate=article.comments_positive_rate,
                            neutralRate=article.comments_neutral_rate,
                            publishDate=original_article.date.replace(
                                tzinfo=timezone.utc
                            ).isoformat(),
                            sourceLogoUrl=None,  # TODO: get source logo url
                            sourceName=original_article.source,
                            title=original_article.title,
                        )
                    )
                topics.append(
                    RestfulTopic(
                        articles=articles,
                        keywords=topic.keywords,
                        averagePositiveRate=topic.average_positive_rate,
                        averageNegativeRate=topic.average_negative_rate,
                        averageNeutralRate=topic.average_neutral_rate,
                    )
                )
            result = RestfulCategory(
                topics=topics,
                creationDate=category_analysis.creation_date.isoformat(),
                categoryName=category.lower(),
            )

            return dataclasses.asdict(result)


api.add_resource(TodoSimple, "/trending/category/<string:category>")

if __name__ == "__main__":

    app.run(debug=True)
