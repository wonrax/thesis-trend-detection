from .base import Crawler, Category
import datetime
import time
import re
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse


class VietnamnetCrawler(Crawler):

    SOURCE_NAME = "Vietnamnet"
    BASE_URL = "https://vietnamnet.vn"
    MAP_CATEGORY_TO_CATEGORY_ID = {
        Category.THE_GIOI: "000005",
        Category.THOI_SU: "000002",
        Category.SUC_KHOE: "00000W",
        Category.VAN_HOA: "000007",
        Category.CONG_NGHE: "00000Q",
        Category.THE_THAO: "000009",
        Category.GIAO_DUC: "000006",
        Category.KINH_DOANH: "000003",
        Category.GIAI_TRI: "000004",
        Category.PHAP_LUAT: "000008",
    }

    def get_news_list_url(
        self,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        cursor: int = 0,  # This news source index starts from 0
    ):
        """
        Return the URL of the newspaper indexes given the date and cursor.
        """

        assert self.category_id is not None

        date_format = "%d/%m/%Y"
        start_date_formatted = start_date.strftime(date_format)
        end_date_formatted = end_date.strftime(date_format)

        return (
            self.BASE_URL
            + "/tin-tuc-24h-p{}?bydate={}-{}&bydaterang=1&cate={}".format(
                cursor, start_date_formatted, end_date_formatted, self.category_id
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
            main_content = soup.select_one(".container.main-content")

            # Check if there is a next page
            pagination = main_content.select_one(".panination__content")
            if pagination:
                for button in pagination.find_all("a"):
                    if button.has_attr("class") and "pre" in button["class"]:
                        # Ignore the "previous page" button
                        continue
                    if button.find("img"):
                        # Found the "next page" button
                        next_page_url = button["href"]
                        break

            if main_content:
                urls = re.findall(
                    r"href=\"(http.*?\d{7,}\.html)\"",
                    str(main_content),
                )

                return urls, next_page_url

        except Exception:
            self.logger.exception(
                f"Error when crawling urls in webpage at {self.SOURCE_NAME} with url {url}."
            )

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

        urls = []

        index_page_url = self.get_news_list_url(start_date, end_date)
        article_urls, next_page_url = self.crawl_urls_in_webpage(index_page_url)
        urls += article_urls

        while next_page_url:
            article_urls, next_page_url = self.crawl_urls_in_webpage(next_page_url)
            urls += article_urls

            if self.delay:
                time.sleep(self.delay)

        return list(set(urls))

    def extract_article(self, url):
        article = super().extract_article(url)
        if article and not article.date:
            try:
                html = requests.get(url, timeout=self.timeout).text

                # regex match "datePublished": "2022-04-19T17:55:00.000 +07:00"
                match = re.search(r"\"datePublished\":\s?\"(.*?)\"", html)

                if match:
                    article.date = parse(match.group(1))

            except Exception:
                self.logger.exception(
                    f"Error while getting date info of article with url {url}."
                )
        return article
