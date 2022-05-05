from .base import Crawler, Category, EmptyPageException
from ..model.article import Comment
import datetime
import time
import re
import requests
import json
from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo


class TuoiTreCrawler(Crawler):

    SOURCE_NAME = "Tuổi Trẻ"
    BASE_URL = "https://tuoitre.vn"
    API_URL = "https://id.tuoitre.vn/api"
    LIKE_COUNT_URL = "https://s5.tuoitre.vn/count-object.htm"
    MAP_CATEGORY_TO_CATEGORY_ID = {
        Category.MOI_NHAT: 0,
        Category.THE_GIOI: 2,
        Category.THOI_SU: 3,
        Category.SUC_KHOE: 12,
        Category.VAN_HOA: 200017,
        Category.CONG_NGHE: 200029,
        Category.THE_THAO: 1209,
        Category.GIAO_DUC: 13,
        Category.GIAI_TRI: 10,
        Category.KINH_DOANH: 11,
        Category.PHAP_LUAT: 6,
    }

    def get_news_list_url(self, date: datetime.datetime, cursor: int = 1):
        """
        Return the URL of the newspaper indexes given the date and cursor.
        """

        assert self.category_id is not None

        return self.BASE_URL + "/timeline-xem-theo-ngay/{}/{}/trang-{}.htm".format(
            self.category_id, date.strftime("%d-%m-%Y"), cursor
        )

    def get_id_by_url(self, url):
        match = re.search(r"\/.*?(\d{8,})\.htm", url)
        if match:
            return match.group(1)
        else:
            return None

    def crawl_urls_in_webpage(self, url: str):
        """
        Extract all urls in the webpage given its url.
        Return a list of article urls.
        """
        try:
            html = requests.get(url, timeout=self.timeout).text
            urls = re.findall(r"href=\"(\/.*?[0-9]{8,}\.htm)\"", html)

            if not urls:
                raise EmptyPageException

            return [self.BASE_URL + url for url in urls]
        except EmptyPageException:
            # Forward the exception to caller
            raise EmptyPageException
        except Exception:
            self.logger.exception(
                f"Error when crawling urls in webpage at {self.SOURCE_NAME} with url {url}."
            )

        return []

    def crawl_urls(
        self, start_date: datetime.datetime = None, end_date: datetime.datetime = None
    ):
        """
        Crawl urls of the news category.
        Return a list of urls.
        """

        if start_date is None or end_date is None:
            start_date, end_date = self.get_datetime_today_yesterday()

        date_generator = self.date_generator_from_range(start_date, end_date)
        urls = []

        for date in date_generator:
            cursor = 1
            while True:
                index_page_url = self.get_news_list_url(date, cursor)

                try:
                    article_urls = self.crawl_urls_in_webpage(index_page_url)
                    urls += article_urls
                except EmptyPageException:
                    break

                cursor += 1

                if self.delay:
                    time.sleep(self.delay)

        return list(set(urls))

    def json_to_comment(self, json_comment: dict):
        """
        Convert a JSON comment to a Comment object.
        """

        id = json_comment["id"]
        author = json_comment["sender_fullname"]
        content = BeautifulSoup(json_comment["content"], "html.parser").text
        likes = int(json_comment["likes"])

        # E.g. 2021-11-12T09:32:32
        str_date = json_comment["created_date"]
        date = datetime.datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%S").astimezone(
            ZoneInfo("Asia/Ho_Chi_Minh")
        )

        replies = []
        if json_comment["child_comments"] is not None:
            replies = [
                self.json_to_comment(reply) for reply in json_comment["child_comments"]
            ]

        return Comment(
            id_source=id,
            author=author,
            content=content,
            date=date,
            replies=replies,
            likes=likes,
        )

    def extract_comments(self, url: str, cursor=1, limit=200):
        """
        Get comments of an article given its ID.
        Return a set of Comment objects.
        """

        id = self.get_id_by_url(url)
        api_url = self.API_URL + "/getlist-comment.api?"

        url = api_url + "objId={}&pageindex={}&pagesize={}&objType=1&sort=1".format(
            id, cursor, limit
        )

        try:
            response = requests.get(url)
            response_json = response.json()

            assert response_json["Success"] == True

            data = json.loads(response_json["Data"])

            comments = []

            for comment in data:
                comments.append(self.json_to_comment(comment))

            return comments

        except Exception:
            self.logger.exception(f"Error when extracting comments from {url}.")

        return []
