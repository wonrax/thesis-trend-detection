import Text from "../components/Text";
import { useEffect, useState } from "react";
import TopicSection from "../components/TopicSection";
import axios from "axios";
import Topic from "../models/Topic";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import Overlay from "../components/Overlay";
import { API_URL } from "../constants";

export const TopicDetail = () => {
  const [topic, setTopic] = useState<Topic>();
  const [loading, setLoading] = useState<boolean>(true);
  const { id, index } = useParams();
  const { passedTopic } = (useLocation().state as { passedTopic?: Topic }) || {
    passedTopic: undefined,
  };
  const navigate = useNavigate();

  useEffect(() => {
    if (passedTopic) {
      setTopic(passedTopic);
    } else {
      axios.get(`${API_URL}/topic/${id}/${index}`).then((res) => {
        setTopic(res.data);
        setLoading(false);
      });
    }
  }, []);

  if (loading && !passedTopic) {
    return (
      <>
        <div className="w-screen h-screen flex items-center justify-center bg-gray-0">
          <Text fontSize="xxl" fontWeight="bold" className="animate-pulse">
            Xu hướng
          </Text>
        </div>
      </>
    );
  }

  return (
    <div className="w-full bg-gray-0">
      <div className="min-h-screen m-auto py-8 p-2 sm:w-[512px]">
        <div className="p-8 flex flex-col justify-center items-center">
          <Text
            fontSize="xxl"
            fontWeight="bold"
            className="hover:underline cursor-pointer"
            onClick={() => navigate("/")}
          >
            Xu hướng
          </Text>
        </div>
        <div className="p-4">
          <Text renderAs="span" fontSize="lg">
            Các bài viết về
          </Text>
          <Text
            className="ml-2"
            renderAs="span"
            fontSize="lg"
            fontWeight="bold"
            leading="tight"
          >{`${topic?.keywords?.at(0)}, ${topic?.keywords?.at(1)}`}</Text>
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
      {<ScrollToTop />}
    </div>
  );
};

const ScrollToTop = () => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return null;
};
