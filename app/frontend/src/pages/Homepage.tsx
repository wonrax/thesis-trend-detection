import MockData from "../test/data";
import Text from "../components/Text";
import { useEffect, useState } from "react";
import TopicSection from "../components/TopicSection";
import axios from "axios";
import Category from "../models/Category";

export const Homepage = () => {
  const [category, setCategory] = useState<Category>();

  useEffect(() => {
    axios
      .get("http://localhost:5000/trending/category/moi_nhat")
      .then((res) => {
        setCategory(res.data);
      });
  }, []);

  return (
    <div className="w-full bg-gray-0">
      <div className="min-h-screen m-auto py-8 p-2 sm:w-[512px]">
        <div className="p-8 flex flex-col justify-center items-center">
          <h3 className="text-xl inline text-gray-100">Xu hướng trong</h3>
          <h3 className="text-xl inline font-bold text-gray-100">
            {category?.categoryName}
          </h3>
        </div>
        {category?.topics?.length == 0 && (
          <Text className="p-4" fontSize="lg" textAlign="center">
            Hôm nay không có tin gì mới, mời bạn quay lại sau.
          </Text>
        )}
        <div className="space-y-2">
          {category?.topics.map((topic, index) => (
            <TopicSection
              key={index}
              spotlightArticle={topic.articles[0]}
              articles={topic.articles.slice(1)}
              hasMore={false}
            />
          ))}
        </div>
      </div>
    </div>
  );
};
