import Text from "../components/Text";
import { useEffect, useState } from "react";
import TopicSection from "../components/TopicSection";
import axios from "axios";
import Trend from "../models/Trend";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import Overlay from "../components/Overlay";
import Masonry from "react-masonry-css";
import styles from "./TrendPage.module.css";
import { API_URL } from "../constants";

const breakpointColumnsObj = {
  default: 3,
  1280: 2,
  768: 1,
};

export const TrendPage = ({
  trend,
  setTrend,
}: {
  trend: Trend | undefined;
  setTrend: React.Dispatch<React.SetStateAction<Trend | undefined>>;
}) => {
  const { trendCategory } = useParams();
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>();
  const [navigating, setNavigating] = useState<boolean>(false);
  const navigate = useNavigate();
  const { passedTrend } = (useLocation().state as { passedTrend?: Trend }) || {
    passedTrend: undefined,
  };

  const memorized =
    passedTrend ||
    (trend &&
      trend.availableCategories &&
      trendCategory &&
      trend.categoryName == trend.availableCategories[trendCategory]);

  useEffect(() => {
    if (!memorized) {
      setLoading(true);
      axios
        .get(`${API_URL}/trending/category/${trendCategory}`)
        .then((res) => {
          const data: Trend = res.data;
          setTrend(data);
          setLoading(false);
        })
        .catch(() => {
          setError("Không thể tải dữ liệu. Vui lòng thử tải lại trang.");
        });
    } else if (passedTrend) {
      setTrend(passedTrend);
      navigate(location.pathname, { state: {}, replace: true }); // Clear location state
      setNavigating(false);
    }
  }, [trendCategory]);

  if (loading && !memorized) {
    return (
      <>
        <div className="w-screen h-screen flex flex-col gap-2 items-center justify-center bg-gray-0">
          <Text fontSize="xxl" fontWeight="medium" className="animate-pulse">
            Xu hướng
          </Text>
          {error && <Text color="red">{error}</Text>}
        </div>
      </>
    );
  }

  return (
    <div className="w-full bg-gray-0">
      <div className="min-h-screen m-auto py-8 px-2 sm:px-16 md:px-4 xl:px-0 xl:w-[1280px]">
        <div className="p-8 flex flex-col justify-center items-center">
          <Text
            fontSize="xxl"
            fontWeight="medium"
            className="hover:underline cursor-pointer"
            onClick={() => navigate("/")}
          >
            Xu hướng
          </Text>
        </div>
        <div className="flex flex-row flex-wrap mb-4 gap-x-4 gap-y-2 justify-center">
          {trend?.availableCategories &&
            Object.entries(trend?.availableCategories).map(([key, value]) => {
              if (trendCategory == key)
                return (
                  <Text
                    key={key}
                    fontSize="body"
                    fontWeight="medium"
                    color="gray-20"
                  >
                    {value}
                  </Text>
                );
              return (
                <div
                  key={key}
                  onClick={() => {
                    setNavigating(true);
                    axios
                      .get(`${API_URL}/trending/category/${key}`)
                      .then((res) => {
                        navigate(`/${key}`, {
                          state: { passedTrend: res.data },
                        });
                      });
                  }}
                >
                  <Text
                    fontSize="body"
                    fontWeight="medium"
                    className="hover:underline cursor-pointer"
                  >
                    {value}
                  </Text>
                </div>
              );
            })}
        </div>
        {trend?.topics?.length == 0 && (
          <Text className="p-4" fontSize="lg" textAlign="center">
            Hôm nay không có tin gì mới, mời bạn quay lại sau.
          </Text>
        )}
        <Masonry
          breakpointCols={breakpointColumnsObj}
          className={styles["my-masonry-grid"]}
          columnClassName={styles["my-masonry-grid_column"]}
        >
          {/* array of JSX items */}
          {trend?.topics.map((topic, index) => (
            <TopicSection
              key={`${trend.id}-${index}`}
              spotlightArticle={topic.articles[0]}
              articles={topic.articles.slice(1)}
              keywords={topic.keywords}
              totalNumberOfArticles={topic.totalNumberOfArticles}
              hasMore={topic.hasMoreArticles}
              rank={index + 1}
              navigateToTopic={() => {
                setNavigating(true);
                axios
                  .get(`${API_URL}/topic/${trend.id}/${index}`)
                  .then((res) => {
                    navigate(`/topic/${trend.id}/${index}`, {
                      state: { passedTopic: res.data },
                    });
                  });
              }}
            />
          ))}
        </Masonry>
      </div>
      {<Overlay enabled={navigating} />}
    </div>
  );
};
