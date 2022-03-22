if __name__ == "__main__":
    import os, sys
    ROOT_DIR = os.path.abspath(os.curdir)
    sys.path.append(ROOT_DIR + "/data")

from crawler.base import Crawler, Category
from bs4 import BeautifulSoup
import requests
import time
class VnExpressCrawler(Crawler):

    BASE_URL = "https://vnexpress.net/"
    API_URL = "https://id.tuoitre.vn/api"
    LIKE_COUNT_URL = "https://s5.tuoitre.vn/count-object.htm"
    SOURCE_NAME = "VnExpress"
    MAP_CATEGORY_TO_CATEGORY_ID = {
        Category.SUC_KHOE: 1003750
    }


    def __init__(
        self,
        category: Category,
        crawl_comment=True,
        delay=0.5,
        skip_these=None,
        newer_only=False,
        telegram_key=None,
    ):
        super().__init__(
            category,
            crawl_comment,
            delay,
            skip_these,
            newer_only,
            telegram_key,
        )
        self.category_id = self.MAP_CATEGORY_TO_CATEGORY_ID[self.category]

    def get_id_from_url(self, url: str):
        """
        Return the article ID given the URL.
        """

        return url.split(".")[-2].split("/")[-1].split("-")[-1]

    def get_news_list_url(self, time: int, index: int):
        """
        Return the url of the page containing a list of articles
        in a day given the time and the index.
        """

        assert self.category_id is not None

        return self.BASE_URL + "category/day?cateid={}&fromdate={}&todate={}&page={}".format(
            self.category_id, time, time, index
        )

    def find_article_urls(self, url: str, limit=float("inf")):
        """
        Find articles in a page given its URL.
        Return a set of URLs to the main articles.
        """
        
        try:
            response = requests.get(url, timeout=self.timeout)
        except:
            return set(), False
    
        article_urls = set()

        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.select("article.item-news.item-news-common")
        for article in articles:
            if len(article_urls) >= limit:
                break
            try:
                url = article.select_one(".title-news").select_one("a").get("href")
                if (self.SOURCE_NAME, self.get_id_from_url(url)) not in self.skip_these:
                    article_urls.add(url)
            except:
                pass
        
        return article_urls
    
    def crawl_articles(limit=float("inf")):
        pass

if __name__ == "__main__":

    crawler = VnExpressCrawler(Category.SUC_KHOE)
    url = crawler.get_news_list_url(int(time.time()), 1)
    a_urls = crawler.find_article_urls(url)
    print(a_urls)