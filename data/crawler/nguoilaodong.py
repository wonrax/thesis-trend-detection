from .base import Crawler, Category, EmptyPageException
import datetime
import time
import re
import requests


class NguoiLaoDongCrawler(Crawler):

    SOURCE_NAME = "Người Lao Động"
    BASE_URL = "https://nld.com.vn"
    MAP_CATEGORY_TO_CATEGORY_ID = {
        Category.THE_GIOI: "1006",
        Category.SUC_KHOE: "1050",
        Category.THOI_SU: "1002",
        Category.VAN_HOA: "1020",
        Category.CONG_NGHE: "1317",
        Category.THE_THAO: "1026",
        Category.GIAO_DUC: "1017",
        Category.GIAI_TRI: "1588",
        Category.KINH_DOANH: "1014",
        Category.PHAP_LUAT: "1019",
    }

    def get_news_list_url(self, cursor: int = 1):
        """
        Return the URL of the newspaper indexes given the and cursor.
        """

        assert self.category_id is not None

        return self.BASE_URL + "/loadmorecategory-{}-{}.htm".format(
            self.category_id, cursor
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

            pattern = r"href=\"(\/.*?\d{8,}\.htm)\""

            urls = re.findall(pattern, html)

            if not urls:
                raise EmptyPageException

            return [self.BASE_URL + url for url in urls]
        except Exception:
            self.logger.exception(
                f"Error when crawling urls in webpage at {self.SOURCE_NAME} with url {url}."
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

        # Since this news source doesn't support query articles by date,
        # we must assume that articles of a day are contained in one single page.
        cursor = 1
        for _ in date_generator:
            index_page_url = self.get_news_list_url(cursor)

            try:
                article_urls = self.crawl_urls_in_webpage(index_page_url)
                urls += article_urls
            except EmptyPageException:
                pass

            cursor += 1

            if self.delay:
                time.sleep(self.delay)

        return list(set(urls))
