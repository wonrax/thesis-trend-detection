import dayjs from "dayjs";
import Text from "./Text";
import Article from "../models/Article";
import classNames from "classnames";
import { capitalizeFirstLetter } from "../utils/string";

const formatSentimentRate = (rate: number) => {
  return (rate * 100).toFixed(0);
};

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
  if (!spotlight)
    return (
      <ArticleCardDefault
        article={article}
        showThumbnail={showThumbnail}
        mobile={mobile}
      />
    );
  else
    return (
      <ArticleCardSpotlight article={article} showThumbnail={showThumbnail} />
    );
};

const ArticleCardSpotlight = ({
  article,
  showThumbnail,
}: {
  article: Article;
  showThumbnail: boolean;
}) => {
  return (
    <a
      className="p-4 w-full space-y-4 block group overflow-hidden"
      {...(article.articleUrl && { href: article.articleUrl })}
    >
      {article.thumbnailUrl && showThumbnail && (
        <img
          loading="lazy"
          className="w-full h-64 rounded-lg object-cover"
          src={article.thumbnailUrl}
          alt={`Hình ảnh cho bài viết ${article.title}`}
        />
      )}
      <div className="space-y-2">
        <NewsSourceBar
          sourceName={article.sourceName}
          sourceLogoUrl={article.sourceLogoUrl}
          publishDate={article.publishDate}
        />
        <Text
          className="group-hover:underline"
          color="gray-100"
          fontSize="lg"
          fontWeight="bold"
          leading="tight"
        >
          {article.title}
        </Text>
        <Text color="gray-60" fontSize="body">
          {article.description}
        </Text>
        {article.positiveRate ? (
          <Text color="green" fontSize="sm" fontWeight="medium">
            {`${formatSentimentRate(article.positiveRate)}% `}
            tích cực
          </Text>
        ) : null}
        {article.negativeRate ? (
          <Text color="red" fontSize="sm" fontWeight="medium">
            {`${formatSentimentRate(article.negativeRate)}% `}
            tiêu cực
          </Text>
        ) : null}
      </div>
    </a>
  );
};

const ArticleCardDefault = ({
  article,
  showThumbnail,
  mobile,
}: {
  article: Article;
  showThumbnail: boolean;
  mobile: boolean;
}) => {
  return (
    <a
      className={classNames(
        "p-4 w-full flex flex-row justify-between gap-x-4 group",
        {
          "bg-white rounded-lg": mobile,
        }
      )}
      {...(article.articleUrl && { href: article.articleUrl })}
    >
      <div className="space-y-4 min-w-0">
        <div className="space-y-2">
          <NewsSourceBar
            sourceName={article.sourceName}
            sourceLogoUrl={article.sourceLogoUrl}
            publishDate={article.publishDate}
          />
          <Text
            className="group-hover:underline break-words"
            color="gray-100"
            fontSize="body"
            fontWeight="bold"
            leading="tight"
          >
            {article.title}
          </Text>
        </div>
        {article.positiveRate ? (
          <Text color="green" fontSize="sm" fontWeight="medium">
            {`${formatSentimentRate(article.positiveRate)}% `}
            tích cực
          </Text>
        ) : null}
        {article.negativeRate ? (
          <Text color="red" fontSize="sm" fontWeight="medium">
            {`${formatSentimentRate(article.negativeRate)}% `}
            tiêu cực
          </Text>
        ) : null}
      </div>
      {article.thumbnailUrl && showThumbnail && (
        <img
          loading="lazy"
          className="rounded-md object-cover h-24 w-24 hidden mobile:block"
          src={article.thumbnailUrl}
          alt={`Hình ảnh cho bài viết ${article.title}`}
        />
      )}
    </a>
  );
};

const NewsSourceBar = ({
  sourceLogoUrl,
  sourceName,
  publishDate,
}: {
  sourceLogoUrl?: string;
  sourceName?: string;
  publishDate?: string;
}) => {
  return (
    <div className="flex flex-row items-center space-x-1">
      <div className="flex flex-row items-center space-x-2 min-w-0">
        {sourceLogoUrl && (
          <img
            loading="lazy"
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
      </div>
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

export default ArticleCard;
