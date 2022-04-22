from .base import Crawler, Category, EmptyPageException
import datetime
import time
import re
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse


class DanTriCrawler(Crawler):

    SOURCE_NAME = "Dân Trí"
    BASE_URL = "https://dantri.com.vn"
    MAP_CATEGORY_TO_CATEGORY_ID = {
        Category.MOI_NHAT: "su-kien",
        Category.THE_GIOI: "the-gioi",
        Category.THOI_SU: "xa-hoi",
        Category.SUC_KHOE: "suc-khoe",
        Category.VAN_HOA: "van-hoa",
        Category.CONG_NGHE: "suc-manh-so",
        Category.THE_THAO: "the-thao",
        Category.GIAO_DUC: "giao-duc-huong-nghiep",
        Category.GIAI_TRI: "giai-tri",
        Category.KINH_DOANH: "kinh-doanh",
    }

    def get_news_list_url(self, cursor: int = 1):
        """
        Return the URL of the newspaper indexes given the and cursor.
        """

        assert self.category_id is not None

        return self.BASE_URL + "/{}/trang-{}.htm".format(self.category_id, cursor)

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
            soup = BeautifulSoup(html, "html.parser")

            highlight_section = soup.select_one(".article.highlight")
            news_list_section = soup.select_one(".article.article-three.large")

            pattern = r"href=\"(\/.*?[0-9]{8,}\.htm)\""

            urls = []
            for section in [highlight_section, news_list_section]:
                if section:
                    urls += re.findall(pattern, str(section))

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

    def extract_article(self, url):
        article = super().extract_article(url)
        if article and not article.date:
            try:
                html = requests.get(url, timeout=self.timeout).text

                # regex match "datePublished":"2022-04-20T11:15:43+07:00"
                match = re.search(r"\"datePublished\":\"(.*?)\"", html)

                if match:
                    article.date = parse(match.group(1))

            except Exception as e:
                print(f"Error while getting date info of article with url {url}: {e}")
        return article
