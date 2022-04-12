import dayjs from "dayjs";
import Text from "./Text";
import Article from "../models/Article";
import classNames from "classnames";

export const ArticleCard = ({
  article,
  spotlight = false,
  showThumbnail = false,
  mobile = false,
}: {
  article: Article;
  spotlight?: boolean;
  showThumbnail?: boolean;
  mobile?: boolean;
}) => {
  const maxSentimentValue = Math.max(
    article.positiveRate || 0,
    article.negativeRate || 0,
    article.neutralRate || 0
  );

  if (!spotlight)
    return (
      <ArticleCardDefault
        article={article}
        maxSentimentValue={maxSentimentValue}
        showThumbnail={showThumbnail}
        mobile={mobile}
      />
    );
  else
    return (
      <ArticleCardSpotlight
        article={article}
        maxSentimentValue={maxSentimentValue}
        showThumbnail={showThumbnail}
      />
    );
};

const ArticleCardSpotlight = ({
  article,
  maxSentimentValue,
  showThumbnail,
}: {
  article: Article;
  maxSentimentValue: number;
  showThumbnail: boolean;
}) => {
  return (
    <div className="p-4 w-full space-y-4">
      {article.imageUrl && showThumbnail && (
        <img
          className="w-full h-64 rounded-lg object-cover"
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
            {`${article.negativeRate.toFixed(0)}% `}
            tiêu cực
          </Text>
        )}
      </div>
    </div>
  );
};

const ArticleCardDefault = ({
  article,
  maxSentimentValue,
  showThumbnail,
  mobile,
}: {
  article: Article;
  maxSentimentValue: number;
  showThumbnail: boolean;
  mobile: boolean;
}) => {
  return (
    <div
      className={classNames(
        "p-4 w-full flex flex-row justify-between gap-x-4",
        {
          "bg-white rounded-lg": mobile,
        }
      )}
    >
      <div className="space-y-4 min-w-0">
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
            {`${article.negativeRate.toFixed(0)}% `}
            tiêu cực
          </Text>
        )}
      </div>
      {article.imageUrl && showThumbnail && (
        <img
          className="rounded-md object-cover h-24 w-24 hidden mobile:block"
          src={article.imageUrl}
          alt={`Hình ảnh cho bài viết ${article.title}`}
        />
      )}
    </div>
  );
};

const NewsSourceBar = ({
  sourceLogoUrl,
  sourceName,
  publishDate,
}: {
  sourceLogoUrl?: string;
  sourceName?: string;
  publishDate?: Date;
}) => {
  return (
    <div className="flex flex-row items-center space-x-1">
      {sourceLogoUrl && (
        <img
          src={sourceLogoUrl}
          className="h-4 rounded-xs"
          alt={`${sourceName} logo`}
        />
      )}
      {sourceName && (
        <Text className="shrink" fontSize="sm" fontWeight="medium" ellipsis>
          {sourceName}
        </Text>
      )}
      {publishDate && (
        <>
          <Text color="gray-40" fontSize="sm" fontWeight="medium">
            ·
          </Text>
          <Text color="gray-40" fontSize="sm" fontWeight="medium" nowrap>
            {`${capitalizeFirstLetter(dayjs(publishDate).fromNow())}`}
          </Text>
        </>
      )}
    </div>
  );
};

const capitalizeFirstLetter = (str: string) =>
  str.charAt(0).toUpperCase() + str.slice(1);

export default ArticleCard;
