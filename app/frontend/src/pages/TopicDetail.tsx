import Text from "../components/Text";
import { useEffect, useState } from "react";
import axios from "axios";
import Topic from "../models/Topic";
import { useParams, useLocation } from "react-router-dom";
import Overlay from "../components/Overlay";
import { API_URL } from "../constants";
import Logo from "../components/Logo";
import LoadingPage from "../components/LoadingPage";
import { MainLayout } from "../components/MainLayout";
import Masonry from "react-masonry-css";
import styles from "./TopicDetail.module.css";
import ArticleCard from "../components/ArticleCard";
import Divider from "../components/Divider";

const breakpointColumnsObj = {
  default: 2,
  1280: 2,
  768: 1,
};

export const TopicDetail = () => {
  const [topic, setTopic] = useState<Topic>();
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>();
  const { id, index } = useParams();
  const { passedTopic } = (useLocation().state as { passedTopic?: Topic }) || {
    passedTopic: undefined,
  };

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
  }, [id, index]);

  if (loading && !passedTopic) {
    return <LoadingPage error={error} />;
  }

  return (
    <MainLayout isTopicDetail>
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
      <Divider darker className="mb-4" />
      {topic?.articles.length == 0 && (
        <Text className="p-4" fontSize="lg" textAlign="center">
          Không có bài nào.
        </Text>
      )}
      {topic && (
        <Masonry
          breakpointCols={breakpointColumnsObj}
          className={styles["my-masonry-grid"]}
          columnClassName={styles["my-masonry-grid_column"]}
        >
          {/* array of JSX items */}
          {topic.articles.map((article) => (
            <ArticleCard key={article.id} article={article} showThumbnail />
          ))}
        </Masonry>
      )}
      {<Overlay enabled={!topic} />}
      {<ScrollToTop />}
    </MainLayout>
  );
};

const ScrollToTop = () => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return null;
};
