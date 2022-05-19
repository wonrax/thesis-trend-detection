from .base import Crawler, Category
from .base import Article
import datetime
import time
from typing import List
from urllib.parse import urlencode
import hmac
import requests
from zoneinfo import ZoneInfo


class BaoMoiCrawler(Crawler):
    """
    Crawler for BaoMoi.com
    """

    ARTICLE_PER_DAYS = 400
    SOURCE_NAME = "Báo Mới"
    BASE_URL = "https://baomoi.com"
    PATHNAME = "/api/v1/content/get/list-by-type"
    APIKEY = "kI44ARvPwaqL7v0KuDSM0rGORtdY1nnw"
    HASHKEY = "882QcNXV4tUZbvAsjmFOHqNC1LpcBRKW"
    MAP_CATEGORY_TO_CATEGORY_ID = {
        Category.THE_GIOI: "119",
        Category.SUC_KHOE: "82",
        Category.THOI_SU: "121",
        Category.VAN_HOA: "54",
        Category.CONG_NGHE: "53",
        Category.THE_THAO: "55",
        Category.GIAO_DUC: "59",
        Category.GIAI_TRI: "52",
        Category.KINH_DOANH: "45",
        Category.PHAP_LUAT: "58",
    }

    def getSig(self, pathname: str, reqParams: dict[str, str]):
        sorted_reqParams = sorted(reqParams.items(), key=lambda x: x[0])
        paramString = urlencode(sorted_reqParams).replace("&", "")
        pathname_w_params = pathname + paramString
        return hmac.new(
            self.HASHKEY.encode(), pathname_w_params.encode(), "sha256"
        ).hexdigest()

    def build_request_url(self, days: int):
        current_time_stamp = int(time.time())
        request_params: dict[str, str] = {
            "listType": "3",
            "listId": self.category_id,
            "page": "1",
            "ctime": current_time_stamp,
            "version": "0.2.48",
            "size": "400",  # limit is around 400, won't return more
        }
        request_params["sig"] = self.getSig(self.PATHNAME, request_params)
        request_params["apiKey"] = self.APIKEY

        return self.BASE_URL + self.PATHNAME + "?" + urlencode(request_params)

    def crawl_urls(self, start_date, end_date) -> "List[str]":
        days = (end_date - start_date).days
        request_url = self.build_request_url(days)
        try:
            response = requests.get(request_url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            assert data["err"] == 0
            articles: List[Article] = []
            for article in data["data"]["items"]:
                article_date = datetime.datetime.fromtimestamp(
                    article["date"], tz=ZoneInfo("Asia/Ho_Chi_Minh")
                )
                if "publisher" in article and "name" in article["publisher"]:
                    publisher: str = article["publisher"]["name"]
                    if publisher.find("Báo ") == 0:
                        publisher = publisher[4:]
                else:  # if publisher is missing
                    publisher = self.SOURCE_NAME

                articles.append(
                    Article(
                        id_source=article["id"],
                        source=publisher,
                        title=article["title"],
                        date=article_date,
                        authors=[publisher],
                        excerpt=article["description"],
                        content=article["description"],  # TODO get real content
                        url=self.BASE_URL + article["url"],
                        img_url=article["thumbL"],
                        comments=[],  # TODO
                        tags=None,
                        category=self.category.name,
                        likes=None,
                    )
                )

            self.articles = articles
            return [article.url for article in articles]
        except:
            self.logger.exception("Error when crawling BaoMoi: %s", request_url)
            return []

    def crawl_articles(self, urls: List[str]) -> "List[Article]":
        return self.articles
