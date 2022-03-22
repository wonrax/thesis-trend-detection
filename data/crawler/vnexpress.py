if __name__ == "__main__":
    import os, sys
    ROOT_DIR = os.path.abspath(os.curdir)
    sys.path.append(ROOT_DIR + "/data")

from crawler.base import Crawler, Category
from bs4 import BeautifulSoup
import requests
import time

class EmptyPageException(Exception):
    """
    Exception raised when the news page is empty, indicating we have reached
    the end of the database.
    """
    pass
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
        in a day given the time of that day and the index.
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
            return set()
    
        article_urls = set()

        soup = BeautifulSoup(response.text, "html.parser")

        articles = soup.select("article.item-news.item-news-common")
        if len(articles) == 0:
            raise EmptyPageException

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

    def crawl_article_urls(self, limit=15):
        """
        Try to find as many articles as possible given the limit.
        Return a set of article URLs.
        """
        article_urls = set()
        
        target_date = int(time.time())
        date_step = 86400 # 1 day
        
        # Assuming the first page contains all the articles in that day
        only_crawl_first_page = True
        
        while len(article_urls) < limit:
            index = 1
            try:
                while True:
                        url = self.get_news_list_url(target_date, index)
                        print("Crawling {}".format(url))
                        a_urls = self.find_article_urls(url, limit - len(article_urls))
                        print("Found {} articles".format(len(a_urls)))
                        
                        if len(a_urls) == 0: # End of the page
                            break
                        else:
                            article_urls.update(a_urls)
                            index += 1

                        if len(article_urls) < limit:
                            time.sleep(self.delay)

                        if only_crawl_first_page:
                            break

            except EmptyPageException:
                # We didn't get anything even on page 1, indicating
                # we've reached the end of the database
                if index == 1:
                    break
                time.sleep(self.delay)

            target_date -= date_step
        
        return article_urls

    
    def crawl_articles(limit=float("inf")):
        pass

if __name__ == "__main__":

    crawler = VnExpressCrawler(Category.SUC_KHOE, delay=10)
    a_urls = crawler.crawl_article_urls(limit=50)
    print(a_urls)
    print("len ", len(a_urls))