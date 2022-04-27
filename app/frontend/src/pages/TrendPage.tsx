import Text from "../components/Text";
import { useEffect, useState } from "react";
import TopicSection from "../components/TopicSection";
import axios from "axios";
import Trend from "../models/Trend";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import Overlay from "../components/Overlay";

export const TrendPage = ({
  trend,
  setTrend,
}: {
  trend: Trend | undefined;
  setTrend: React.Dispatch<React.SetStateAction<Trend | undefined>>;
}) => {
  const { trendCategory } = useParams();
  const [loading, setLoading] = useState<boolean>(true);
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
        .get(`http://localhost:5000/trending/category/${trendCategory}`)
        .then((res) => {
          setTrend(res.data);
          setLoading(false);
        });
    } else if (passedTrend) {
      setTrend(passedTrend);
      setNavigating(false);
    }
  }, [trendCategory]);

  if (loading && !memorized) {
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
        <div className="flex flex-row flex-wrap mb-4 gap-x-4 gap-y-2 justify-center">
          {trend?.availableCategories &&
            Object.entries(trend?.availableCategories).map(([key, value]) => {
              if (trendCategory == key)
                return (
                  <Text fontSize="body" fontWeight="medium" color="gray-20">
                    {value}
                  </Text>
                );
              return (
                <div
                  onClick={() => {
                    setNavigating(true);
                    axios
                      .get(`http://localhost:5000/trending/category/${key}`)
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
        <div className="space-y-4">
          {trend?.topics.map((topic, index) => (
            <TopicSection
              key={index}
              spotlightArticle={topic.articles[0]}
              articles={topic.articles.slice(1)}
              keywords={topic.keywords}
              hasMore={topic.hasMoreArticles}
              navigateToTopic={() => {
                setNavigating(true);
                axios
                  .get(`http://localhost:5000/topic/${trend.id}/${index}`)
                  .then((res) => {
                    navigate(`/topic/${trend.id}/${index}`, {
                      state: { passedTopic: res.data },
                    });
                  });
              }}
            />
          ))}
        </div>
      </div>
      {<Overlay enabled={navigating} />}
    </div>
  );
};
