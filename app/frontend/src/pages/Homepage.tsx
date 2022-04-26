import Text from "../components/Text";
import { useEffect, useState } from "react";
import TopicSection from "../components/TopicSection";
import axios from "axios";
import Trend from "../models/Trend";

export const Homepage = () => {
  const [trend, setTrend] = useState<Trend>();

  useEffect(() => {
    axios
      .get("http://localhost:5000/trending/category/moi_nhat")
      .then((res) => {
        setTrend(res.data);
      });
  }, []);

  return (
    <div className="w-full bg-gray-0">
      <div className="min-h-screen m-auto py-8 p-2 sm:w-[512px]">
        <div className="p-8 flex flex-col justify-center items-center">
          <h3 className="text-xl inline text-gray-100">Xu hướng trong</h3>
          <h3 className="text-xl inline font-bold text-gray-100">
            {trend?.categoryName}
          </h3>
        </div>
        {trend?.topics?.length == 0 && (
          <Text className="p-4" fontSize="lg" textAlign="center">
            Hôm nay không có tin gì mới, mời bạn quay lại sau.
          </Text>
        )}
        <div className="space-y-4">
          {trend?.topics.map((topic, index) => (
            <TopicSection
              key={index}
              spotlightArticle={topic.articles[0]}
              articles={topic.articles.slice(1)}
              keywords={topic.keywords}
              hasMore={topic.hasMoreArticles}
              trendId={trend.id}
              topicIndex={index}
            />
          ))}
        </div>
      </div>
    </div>
  );
};
