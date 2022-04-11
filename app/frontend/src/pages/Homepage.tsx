import MockData from "../test/data";
import { useEffect, useState } from "react";

export const Homepage = () => {
  const [topics, setTopics] = useState<
    Array<ReturnType<typeof MockData.getRandomArticle>[]>
  >([]);

  useEffect(() => {
    const topics: Array<ReturnType<typeof MockData.getRandomArticle>[]> =
      new Array(Math.floor(Math.random() * 5)).fill(null);
    setTopics(
      topics.map(() => {
        const articles: ReturnType<typeof MockData.getRandomArticle>[] =
          new Array(Math.floor(Math.random() * 5)).fill(null);
        return articles.map(() => MockData.getRandomArticle());
      })
    );
  }, []);

  return (
    <>
      <div className="p-8 flex flex-col justify-center items-center">
        <h3 className="text-xl inline text-gray-100">Các chủ đề nổi bật về</h3>
        <h3 className="text-xl inline font-bold text-gray-100">Sức khỏe</h3>
      </div>
      <div>
        {topics.map((articles) =>
          articles.map((article) => (
            <Article key={article.id} article={article} />
          ))
        )}
      </div>
    </>
  );
};

const Article = ({
  article,
}: {
  article: ReturnType<typeof MockData.getRandomArticle>;
}) => {
  const maxSentimentValue = Math.max(
    article.positiveRate,
    article.negativeRate,
    article.neutralRate
  );
  return (
    <div className="p-6 w-full space-y-4">
      <img
        className="w-full h-64 rounded-xl object-cover"
        src={article.imageUrl}
        alt={`Hình ảnh cho bài viết ${article.title}`}
      />
      <div className="space-y-2">
        <div className="flex flex-row items-center space-x-1">
          <img
            src={article.sourceImageUrl}
            className="h-4"
            alt={`${article.sourceName} logo`}
          />
          <p className="text-sm font-medium uppercase">
            {article.sourceName.replace(".", "")}
          </p>
          <p className="text-sm text-gray-40">·</p>
          <p className="text-sm text-gray-40">
            {article.publishDate.toLocaleString()}
          </p>
        </div>
        <h4 className="text-lg font-bold text-gray-100">{article.title}</h4>
        <p className="text-body text-gray-60">{article.description}</p>
        {maxSentimentValue == article.positiveRate && (
          <p className="text-sm font-medium text-green">
            {`${article.positiveRate.toFixed(0)}% `}
            tích cực
          </p>
        )}
        {maxSentimentValue == article.negativeRate && (
          <p className="text-sm font-medium text-red">
            {`${article.negativeRate.toFixed(0)}% `}
            tiêu cực
          </p>
        )}
      </div>
    </div>
  );
};
