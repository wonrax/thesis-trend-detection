from main import perform_analysis, perform_crawl
from data.model.category import Category
from logger import get_common_logger
from data.preprocess import rdrsegmenter

if __name__ == "__main__":
    logger = get_common_logger()

    categories = [c for c in Category]

    logger.critical("Cronjob started crawling and performing analysis")

    try:
        perform_crawl(
            category=Category.MOI_NHAT,
            days=1,
            source="all",
            do_crawl_comment=True,
        )
        for _category in categories:
            perform_analysis(category=_category, days=1.5)
    except:
        logger.exception("Exception occurred while running cronjob")
        logger.critical("Cronjob stopped with error")

    if rdrsegmenter:
        logger.info(f"Closing VnCoreNLP server...")
        rdrsegmenter.close()
