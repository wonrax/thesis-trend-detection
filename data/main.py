from crawler.tuoitre import TuoiTreCrawler
from crawler.vnexpress import VnExpressCrawler
from crawler.base import Category
from model.article import Article
from serialization import FileStorage
import argparse
import time
from util import telegram
from queue import Queue, Empty
import threading

CATEGORY_MAP = {
    "the-gioi": Category.THE_GIOI,
    "thoi-su": Category.THOI_SU,
    "suc-khoe": Category.SUC_KHOE,
    "van-hoa": Category.VAN_HOA,
    "cong-nghe": Category.CONG_NGHE,
    "the-thao": Category.THE_THAO,
    "giao-duc": Category.GIAO_DUC,
    "moi-nhat": Category.MOI_NHAT,
}


def crawl(
    crawlers,
    file_path,
    category,
    limit,
    delay,
    crawl_comment,
    newer_only,
    extend,
    telegram_key,
):
    crawled_ids = set()
    write_mode = "w"

    if extend:
        write_mode = "a"
        loaded_articles: list[Article] = FileStorage.load(args.file)
        crawled_ids = set([(a.source, a.id) for a in loaded_articles])

    crawlers_engine = []
    if "tuoitre" in crawlers:
        crawlers_engine.append(
            TuoiTreCrawler(
                category=category,
                delay=delay,
                crawl_comment=crawl_comment,
                skip_these=crawled_ids,
                newer_only=newer_only,
                telegram_key=telegram_key,
            )
        )
    if "vnexpress" in crawlers:
        crawlers_engine.append(
            VnExpressCrawler(
                category=category,
                delay=delay,
                crawl_comment=crawl_comment,
                skip_these=crawled_ids,
                newer_only=newer_only,
                telegram_key=telegram_key,
            )
        )

    t_start = time.time()

    print_session_info(
        limit=limit,
        category=category,
        crawl_comment=crawl_comment,
        delay=delay,
        newer_only=newer_only,
        telegram_key=telegram_key,
    )

    def start_crawl_thread(crawler, queue):
        _articles = crawler.crawl_articles(limit=limit)
        queue.put(_articles)

    crawler_result_queue = Queue(len(crawlers_engine))

    for crawler in crawlers_engine:
        threading.Thread(
            target=start_crawl_thread, args=(crawler, crawler_result_queue)
        ).start()

    articles = []

    for _ in range(len(crawlers_engine)):
        try:
            articles += crawler_result_queue.get(timeout=24 * 60 * 60)
        except Empty:
            print(f"Timeout for {crawler.SOURCE_NAME}")

    FileStorage.store(articles, file_path=file_path, mode=write_mode)

    time_taken_string = "Finish. Time taken: {}m{:.2f}s".format(
        (time.time() - t_start) // 60, (time.time() - t_start) % 60
    )

    print(time_taken_string)
    if telegram_key:
        telegram.send_message(time_taken_string, telegram_key)


def print_session_info(limit, category, crawl_comment, delay, newer_only, telegram_key):
    start_string = (
        "Starting to crawl articles...\nLimit per news source: {}\nCategory ID: {}\n"
        + "Crawl comments: {}\nDelay: {}\nNewer only: {}"
    ).format(limit, category, crawl_comment, delay, newer_only)

    print(start_string)

    from datetime import datetime
    import pytz

    if telegram_key:
        telegram.send_message(
            "🔥🔥🔥\nNew crawl session started at {}".format(
                datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ),
            telegram_key,
        )
        telegram.send_message(start_string, telegram_key)


def preview_data(file_path):
    """
    Preview the first and the last article of the batch.
    """

    articles = FileStorage.load(file_path)
    titles = [article.title for article in articles]
    print_list_preview(titles)


# Print the preview of the set of the articles
def print_list_preview(l: list):
    """
    Print the first and the last item of the list
    """

    if len(l) < 1:
        return

    print("[", 1, "]", l[0])
    if len(l) < 2:
        return

    print("...")
    print("[", len(l), "]", l[-1])


def preview_random_comment():
    """Preview comment from a random article."""

    comments = TuoiTreCrawler()._crawl_comments(id="202111131227554", limit=2)
    print(comments[0])


def sort_data(file_path):
    """
    Sort the articles by their date.
    """

    loaded_articles = FileStorage.load(file_path=file_path)
    FileStorage.store(loaded_articles, file_path, mode="w", sort=True)


def duplication_test(file_path):
    """
    Test if the articles are duplicated.
    """

    loaded_articles = FileStorage.load(file_path)

    print("Duplicated:", len(loaded_articles) - len(set(loaded_articles)))

    # Print duplicate article ids
    import collections

    print(
        [
            item.id
            for item, count in collections.Counter(loaded_articles).items()
            if count > 1
        ]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Crawl TuoiTre news.")

    group = parser.add_mutually_exclusive_group()

    parser.add_argument(
        "--crawler",
        action="append",
        help="Add news crawler. Default: Use all crawlers. Options: tuoitre, vnexpress.",
        required=False,
    )

    parser.add_argument("-f", "--file", help="file to store or load the crawled data")

    group.add_argument(
        "-c", "--crawl", help="crawl the TuoiTre website", action="store_true"
    )
    parser.add_argument("-n", "--number", help="number of articles to crawl", type=int)
    parser.add_argument(
        "--no-comment",
        help="do not crawl the comments of the articles",
        action="store_true",
    )
    parser.add_argument(
        "-d", "--delay", help="delay between requests", type=float, default=1
    )
    parser.add_argument(
        "--category",
        help="category of the articles to crawl",
        type=str,
        default="moi-nhat",
    )
    parser.add_argument(
        "--newer-only",
        help="only crawl articles newer than the last crawled article",
        action="store_true",
    )
    parser.add_argument(
        "-e", "--extend", help="extend the crawled articles", action="store_true"
    )

    parser.add_argument("--telegram", help="send the status to telegram", type=str)

    parser.add_argument(
        "-s", "--sort", help="sort the crawled articles", action="store_true"
    )

    parser.add_argument(
        "-p",
        "--preview",
        help="print a preview of the crawled articles",
        action="store_true",
    )

    parser.add_argument(
        "-t", "--test", help="test duplication in the dataset", action="store_true"
    )

    args = parser.parse_args()

    if args.crawl:
        if args.number is None:
            parser.error("Please specify the number of articles to crawl with --number")
        if args.file is None:
            parser.error(
                "Please specify the file to store the crawled data with --file"
            )
        if args.category not in CATEGORY_MAP:
            parser.error("Please specify a valid category with --category")

        crawlers = ["tuoitre", "vnexpress"]
        if args.crawler:
            crawlers = args.crawler

        crawl(
            crawlers,
            file_path=args.file,
            category=CATEGORY_MAP[args.category],
            limit=args.number,
            delay=args.delay,
            crawl_comment=not args.no_comment,
            newer_only=args.newer_only,
            extend=args.extend,
            telegram_key=args.telegram,
        )

        if args.sort:
            sort_data(file_path=args.file)

        if args.preview:
            preview_data(file_path=args.file)

        if args.test:
            duplication_test(file_path=args.file)

    else:
        if args.file is None:
            parser.error("Please specify the file to load the crawled data with --file")

        if args.sort:
            sort_data(file_path=args.file)

        if args.preview:
            preview_data(file_path=args.file)

        if args.test:
            duplication_test(file_path=args.file)
