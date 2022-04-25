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
    <div className="w-full rounded-lg bg-white">
      {spotlightArticle && (
        <ArticleCard spotlight showThumbnail article={spotlightArticle} />
      )}
      {articles &&
        articles.length > 0 &&
        articles.map((article, index) => (
          <div key={article.id}>
            {index == 0 && <Divider />}
            <ArticleCard article={article} />
            {(hasMore || index < articles.length - 1) && <Divider />}
          </div>
        ))}
      {hasMore && (
        <div className="py-4 group hover:cursor-pointer">
          <Text
            className="px-3 py-1 m-auto rounded-md bg-gray-0 w-fit group-hover:underline"
            fontWeight="medium"
            textAlign="center"
          >
            Xem thêm tin về chủ đề này
          </Text>
        </div>
      )}
    </div>
  );
};

export default TopicSection;
