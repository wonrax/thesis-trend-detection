if __name__ == "__main__":
    import os, sys
    ROOT_DIR = os.path.abspath(os.curdir)
    sys.path.append(ROOT_DIR + "/data")

from crawler.base import Crawler, Category
from model.article import Article, Comment
from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime
from functools import reduce
import unicodedata
import json
from queue import Queue, Empty
import threading
from util import telegram

class EmptyPageException(Exception):
    """
    Exception raised when the news page is empty, indicating we have reached
    the end of the database.
    """
    pass
class VnExpressCrawler(Crawler):

    BASE_URL = "https://vnexpress.net/"
    API_URL = "https://usi-saas.vnexpress.net/"
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
    
    def get_comments_endpoint(self, article_id: str):
        """
        Return the API endpoint to get comments of the given the article id.
        """
        return self.API_URL + \
            "index/get?offset=0&limit=200&sort=like&objectid={}&objecttype=1&siteid=1003750" \
                .format(article_id)

    def get_reply_endpoint(self, comment_id: str):
        """
        Return the API endpoint to get replies of the given the comment id.
        """
        return self.API_URL + \
            "index/getreplay?id={}&limit=1000&offset=0&sort_by=like" \
                .format(comment_id)

    def get_news_list_url(self, time: int, index: int):
        """
        Return the url of the page containing a list of articles
        in a day given the time of that day and the index.
        """

        assert self.category_id is not None

        return self.BASE_URL + "category/day?cateid={}&fromdate={}&todate={}&page={}".format(
            self.category_id, time, time, index
        )

    def normalize_unicode(self, unicode_str):
        """
        Normalize unicode string (e.g. remove \xa0 characters).
        """
        return unicodedata.normalize("NFKC", unicode_str)

    def find_article_urls(self, url: str, limit=float("inf")):
        """
        Find articles in a page given its URL.
        Return a set of URLs to the main articles.
        """
        
        try:
            response = requests.get(url, timeout=self.timeout)
        except Exception as e:
            print("Error while crawling {}: {}".format(url, e))
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
    
    def crawl_replies(self, id: str):
        """
        Crawl replies of the given comment ID.
        Return a list of replies.
        """
        url = self.get_reply_endpoint(id)
        time.sleep(min(self.delay, 1))
        try:
            response = requests.get(url, timeout=self.timeout)
            data = json.loads(response.text)
            assert data["error"] != "0"
            replies = []
            for reply in data["data"]["items"]:
                replies.append(Comment(
                    id=reply["comment_id"],
                    author=reply["full_name"],
                    content=BeautifulSoup(reply["content"], "html.parser").text,
                    date=datetime.utcfromtimestamp(int(reply["creation_time"])),
                    likes=reply["userlike"],
                    replies=self.crawl_replies(reply["comment_id"])
                ))
            return replies
        except Exception as e:
            print("Error while crawling reply of {}: {}".format(url, e))
            return []

    def crawl_comments(self, id: str, queue: Queue, crawl_replies=False):
        """
        Crawl comments of the given articles.
        """
        comments_endpoint = self.get_comments_endpoint(id)

        try:
            response = requests.get(comments_endpoint, timeout=self.timeout)
            data = json.loads(response.text)
            assert data["error"] != "0"

            replies = []
            if crawl_replies:
                replies = self.crawl_replies(comment["comment_id"])
            
            comments = []
            for comment in data["data"]["items"]:
                comments.append(Comment(
                    id=comment["comment_id"],
                    author=comment["full_name"],
                    content=BeautifulSoup(comment["content"], "html.parser").text,
                    date=datetime.utcfromtimestamp(int(comment["creation_time"])),
                    replies=replies,
                    likes=int(comment["userlike"])
                ))
            queue.put(comments)
        except Exception as e:
            print("Error while crawling comment of {}: {}".format(id, e))
            queue.put([])

    def get_article(self, url: str, crawl_comment=True):
        """
        Get an article given its URL.
        Return an Article object.
        """
        
        comments_queue = Queue(1)
        if crawl_comment:
            threading.Thread(
                target=self.crawl_comments,
                args=(self.get_id_from_url(url),
                comments_queue)).start()

        try:
            response = requests.get(url, timeout=self.timeout)
        except:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        try:
            title = soup.select_one(".title-detail").getText()
            author = soup.find("meta", {"name": "author"})["content"]
            excerpt = soup.find("meta", {"property": "og:description"})["content"]
            category = soup.find("meta", {"name": "tt_site_id_detail"})[
                "catename"
            ]

            tags = soup.find("meta", {"name": "keywords"})["content"]
            if tags:
                tags = [tag.strip() for tag in tags.split(",")]

            # Format 2021-11-13T13:02:00+07:00
            date = soup.find("meta", {"name": "pubdate"})["content"]
            date = date.split("+")[0] + "+0700"
            date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")

            paragraphs = soup.select("p.Normal")
            # Can be an empty string because some articles
            # might have no textual content (e.g. video, infographic)
            content = reduce(
                lambda value, p: value + p.get_text().strip() + "\n", paragraphs, ""
            )
            content = self.normalize_unicode(content)
            
            time.sleep(self.delay)
            
            comments = []
            if crawl_comment:
                try:
                    comments = comments_queue.get(timeout=10*60)
                except Empty:
                    pass

            return Article(
                id=self.get_id_from_url(url),
                source=self.SOURCE_NAME,
                title=title,
                date=date,
                tags=tags,
                author=author,
                excerpt=excerpt,
                content=content,
                url=url,
                comments=comments,
                category=category,
                likes=None # This news source doesn't have like count
            )

        except Exception as e:
            print("Error getting article {}: {}".format(url, e))
        
    
    def crawl_articles(self, limit=15):
        """
        Crawl articles given the limit.
        """
        article_urls = self.crawl_article_urls(limit)
        articles = []
        loss = 0
        try:
            for url in article_urls:
                article = self.get_article(url)
                if article:
                    articles.append(article)
                else:
                    loss += 1

                # Print progress
                freq = limit // 10 if limit > 10 else 1
                if len(articles) % freq == 0:
                    progress_string = (
                        "{}: Crawling {}%... Success: {}/{} Loss: {}".format(
                            self.SOURCE_NAME, len(articles) / limit * 100, len(articles), limit, loss
                        )
                    )
                    print(progress_string)
                    if self.telegram_key:
                        telegram.send_message(progress_string, self.telegram_key)

        except Exception as e:
            print(f"{self.SOURCE_NAME}:", "Error while getting articles:", e)

        print(f"{self.SOURCE_NAME}:", "Success:", len(articles), "/", limit, "Loss:", loss)
        
        return articles

if __name__ == "__main__":

    crawler = VnExpressCrawler(Category.SUC_KHOE, delay=5)
    a_urls = crawler.crawl_article_urls(limit=50)
    print(a_urls)
    print("len ", len(a_urls))
    
    for a_url in a_urls:
        a = crawler.get_article(a_url)
        if a is not None:
            with open("data/vnexpress_suc_khoe/{}.json".format(a.id), "w", encoding='utf8') as f:
                json.dump(a.to_dict(), f, ensure_ascii=False, indent=4)
