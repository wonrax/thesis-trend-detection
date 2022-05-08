from main import perform_analysis, perform_crawl
from data.model.category import Category
import time
from logger import get_common_logger

if __name__ == "__main__":
    logger = get_common_logger()

    categories = [c for c in Category]
    categories.remove(Category.MOI_NHAT)

    try:
        while True:
            logger.critical(
                "Deamon started performing analysis at {}".format(time.ctime())
            )
            perform_crawl(
                category=Category.MOI_NHAT,
                days=1,
                source="all",
                do_crawl_comment=True,
            )
            perform_analysis(category=Category.MOI_NHAT, days=1.5)
            for _category in categories:
                perform_analysis(category=_category, days=3)

            time.sleep(6 * 60 * 60)  # sleep for 6 hours
    except Exception:
        logger.exception("Exception occurred while running deamon")
        logger.critical("Daemon stopped")
