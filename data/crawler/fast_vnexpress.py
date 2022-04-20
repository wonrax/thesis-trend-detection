from crawler.fast_base import FastCrawler, Category
import datetime
import time
import re
import requests
from bs4 import BeautifulSoup
from model.article import Article
from dateutil.parser import parse


class FastVnExpressCrawler(FastCrawler):

    SOURCE_NAME = "VnExpress"
    BASE_URL = "https://vnexpress.net/"
    API_URL = "https://usi-saas.vnexpress.net/"
    MAP_CATEGORY_TO_CATEGORY_ID = {Category.SUC_KHOE: 1003750}

    def __init__(self, category: Category, do_crawl_comment: bool, delay: float):
        super().__init__(category, do_crawl_comment, delay)
        self.category_id = self.MAP_CATEGORY_TO_CATEGORY_ID[category]

    def get_news_list_url(self, date: datetime.datetime, cursor: int = 1):
        """
        Return the URL of the newspaper indexes given the date and cursor.
        """

        assert self.category_id is not None

        timestamp = int(date.timestamp())

        return (
            self.BASE_URL
            + "category/day?cateid={}&fromdate={}&todate={}&page={}".format(
                self.category_id, timestamp, timestamp, cursor
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

        try:
            html = requests.get(url, timeout=self.timeout).text
            soup = BeautifulSoup(html, "html.parser")
            news_list = soup.find(class_="list-news-subfolder")

            if news_list:
                urls = re.findall(
                    r"href=\"(https?:\/\/vnexpress.net\/.*?[0-9]{7,}\.html)\"",
                    str(news_list),
                )

                return urls

        except Exception as e:
            print(
                f"Error when crawling urls in webpage at {self.SOURCE_NAME} with url {url}: {e}"
            )

        print(f"Found 0 url in webpage at {self.SOURCE_NAME} with url {url}")
        return []

    def crawl_urls(self):
        """
        Crawl urls of today and yesterday news urls.
        Return a list of urls.
        """

        today, yesterday = self.get_datetime_today_yesterday()

        urls = []
        for date in [today, yesterday]:
            for cursor in range(2):
                index_page_url = self.get_news_list_url(date, cursor)
                article_urls = self.crawl_urls_in_webpage(index_page_url)
                urls += article_urls

                if self.delay:
                    time.sleep(self.delay)

        return list(set(urls))

    def extract_article(self, url) -> Article:
        article = super().extract_article(url)
        if not article.date:
            try:
                html = requests.get(url, timeout=self.timeout).text
                soup = BeautifulSoup(html, "html.parser")
                date = soup.find("meta", {"name": "pubdate"})
                if date:
                    article.date = parse(date["content"])
            except Exception as e:
                print(f"Error while getting date info of article with url {url}: {e}")
        return article
