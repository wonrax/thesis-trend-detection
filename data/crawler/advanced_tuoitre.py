import requests
from bs4 import BeautifulSoup
import time
from functools import reduce
import json
from datetime import datetime, timedelta, timezone
import unicodedata
import threading
from model.article import Article, Comment
from util import telegram
from crawler.base import Crawler, Category


class TuoiTreCrawler(Crawler):
    """
    Crawl articles from TuoiTre news. Support crawling articles from
    sub-categories (e.g "the-thao" as in "https://tuoitre.vn/the-thao.htm").
    """

    BASE_URL = "https://tuoitre.vn"
    API_URL = "https://id.tuoitre.vn/api"
    LIKE_COUNT_URL = "https://s5.tuoitre.vn/count-object.htm"
    SOURCE_NAME = "Tuổi Trẻ"

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

    def get_news_list_url(self, date: datetime, cursor: int):
        """
        Return the URL of the newspaper indexes given the date and cursor.
        """

        assert self.category_id is not None

        return (
            TuoiTreCrawler.BASE_URL
            + "/timeline-xem-theo-ngay/{}/{}/trang-{}.htm".format(
                self.category_id, date.strftime("%d-%m-%Y"), cursor
            )
        )

    def get_id_from_url(self, url: str):
        """
        Return the article ID given the URL.
        """

        return url.split("/")[-1].split(".")[0].split("-")[-1]

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

        print("Getting article URLs from", url)

        try:
            response = requests.get(url, timeout=self.timeout)
        except requests.exceptions.ConnectionError:
            print("\nConnection timed out for url {}.\n".format(url))
            return set(), False
        except:
            return set(), False
        finally:
            time.sleep(self.delay)

        response_soup = BeautifulSoup(response.text, "html.parser")

        news_items = response_soup.find_all("li", class_="news-item")

        article_urls = set()

        # Signal the caller to stop
        stop = False

        for item in news_items:

            if limit and limit <= len(article_urls):
                break

            a_tag = item.find("a", recursive=False)
            article_url = TuoiTreCrawler.BASE_URL + a_tag["href"]

            if (
                self.SOURCE_NAME,
                self.get_id_from_url(article_url),
            ) not in self.skip_these:
                article_urls.add(article_url)

            elif self.newer_only:
                stop = True
                break

        return article_urls, stop

    def get_date_from_range(self, start_time, end_time):
        """
        Generate a list of dates between end_time and start_time.
        """

        date = end_time

        while date >= start_time:
            yield date
            date -= timedelta(days=1)

    def crawl_article_urls(self, limit=15, start_time=None, end_time=None):
        """
        Try to find as many articles as possible given the limit.
        Return a set of article URLs.
        """

        if start_time is None:
            start_time = self.utc_to_vietnam_time(
                datetime(1970, 1, 1, tzinfo=timezone.utc)
            )
        if end_time is None:
            end_time = self.utc_to_vietnam_time(
                datetime.utcnow().astimezone(timezone.utc)
            )

        article_urls = set()

        date_generator = self.get_date_from_range(start_time, end_time)

        try:
            stop = False

            while len(article_urls) < limit:
                date = next(date_generator, None)
                if date is None:
                    break
                cursor = 1

                while True and len(article_urls) < limit:
                    page_url = self.get_news_list_url(date, cursor)
                    new_urls, stop = self.find_article_urls(
                        page_url, limit - len(article_urls)
                    )
                    article_urls.update(new_urls)
                    # Empty page (indicating we've reached the end of this day)
                    # or stop signal
                    if len(new_urls) == 0 or stop:
                        break
                    cursor += 1

                if stop:
                    break

                time.sleep(self.delay)
        except Exception as e:
            print("\nError while getting article URLs:", e, "\n")
            pass

        return article_urls

    def get_likes_count(self, id, likes=None):
        """
        Get the number of likes an article has received given its id.
        """

        try:

            url = TuoiTreCrawler.LIKE_COUNT_URL + "?newsId=" + id

            like_count = 0

            try:
                like_count = requests.get(
                    url, headers={"Origin": "https://tuoitre.vn"}, timeout=self.timeout
                )
                like_count = int(like_count.text)
            except requests.exceptions.ConnectionError:
                print("\nConnection timed out for like count {}.\n".format(id))
            except:
                pass

            if likes is not None:
                likes[0] = like_count

        except Exception as e:
            print("\nError while getting likes for article with id", id, ":", e, "\n")

        return like_count

    def get_article(self, url: str):
        """
        Get an article given its URL.
        Return an Article object.
        """

        id = self.get_id_from_url(url)

        likes = [None]  # A list makes it easier to pass data across threads

        get_like_thread = threading.Thread(
            target=self.get_likes_count,
            args=[id, likes],
            name="Crawler_Get_like_thread",
        )
        get_like_thread.start()

        try:
            response = requests.get(url, timeout=self.timeout)
        except Exception as e:
            print("Error while getting article with url", url, ":", e, "\n")
            return None

        response_soup = BeautifulSoup(response.text, "html.parser")

        source = TuoiTreCrawler.SOURCE_NAME

        try:
            title = response_soup.find("meta", {"property": "og:title"})["content"]
            author = response_soup.find("meta", {"name": "author"})["content"]
            excerpt = response_soup.find("meta", {"name": "description"})["content"]
            category = response_soup.find("meta", {"property": "article:section"})[
                "content"
            ]

            tags = response_soup.find("meta", {"name": "keywords"})["content"]
            if tags:
                tags = tags.split(",")

            # Format 2021-11-13T13:02:00+07:00
            date = response_soup.find("meta", {"name": "pubdate"})["content"]
            date = date.split("+")[0] + "+0700"
            date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")

            paragraphs = response_soup.find(id="main-detail-body").find_all(
                "p", recursive=False
            )
            # Can be an empty string because some articles
            # might have no textual content (e.g. video, infographic)
            content = reduce(
                lambda value, p: value + p.get_text().strip() + "\n", paragraphs, ""
            )
            content = self.normalize_unicode(content)

            return Article(
                id,
                source,
                title,
                date,
                tags,
                author,
                excerpt,
                content,
                url,
                category=category,
                likes=likes[0],
            )

        except Exception as e:
            print("\nError while getting article with id", id, ":", e)
            print("The article could be an unexpected format (Infographic, video...).")

        get_like_thread.join()

    def json_to_comment(self, json_comment: dict):
        """
        Convert a JSON comment to a Comment object.
        """

        id = json_comment["id"]
        author = json_comment["sender_fullname"]
        content = BeautifulSoup(json_comment["content"], "html.parser").text
        likes = int(json_comment["likes"])

        # E.g. 2021-11-12T09:32:32
        str_date = json_comment["created_date"]
        date = datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%S")

        replies = []
        if json_comment["child_comments"] is not None:
            replies = [
                self.json_to_comment(reply) for reply in json_comment["child_comments"]
            ]

        return Comment(id, author, content, date, replies, likes)

    def _crawl_comments(self, id, cursor=1, limit=20):
        """
        Get comments of an article given its ID.
        Return a set of Comment objects.
        """

        api_url = self.API_URL + "/getlist-comment.api?"

        url = api_url + "objId={}&pageindex={}&pagesize={}&objType=1&sort=1".format(
            id, cursor, limit
        )

        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            print("\nConnection timed out while getting comments.\n")
            return []
        except:
            return []

        response_json = response.json()

        assert response_json["Success"] == True

        data = json.loads(response_json["Data"])

        comments = []

        for comment in data:
            comments.append(self.json_to_comment(comment))

        return comments

    def crawl_comments(self, id, limit=float("inf"), thread_return=None):
        """
        Get comments of an article given its ID.
        Return a set of Comment objects.
        """

        comments = []
        cursor = 1

        try:
            while len(comments) < limit:
                new_comments = self._crawl_comments(id, cursor)

                time.sleep(self.delay)

                # Reached the end of the comments
                if len(new_comments) == 0:
                    break

                comments += new_comments
                cursor += 1

        except AssertionError:
            # No more comments
            pass

        except Exception as e:
            print(
                "\nError while getting crawling comments of post id", id, ":", e, "\n"
            )
            pass

        if thread_return is not None:
            thread_return[0] = comments

        return comments

    def crawl_articles(self, limit, start_time=None, end_time=None):
        """
        Crawl articles given the limit.
        Return a list of Article objects.
        """

        article_urls = self.crawl_article_urls(
            limit=limit, start_time=start_time, end_time=end_time
        )

        articles = []
        loss = 0

        print("Getting", len(article_urls), "articles...")

        # update the limit according to the number of articles
        limit = len(article_urls)

        try:
            for url in article_urls:

                get_comments_thread = None
                comments = [None]  # A list makes it easier to pass data across threads

                if self.crawl_comment:

                    id = self.get_id_from_url(url)
                    get_comments_thread = threading.Thread(
                        target=self.crawl_comments,
                        kwargs={"id": id, "thread_return": comments},
                        name="Crawler_Get_comments_thread",
                    )
                    get_comments_thread.start()

                a = self.get_article(url)

                if a:
                    articles.append(a)
                    if get_comments_thread:
                        get_comments_thread.join()
                        a.comments = comments[0]

                else:
                    loss += 1

                time.sleep(self.delay)

                freq = limit // 10 if limit > 10 else 1
                if len(articles) % freq == 0:
                    progress_string = (
                        "{}: Crawling {}%... Success: {}/{} Loss: {}".format(
                            self.SOURCE_NAME,
                            len(articles) / limit * 100,
                            len(articles),
                            limit,
                            loss,
                        )
                    )
                    print(progress_string)
                    if self.telegram_key:
                        telegram.send_message(progress_string, self.telegram_key)

        except Exception as e:
            print(f"{self.SOURCE_NAME}:", "Error while getting articles:", e)

        print(
            f"{self.SOURCE_NAME}:", "Success:", len(articles), "/", limit, "Loss:", loss
        )

        return articles
