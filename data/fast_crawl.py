from crawler.fast_tuoitre import FastTuoiTreCrawler
from crawler.fast_vnexpress import FastVnExpressCrawler
from crawler.fast_base import Category
import json
import datetime
from zoneinfo import ZoneInfo

config = {"category": Category.MOI_NHAT, "do_crawl_comment": False, "delay": None}

ttcrawler = FastTuoiTreCrawler(**config)
vncrawler = FastVnExpressCrawler(**config)

articles = []
for crawler in [ttcrawler]:
    end_date = datetime.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    start_date = end_date - datetime.timedelta(days=3)
    articles += crawler.crawl(
        start_date=start_date,
        end_date=end_date,
    )

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
