import ArticleCard from "./ArticleCard";
import Article from "../models/Article";
import Text from "./Text";

export const TopicSection = ({
  spotlightArticle,
  articles = undefined,
}: {
  spotlightArticle: Article;
  articles?: Array<Article>;
}) => {
  if (!spotlightArticle) return null;
  return (
    <div className="w-full rounded-xl bg-gradient-to-b from-white to-gray-0">
      {spotlightArticle && <ArticleCard article={spotlightArticle} />}
      {articles && articles.length > 0 && (
        <ArticleCard compact article={articles[0]} />
      )}
      <Text
        className="px-3 py-1 m-auto rounded-md my-4 bg-white w-fit"
        fontWeight="medium"
        textAlign="center"
      >
        Xem thêm tin về chủ đề này
      </Text>
    </div>
  );
};

export default TopicSection;
