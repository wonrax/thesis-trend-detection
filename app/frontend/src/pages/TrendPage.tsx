import Text from "../components/Text";
import { useEffect, useState } from "react";
import TopicSection from "../components/TopicSection";
import axios from "axios";
import Trend from "../models/Trend";
import { useNavigate, useParams } from "react-router-dom";

export const TrendPage = ({
  trend,
  setTrend,
  scrollPosition,
  setScrollPosition,
}: {
  trend: Trend | undefined;
  setTrend: React.Dispatch<React.SetStateAction<Trend | undefined>>;
  scrollPosition: number;
  setScrollPosition: React.Dispatch<React.SetStateAction<number>>;
}) => {
  const { trendCategory } = useParams();
  const [loading, setLoading] = useState<boolean>(true);
  const navigate = useNavigate();

  const handleScroll = () => {
    const position = window.pageYOffset;
    setScrollPosition(position);
    console.log(position);
  };

  useEffect(() => {
    const oldScrollPosition = scrollPosition;
    window.addEventListener("scroll", handleScroll, { passive: true });
    if (
      trend &&
      trend.availableCategories &&
      trendCategory &&
      trend.categoryName == trend.availableCategories[trendCategory]
    ) {
      setLoading(false);
      if (oldScrollPosition) {
        console.log("setting scroll at", oldScrollPosition);
        window.scrollTo(0, oldScrollPosition);
      }
    } else {
      setLoading(true);
      axios
        .get(`http://localhost:5000/trending/category/${trendCategory}`)
        .then((res) => {
          setTrend(res.data);
          setLoading(false);
        });
    }
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, [trendCategory]);

  if (loading) {
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
          <h3 className="text-xl inline text-gray-100">Xu hướng trong</h3>
          <h3 className="text-xl inline font-bold text-gray-100">
            {trend?.categoryName}
          </h3>
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
                <div onClick={() => navigate(`/${key}`)}>
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
              trendId={trend.id}
              topicIndex={index}
            />
          ))}
        </div>
      </div>
    </div>
  );
};
