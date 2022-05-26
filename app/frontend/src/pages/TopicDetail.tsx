import Text from "../components/Text";
import { useEffect, useState } from "react";
import TopicSection from "../components/TopicSection";
import axios from "axios";
import Topic from "../models/Topic";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import Overlay from "../components/Overlay";
import { API_URL } from "../constants";
import Logo from "../components/Logo";
import LoadingPage from "../components/LoadingPage";

export const TopicDetail = () => {
  const [topic, setTopic] = useState<Topic>();
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>();
  const { id, index } = useParams();
  const { passedTopic } = (useLocation().state as { passedTopic?: Topic }) || {
    passedTopic: undefined,
  };
  const navigate = useNavigate();

  useEffect(() => {
    if (passedTopic) {
      setTopic(passedTopic);
    } else {
      axios
        .get(`${API_URL}/topic/${id}/${index}`)
        .then((res) => {
          setTopic(res.data);
          setLoading(false);
        })
        .catch(() => {
          setError("Không thể tải dữ liệu. Vui lòng thử tải lại trang.");
        });
    }
    navigate(location.pathname, { state: {}, replace: true }); // Clear location state
  }, []);

  if (loading && !passedTopic) {
    return <LoadingPage error={error} />;
  }

  return (
    <div className="w-full bg-gray-0">
      <div className="min-h-screen m-auto py-8 p-2 sm:w-[512px]">
        <div className="p-8 flex flex-col justify-center items-center">
          <Logo />
        </div>
        <div className="p-4">
          <Text renderAs="span" fontSize="lg">
            Các bài viết về
          </Text>
          <Text
            className="ml-2"
            renderAs="span"
            fontSize="lg"
            fontWeight="medium"
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
