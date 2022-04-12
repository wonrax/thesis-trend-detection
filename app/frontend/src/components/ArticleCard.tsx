import MockData from "../test/data";
import "dayjs";
import "dayjs/locale/vi";
import dayjs from "dayjs";
import { Text } from "./Text";

export const ArticleCard = ({
  article,
  compact = false,
  showThumbnail = true,
}: {
  article: ReturnType<typeof MockData.getRandomArticle>;
  compact?: boolean;
  showThumbnail?: boolean;
}) => {
  const maxSentimentValue = Math.max(
    article.positiveRate,
    article.negativeRate,
    article.neutralRate
  );

  if (compact)
    return (
      <ArticleCardCompact
        article={article}
        maxSentimentValue={maxSentimentValue}
        showThumbnail={showThumbnail}
      />
    );
  else
    return (
      <ArticleCardDefault
        article={article}
        maxSentimentValue={maxSentimentValue}
        showThumbnail={showThumbnail}
      />
    );
};

const ArticleCardDefault = ({
  article,
  maxSentimentValue,
  showThumbnail,
}: {
  article: ReturnType<typeof MockData.getRandomArticle>;
  maxSentimentValue: number;
  showThumbnail: boolean;
}) => {
  return (
    <div className="p-4 w-full space-y-4">
      {showThumbnail && (
        <img
          className="w-full h-64 rounded-xl object-cover"
          src={article.imageUrl}
          alt={`Hình ảnh cho bài viết ${article.title}`}
        />
      )}
      <div className="space-y-2">
        <NewsSourceBar
          sourceName={article.sourceName}
          sourceLogoUrl={article.sourceLogoUrl}
          publishDate={article.publishDate}
        />
        <Text color="gray-100" fontSize="lg" fontWeight="bold" leading="tight">
          {article.title}
        </Text>
        <Text color="gray-60" fontSize="body">
          {article.description}
        </Text>
        {maxSentimentValue == article.positiveRate && (
          <Text color="green" fontSize="sm" fontWeight="medium">
            {`${article.positiveRate.toFixed(0)}% `}
            tích cực
          </Text>
        )}
        {maxSentimentValue == article.negativeRate && (
          <Text color="red" fontSize="sm" fontWeight="medium">
            {`${article.positiveRate.toFixed(0)}% `}
            tiêu cực
          </Text>
        )}
      </div>
    </div>
  );
};

const ArticleCardCompact = ({
  article,
  maxSentimentValue,
  showThumbnail,
}: {
  article: ReturnType<typeof MockData.getRandomArticle>;
  maxSentimentValue: number;
  showThumbnail: boolean;
}) => {
  return (
    <div className="p-4 w-full bg-white rounded-md flex flex-row justify-between gap-x-4">
      <div className="space-y-4 w-full">
        <div className="space-y-2">
          <NewsSourceBar
            sourceName={article.sourceName}
            sourceLogoUrl={article.sourceLogoUrl}
            publishDate={article.publishDate}
          />
          <Text
            className="break-words"
            color="gray-100"
            fontSize="body"
            fontWeight="bold"
            leading="tight"
          >
            {article.title}
          </Text>
        </div>
        {maxSentimentValue == article.positiveRate && (
          <Text color="green" fontSize="sm" fontWeight="medium">
            {`${article.positiveRate.toFixed(0)}% `}
            tích cực
          </Text>
        )}
        {maxSentimentValue == article.negativeRate && (
          <Text color="red" fontSize="sm" fontWeight="medium">
            {`${article.positiveRate.toFixed(0)}% `}
            tiêu cực
          </Text>
        )}
      </div>
      <img
        className="rounded-md object-cover h-24 w-24 hidden mobile:block"
        src={article.imageUrl}
        alt={`Hình ảnh cho bài viết ${article.title}`}
      />
    </div>
  );
};

const NewsSourceBar = ({
  sourceLogoUrl,
  sourceName,
  publishDate,
}: {
  sourceLogoUrl: string;
  sourceName: string;
  publishDate: Date;
}) => {
  return (
    <div className="flex flex-row items-center space-x-1">
      <img
        src={sourceLogoUrl}
        className="h-4 rounded-xs"
        alt={`${sourceName} logo`}
      />
      <Text
        className="shrink grow-0"
        fontSize="sm"
        fontWeight="medium"
        ellipsis
      >
        {sourceName}
      </Text>
      <Text color="gray-40" fontSize="sm" fontWeight="medium">
        ·
      </Text>
      <Text color="gray-40" fontSize="sm" fontWeight="medium" ellipsis>
        {`${capitalizeFirstLetter(dayjs(publishDate).fromNow())}`}
      </Text>
    </div>
  );
};

const capitalizeFirstLetter = (str: string) =>
  str.charAt(0).toUpperCase() + str.slice(1);

export default ArticleCard;
