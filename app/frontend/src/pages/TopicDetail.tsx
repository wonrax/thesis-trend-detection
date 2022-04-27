import Text from "../components/Text";
import { useEffect, useState } from "react";
import TopicSection from "../components/TopicSection";
import axios from "axios";
import Topic from "../models/Topic";
import { useParams, useLocation } from "react-router-dom";
import Overlay from "../components/Overlay";

export const TopicDetail = () => {
  const [topic, setTopic] = useState<Topic>();
  const [loading, setLoading] = useState<boolean>(true);
  const { id, index } = useParams();
  const { passedTopic } = useLocation().state as { passedTopic: Topic };

  useEffect(() => {
    if (passedTopic) {
      setTopic(passedTopic);
    } else {
      axios.get(`http://localhost:5000/topic/${id}/${index}`).then((res) => {
        setTopic(res.data);
        setLoading(false);
      });
    }
  }, []);

  if (loading && !passedTopic) {
    return (
      <div className="w-screen h-screen flex items-center justify-center bg-gray-0">
        <Text fontSize="lg">Đang tải...</Text>
      </div>
    );
  }

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
      {<Overlay enabled={!topic} />}
    </div>
  );
};
