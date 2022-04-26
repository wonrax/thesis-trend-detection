import ArticleCard from "./ArticleCard";
import Article from "../models/Article";
import Text from "./Text";
import Divider from "./Divider";
import { useNavigate } from "react-router-dom";

export const TopicSection = ({
  spotlightArticle,
  articles = undefined,
  showThumbnail = false,
  keywords = undefined,
  hasMore,
  trendId = undefined,
  topicIndex = undefined,
}: {
  spotlightArticle: Article;
  articles?: Array<Article>;
  showThumbnail?: boolean;
  keywords?: Array<string>;
  hasMore?: boolean;
  trendId?: string;
  topicIndex?: number;
}) => {
  const navigate = useNavigate();
  if (!spotlightArticle) return null;
  return (
    <div className="w-full rounded-lg bg-white">
      {spotlightArticle && (
        <>
          <ArticleCard spotlight showThumbnail article={spotlightArticle} />
          <Divider />
        </>
      )}
      {keywords && (
        <div className="flex flex-row items-center gap-2 px-4 py-2">
          <Text fontSize="lg" color="gray-40" fontWeight="medium">
            #
          </Text>
          <div className="flex flex-row flex-wrap gap-2">
            {keywords.map((keyword, index) => (
              <div className="bg-gray-0 px-3 py-2 rounded-md min-w-0">
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
          onClick={() => navigate(`/topic/${trendId}/${topicIndex}`)}
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
