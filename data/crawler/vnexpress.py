from .base import Crawler, Category
import datetime
import time
import re
import requests
from bs4 import BeautifulSoup
from ..model.article import Article
from dateutil.parser import parse


class VnExpressCrawler(Crawler):

    SOURCE_NAME = "VnExpress"
    BASE_URL = "https://vnexpress.net"
    API_URL = "https://usi-saas.vnexpress.net"
    MAP_CATEGORY_TO_CATEGORY_ID = {
        Category.SUC_KHOE: 1003750,
        Category.THE_GIOI: 1001002,
        Category.THOI_SU: 1001005,
        Category.CONG_NGHE: 1002592,
        Category.THE_THAO: 1002565,
        Category.GIAO_DUC: 1003497,
        Category.GIAI_TRI: 1002691,
        Category.KINH_DOANH: 1003159,
        Category.PHAP_LUAT: 1001007,
    }
    MAP_CATEGORY_TO_CATEGORY = {
        Category.SUC_KHOE: "suc-khoe",
        Category.THE_GIOI: "the-gioi",
        Category.THOI_SU: "thoi-su",
        Category.CONG_NGHE: "so-hoa",
        Category.THE_THAO: "the-thao",
        Category.GIAO_DUC: "giao-duc",
        Category.GIAI_TRI: "giai-tri",
        Category.KINH_DOANH: "kinh-doanh",
        Category.PHAP_LUAT: "phap-luat",
    }

    def get_news_list_url(
        self,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        cursor: int = 1,
    ):
        """
        Return the URL of the newspaper indexes given the date and cursor.
        """

        assert self.category_id is not None

        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())

        return (
            self.BASE_URL
            + "/category/day?cateid={}&fromdate={}&todate={}&page={}".format(
                self.category_id, start_timestamp, end_timestamp, cursor
            )
        )

    def get_id_by_url(self, url):
        match = re.search(r"\/.*?(\d{7,})\.html", url)
        if match:
            return match.group(1)
        else:
            return None

    def crawl_urls_in_webpage(self, url: str):
        """
        Extract all urls in the webpage given its url.
        Return a list of article urls.
        """

        next_page_url = None

        try:
            html = requests.get(url, timeout=self.timeout).text
            soup = BeautifulSoup(html, "html.parser")
            news_list = soup.find(class_="list-news-subfolder")

            next_page_button = soup.select_one(".btn-page.next-page")
            if next_page_button and "disable" not in next_page_button["class"]:
                next_page_url = self.BASE_URL + next_page_button["href"]

            if news_list:
                urls = re.findall(
                    r"href=\"(https?:\/\/vnexpress.net\/.*?[0-9]{7,}\.html)\"",
                    str(news_list),
                )

                return urls, next_page_url

        except Exception:
            self.logger.exception(
                f"Error when crawling urls in webpage at {self.SOURCE_NAME} with url {url}."
            )

        print(f"Found 0 url in webpage at {self.SOURCE_NAME} with url {url}")
        return [], next_page_url

    def crawl_urls(
        self, start_date: datetime.datetime = None, end_date: datetime.datetime = None
    ):
        """
        Crawl urls of the news category.
        Return a list of urls.
        """

        if start_date is None or end_date is None:
            start_date, end_date = self.get_datetime_today_yesterday()

        if True:  # Temporarily fix for VnExpress not returning articles
            category_str = self.MAP_CATEGORY_TO_CATEGORY[self.category]
            index_url_base = "https://vnexpress.net/{}-p{}"
            days = (end_date - start_date).days + 1
            urls = []
            for i in range(days):
                index_url = index_url_base.format(category_str, i + 1)
                html = requests.get(index_url, timeout=self.timeout).text
                urls += re.findall(
                    r"href=\"(https?:\/\/vnexpress.net\/[^\/\.]*?\d{7,}\.html)\"",
                    html,
                )
            return list(set(urls))

        urls = []

        index_page_url = self.get_news_list_url(start_date, end_date, 1)
        article_urls, next_page_url = self.crawl_urls_in_webpage(index_page_url)
        urls += article_urls

        while next_page_url:
            article_urls, next_page_url = self.crawl_urls_in_webpage(next_page_url)
            urls += article_urls

            if self.delay:
                time.sleep(self.delay)

        return list(set(urls))

    def extract_article(self, url) -> Article:
        article = super().extract_article(url)
        if article and not article.date:
            try:
                html = requests.get(url, timeout=self.timeout).text
                soup = BeautifulSoup(html, "html.parser")
                date = soup.find("meta", {"name": "pubdate"})
                if date:
                    article.date = parse(date["content"])
            except Exception:
                self.logger.exception(
                    f"Error while getting date info of article with url {url}."
                )
        return article
