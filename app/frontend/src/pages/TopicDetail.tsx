import Text from "../components/Text";
import { useEffect, useState } from "react";
import TopicSection from "../components/TopicSection";
import axios from "axios";
import Topic from "../models/Topic";
import { useParams } from "react-router-dom";

export const TopicDetail = () => {
  const [topic, setTopic] = useState<Topic>();
  const { id, index } = useParams();

  useEffect(() => {
    axios.get(`http://localhost:5000/topic/${id}/${index}`).then((res) => {
      setTopic(res.data);
    });
  }, []);

  return (
    <div className="w-full bg-gray-0">
      <div className="min-h-screen m-auto py-8 p-2 sm:w-[512px]">
        <div className="p-8 flex flex-col justify-center items-center">
          <h3 className="text-xl inline text-gray-100">Các bài viết về</h3>
          <h3 className="text-xl inline font-bold text-gray-100">
            {`${topic?.keywords?.at(0)}, ${topic?.keywords?.at(1)}`}
          </h3>
        </div>
        {topic?.articles.length == 0 && (
          <Text className="p-4" fontSize="lg" textAlign="center">
            Không có bài nào.
          </Text>
        )}
        {topic && (
          <TopicSection
            key={index}
            spotlightArticle={topic.articles[0]}
            articles={topic.articles.slice(1)}
            showThumbnail={true}
            keywords={topic.keywords}
            hasMore={topic.hasMoreArticles}
          />
        )}
      </div>
    </div>
  );
};
