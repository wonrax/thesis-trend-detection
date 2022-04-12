import MockData from "../test/data";
import { useEffect, useState } from "react";
import ArticleCard from "../components/ArticleCard";

export const Homepage = () => {
  const [topics, setTopics] = useState<
    Array<ReturnType<typeof MockData.getRandomArticle>[]>
  >([]);

  useEffect(() => {
    const topics: Array<ReturnType<typeof MockData.getRandomArticle>[]> =
      new Array(Math.floor(Math.random() * 8)).fill(null);
    setTopics(
      topics.map(() => {
        const articles: ReturnType<typeof MockData.getRandomArticle>[] =
          new Array(Math.floor(Math.random() * 5)).fill(null);
        return articles.map(() => MockData.getRandomArticle());
      })
    );
  }, []);

  return (
    <div className="bg-gray-0 min-h-screen">
      <div className="p-8 flex flex-col justify-center items-center">
        <h3 className="text-xl inline text-gray-100">Các chủ đề nổi bật về</h3>
        <h3 className="text-xl inline font-bold text-gray-100">Sức khỏe</h3>
      </div>
      <div className="space-y-2">
        {topics.map((articles) =>
          articles.map((article) => (
            <ArticleCard key={article.id} article={article} compact />
          ))
        )}
      </div>
    </div>
  );
};
