from crawler import TuoiTreCrawler
from serialization import FileStorage
import argparse

CATEGORY_MAP = {
    "moi-nhat": TuoiTreCrawler.Category.MOI_NHAT,
    "the-gioi": TuoiTreCrawler.Category.THE_GIOI,
    "thoi-su": TuoiTreCrawler.Category.THOI_SU,
    "suc-khoe": TuoiTreCrawler.Category.SUC_KHOE,
    "van-hoa": TuoiTreCrawler.Category.VAN_HOA,
    "cong-nghe": TuoiTreCrawler.Category.CONG_NGHE,
    "the-thao": TuoiTreCrawler.Category.THE_THAO,
    "giao-duc": TuoiTreCrawler.Category.GIAO_DUC,
}


def crawl(
    file_path, category, limit, delay, crawl_comment, newer_only, extend, telegram_key
):
    crawled_ids = set()
    write_mode = "w"

    if extend:
        write_mode = "a"
        loaded_articles = FileStorage.load(args.file)
        crawled_ids = set([a.id for a in loaded_articles])

    crawler = TuoiTreCrawler(
        category=category,
        delay=delay,
        crawl_comment=crawl_comment,
        skip_these=crawled_ids,
        newer_only=newer_only,
    )

    articles = crawler.crawl_articles(limit=limit, telegram_key=telegram_key)

    FileStorage.store(articles, file_path=file_path, mode=write_mode)


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
    ids = [a.id for a in loaded_articles]

    print("Duplicated:", len(ids) != len(set(ids)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Crawl TuoiTre news.")

    group = parser.add_mutually_exclusive_group()

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

        crawl(
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

        if args.preview:
            preview_data(file_path=args.file)

        if args.sort:
            sort_data(file_path=args.file)

        if args.test:
            duplication_test(file_path=args.file)
