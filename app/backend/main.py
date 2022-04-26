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


CATEGORY_TO_ID = {}
for category in Category:
    key = str(category).split(".")[-1].lower()
    CATEGORY_TO_ID[key] = category

CATEGORY_TO_HUMAN_READABLE = {
    "suc_khoe": "Sức khỏe",
    "moi_nhat": "Mới nhất",
    "the_gioi": "Thế giới",
    "thoi_su": "Thời sự",
    "van_hoa": "Văn hóa",
    "cong_nghe": "Công nghệ",
    "the_thao": "Thể thao",
    "giao_duc": "Giáo dục",
    "giai_tri": "Giải trí",
    "kinh_doanh": "Kinh doanh",
    "phap_luat": "Pháp luật",
}

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
    hasMoreArticles: bool


@dataclass()
class RestfulTrend:
    id: str
    topics: List[RestfulTopic]
    creationDate: str
    categoryName: str
    availableCategories: dict[str, str]  # e.g. {suc-khoe: "Sức khỏe"}


def capitalize_first_letter(string) -> str:
    return string[0].upper() + string[1:]


class Trending(Resource):
    def get(self, category):
        category = category.lower().replace("-", "_")
        if category in CATEGORY_TO_ID:
            category_analysis = (
                CategoryAnalysis.objects.filter(category=str(CATEGORY_TO_ID[category]))
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
                    if len(articles) == 5:
                        break

                keywords = [
                    capitalize_first_letter(k).replace("_", " ") for k in topic.keywords
                ]

                topics.append(
                    RestfulTopic(
                        articles=articles,
                        keywords=keywords,
                        averagePositiveRate=topic.average_positive_rate,
                        averageNegativeRate=topic.average_negative_rate,
                        averageNeutralRate=topic.average_neutral_rate,
                        hasMoreArticles=len(topic.articles) > len(articles),
                    )
                )

                if len(topics) > 35:
                    break

            categories = CategoryAnalysis.objects.distinct(field="category")
            availableCategories = {}
            for c in categories:
                c = c.split(".")[-1].lower()
                availableCategories[
                    c.replace("_", "-")
                ] = CATEGORY_TO_HUMAN_READABLE[c]

            result = RestfulTrend(
                id=str(category_analysis.id),
                topics=topics,
                creationDate=category_analysis.creation_date.isoformat(),
                categoryName=CATEGORY_TO_HUMAN_READABLE[category],
                availableCategories=availableCategories,
            )

            return dataclasses.asdict(result)


class TopicDetail(Resource):
    def get(self, id, index):
        ca = CategoryAnalysis.objects.get(id=id)
        topic = ca.topics[index]
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

        keywords = [
            capitalize_first_letter(k).replace("_", " ") for k in topic.keywords
        ]

        result = RestfulTopic(
            articles=articles,
            keywords=keywords,
            averagePositiveRate=topic.average_positive_rate,
            averageNegativeRate=topic.average_negative_rate,
            averageNeutralRate=topic.average_neutral_rate,
            hasMoreArticles=len(topic.articles) > len(articles),
        )

        return dataclasses.asdict(result)


api.add_resource(Trending, "/trending/category/<string:category>")
api.add_resource(TopicDetail, "/topic/<string:id>/<int:index>")

if __name__ == "__main__":

    app.run(debug=True)
