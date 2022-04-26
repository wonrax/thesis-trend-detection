from .base import Crawler, Category, EmptyPageException
import datetime
import time
import re
import requests


class ZingNewsCrawler(Crawler):

    SOURCE_NAME = "Zing News"
    BASE_URL = "https://zingnews.vn/"
    MAP_CATEGORY_TO_CATEGORY_ID = {
        Category.THE_GIOI: "the-gioi",
        Category.SUC_KHOE: "suc-khoe",
        Category.THOI_SU: "thoi-su",
        Category.VAN_HOA: "du-lich",
        Category.CONG_NGHE: "cong-nghe",
        Category.THE_THAO: "the-thao",
        Category.GIAO_DUC: "giao-duc",
        Category.GIAI_TRI: "giai-tri",
        Category.KINH_DOANH: "kinh-doanh-tai-chinh",
        Category.PHAP_LUAT: "phap-luat",
    }

    def get_news_list_url(self, cursor: int = 1):
        """
        Return the URL of the newspaper indexes given the and cursor.
        """

        assert self.category_id is not None

        return self.BASE_URL + "/{}/trang{}.html".format(self.category_id, cursor)

    def get_id_by_url(self, url):
        match = re.search(r"\/.*?post(\d{7,})\.html", url)
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

            pattern = r"href=\"(\/.*?post\d{7,}\.html)\""

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
