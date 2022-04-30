import ArticleCard from "./ArticleCard";
import Article from "../models/Article";
import Text from "./Text";
import Divider from "./Divider";

export const TopicSection = ({
  spotlightArticle,
  articles,
  showThumbnail = false,
  keywords,
  rank,
  hasMore,
  navigateToTopic,
}: {
  spotlightArticle: Article;
  articles?: Array<Article>;
  showThumbnail?: boolean;
  keywords?: Array<string>;
  rank?: number;
  hasMore?: boolean;
  navigateToTopic?: () => void;
}) => {
  if (!spotlightArticle) return null;

  let _kws = undefined;
  if (keywords && keywords?.length <= 2) _kws = keywords;
  else _kws = keywords?.slice(0, 2);

  return (
    <div className="w-full rounded-lg bg-white">
      {spotlightArticle && (
        <>
          <ArticleCard spotlight showThumbnail article={spotlightArticle} />
          <Divider />
        </>
      )}
      {_kws && (
        <div className="flex flex-row items-center gap-2 px-4 py-2">
          <Text fontSize="lg" color="gray-40" fontWeight="medium">
            #{rank || ""}
          </Text>
          <div className="flex flex-row flex-wrap gap-2">
            {_kws.map((keyword, index) => (
              <div
                key={index}
                className="bg-gray-0 px-3 py-2 rounded-md min-w-0"
              >
                <Text key={index} fontWeight="medium" color="gray-40" ellipsis>
                  {keyword}
                </Text>
              </div>
            ))}
          </div>
        </div>
      )}
      {articles &&
        articles.length > 0 &&
        articles.map((article, index) => (
          <div key={article.id}>
            {index == 0 && <Divider />}
            <ArticleCard showThumbnail={showThumbnail} article={article} />
            {(hasMore || index < articles.length - 1) && <Divider />}
          </div>
        ))}
      {hasMore && (
        <div
          className="py-4 group hover:cursor-pointer"
          onClick={() => {
            if (navigateToTopic) navigateToTopic();
          }}
        >
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
