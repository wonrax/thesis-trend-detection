from crawler.fast_base import FastCrawler, Category, EmptyPageException
import datetime
import time
import re
import requests
from bs4 import BeautifulSoup


class FastTuoiTreCrawler(FastCrawler):

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
    }

    def __init__(self, category: Category, do_crawl_comment: bool, delay: float):
        super().__init__(category, do_crawl_comment, delay)
        self.category_id = self.MAP_CATEGORY_TO_CATEGORY_ID[category]

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
        except Exception as e:
            print(
                f"Error when crawling urls in webpage at {self.SOURCE_NAME} with url {url}: {e}"
            )

        raise EmptyPageException

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
