import dayjs from "dayjs";
import Text from "./Text";
import Article from "../models/Article";
import classNames from "classnames";
import { capitalizeFirstLetter } from "../utils/string";
import { ReactComponent as ThumbsUp } from "./icons/ThumbsUp.svg";
import { ReactComponent as ThumbsDown } from "./icons/ThumbsDown.svg";

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
          fontWeight="medium"
          leading="tight"
        >
          {article.title}
        </Text>
        <Text color="gray-60" fontSize="body">
          {article.description}
        </Text>
        <SentimentBar
          positiveRate={article.positiveRate}
          negativeRate={article.negativeRate}
        />
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
        <SentimentBar
          positiveRate={article.positiveRate}
          negativeRate={article.negativeRate}
        />
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
          <Text className="shrink" color="gray-40" fontSize="sm">
            {sourceName}
          </Text>
        )}
      </div>
      {publishDate && (
        <>
          <Text color="gray-40" fontSize="sm">
            ·
          </Text>
          <Text color="gray-40" fontSize="sm" nowrap>
            {`${capitalizeFirstLetter(dayjs(publishDate).fromNow())}`}
          </Text>
        </>
      )}
    </div>
  );
};

const SentimentChip = ({
  rate,
  negative,
}: {
  rate: number;
  negative?: boolean;
}) => {
  return (
    <div
      className={`flex flex-row w-fit items-center gap-1 rounded-md px-2 py-1 bg-opacity-10 ${
        negative ? "bg-red" : "bg-green"
      }`}
    >
      {negative ? <ThumbsDown /> : <ThumbsUp />}
      <Text
        fontSize="sm"
        fontWeight="medium"
        color={negative ? "red" : "green"}
      >
        {`${formatSentimentRate(rate)}%`}
      </Text>
    </div>
  );
};

const SentimentBar = ({
  positiveRate,
  negativeRate,
}: {
  positiveRate?: number;
  negativeRate?: number;
}) => {
  return (
    <div className="flex flex-row gap-2">
      {positiveRate ? <SentimentChip rate={positiveRate} /> : null}
      {negativeRate ? <SentimentChip rate={negativeRate} negative /> : null}
    </div>
  );
};

export default ArticleCard;
