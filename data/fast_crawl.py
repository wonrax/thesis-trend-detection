from crawler.fast_tuoitre import FastTuoiTreCrawler
from crawler.fast_vnexpress import FastVnExpressCrawler
from crawler.fast_dantri import FastDanTriCrawler
from crawler.fast_vietnamnet import FastVietnamnetCrawler
from crawler.fast_base import Category
import json
import datetime
from zoneinfo import ZoneInfo
import threading
from queue import Queue, Empty
import time

config = {"category": Category.THOI_SU, "do_crawl_comment": False, "delay": 0.5}

ttcrawler = FastTuoiTreCrawler(**config)
vncrawler = FastVnExpressCrawler(**config)
dtcrawler = FastDanTriCrawler(**config)
vnncrawler = FastVietnamnetCrawler(**config)

crawler_engines = [ttcrawler, vncrawler, dtcrawler, vnncrawler]

# Date range to crawl
end_date = datetime.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
start_date = end_date - datetime.timedelta(days=2)


def start_crawl_thread(crawler, queue):
    _articles = crawler.crawl(start_date, end_date)
    queue.put(_articles)


crawler_result_queue = Queue(len(crawler_engines))

t1 = time.time()

for crawler in crawler_engines:
    threading.Thread(
        target=start_crawl_thread, args=(crawler, crawler_result_queue)
    ).start()

articles = []

for _ in crawler_engines:
    try:
        articles += crawler_result_queue.get(timeout=24 * 60 * 60)
    except Empty:
        print(f"Timeout for {crawler.SOURCE_NAME}")

print(f"Got a total of {len(articles)} articles.")
print(f"Crawling took {time.time() - t1} seconds.")

# sort articles by date
articles.sort(key=lambda x: x.date)

with open("./tmp/articles.json", "w", encoding="utf-8") as f:
    file_content = json.dump(
        [article.to_dict() for article in articles],
        fp=f,
        indent=2,
        default=str,
        ensure_ascii=False,
    )
