import ArticleCard from "./ArticleCard";
import Article from "../models/Article";
import Text from "./Text";
import Divider from "./Divider";

export const TopicSection = ({
  spotlightArticle,
  articles = undefined,
  hasMore,
}: {
  spotlightArticle: Article;
  articles?: Array<Article>;
  hasMore: boolean;
}) => {
  if (!spotlightArticle) return null;
  return (
    <div className="w-full rounded-lg bg-white pb-4">
      {spotlightArticle && (
        <ArticleCard spotlight showThumbnail article={spotlightArticle} />
      )}
      {articles &&
        articles.length > 0 &&
        articles.map((article) => (
          <>
            <Divider />
            <ArticleCard showThumbnail article={article} />
          </>
        ))}
      {hasMore && (
        <Text
          className="px-3 py-1 m-auto mt-4 rounded-md bg-gray-0 w-fit"
          fontWeight="medium"
          textAlign="center"
        >
          Xem thêm tin về chủ đề này
        </Text>
      )}
    </div>
  );
};

export default TopicSection;
