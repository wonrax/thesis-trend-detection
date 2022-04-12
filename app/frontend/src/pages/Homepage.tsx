import MockData from "../test/data";
import Text from "../components/Text";
import { useEffect, useState } from "react";
import TopicSection from "../components/TopicSection";

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
    <div className="w-full bg-gray-0">
      <div className="min-h-screen m-auto py-8 p-2 sm:w-[512px]">
        <div className="p-8 flex flex-col justify-center items-center">
          <h3 className="text-xl inline text-gray-100">
            Các chủ đề nổi bật về
          </h3>
          <h3 className="text-xl inline font-bold text-gray-100">Sức khỏe</h3>
        </div>
        {topics.length == 0 && (
          <Text className="p-4" fontSize="lg" textAlign="center">
            Hôm nay không có tin gì mới, mời bạn quay lại sau.
          </Text>
        )}
        <div className="space-y-2">
          {topics.map((articles) => (
            <TopicSection
              spotlightArticle={articles[0]}
              articles={articles.slice(1)}
              hasMore={Math.random() > 0.3}
            />
          ))}
        </div>
      </div>
    </div>
  );
};
