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
import { ReactComponent as BriefcaseMedical } from "../components/icons/categories/BriefcaseMedical.svg";
import { ReactComponent as DocumentSearch } from "../components/icons/categories/DocumentSearch.svg";
import { ReactComponent as Earth } from "../components/icons/categories/Earth.svg";
import { ReactComponent as HatGraduation } from "../components/icons/categories/HatGraduation.svg";
import { ReactComponent as Money } from "../components/icons/categories/Money.svg";
import { ReactComponent as Music } from "../components/icons/categories/Music.svg";
import { ReactComponent as New } from "../components/icons/categories/New.svg";
import { ReactComponent as News } from "../components/icons/categories/News.svg";
import { ReactComponent as People } from "../components/icons/categories/People.svg";
import { ReactComponent as Sport } from "../components/icons/categories/Sport.svg";
import { ReactComponent as Technology } from "../components/icons/categories/Technology.svg";
import Loading from "../components/Loading";
import Link from "../components/Link";
import Logo from "../components/Logo";
import { MainLayout } from "../components/MainLayout";
import LoadingPage from "../components/LoadingPage";

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

  // Lazy loading
  const [isLazyLoading, setIsLazyLoading] = useState<boolean>(false);
  const [lazyLoadingHasMore, setLazyLoadingHasMore] = useState<boolean>(true);

  const [error, setError] = useState<string>();
  const [navigating, setNavigating] = useState<boolean>(false);
  const navigate = useNavigate();
  const { passedTrend } = (useLocation().state as { passedTrend?: Trend }) || {
    passedTrend: undefined,
  };

  useEffect(() => {
    const listener = () => handleLazyScroll(trend);
    window.addEventListener("scroll", listener);
    return () => window.removeEventListener("scroll", listener);
  }, [trend, lazyLoadingHasMore, isLazyLoading]);

  const handleLazyScroll = (trend?: Trend) => {
    if (
      document.documentElement.scrollTop + 4 * window.innerHeight <
        document.documentElement.offsetHeight ||
      isLazyLoading ||
      !lazyLoadingHasMore ||
      !trend
    )
      return;
    handleLoadMore(trend);
  };

  const handleLoadMore = (trend: Trend) => {
    setIsLazyLoading(true);
    if (trend?.topics) {
      const page_size = 10;
      const page = Math.ceil(trend?.topics.length / page_size);
      axios
        .get(
          `${API_URL}/trending/byid?trend_id=${trend?.id}&page=${page}&page_size=${page_size}`
        )
        .then((res) => {
          const data: Trend = res.data;
          trend.topics = [...trend.topics, ...data.topics];
          setTrend(trend);
          setLazyLoadingHasMore(data.hasMoreTopics || false);
        })
        .finally(() => setIsLazyLoading(false));
    }
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

      // reset lazyloading
      setIsLazyLoading(false);
      setLazyLoadingHasMore(true);

      navigate(location.pathname, { state: {}, replace: true }); // Clear location state
      setNavigating(false);
    }
  }, [trendCategory]);

  if (loading && !memorized) {
    return <LoadingPage error={error} />;
  }

  return (
    <MainLayout>
      <div className="p-8 flex flex-col justify-center items-center">
        <Logo />
      </div>
      <div className="flex flex-row flex-wrap mb-4 max-w-screen-md px-4 gap-x-2 gap-y-2 justify-center">
        {trend?.availableCategories &&
          Object.entries(trend?.availableCategories).map(([key, value]) => (
            <CategoryNavigationChip
              key={key}
              catId={key}
              category={value}
              current={trendCategory == key}
              onClick={() => {
                if (trendCategory == key) return;
                setNavigating(true);
                axios.get(`${API_URL}/trending/category/${key}`).then((res) => {
                  navigate(`/${key}`, {
                    state: { passedTrend: res.data },
                  });
                });
              }}
            />
          ))}
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
            trendId={trend.id}
            topicIndex={index}
            navigateToTopic={() => {
              setNavigating(true);
              axios.get(`${API_URL}/topic/${trend.id}/${index}`).then((res) => {
                navigate(`/topic/${trend.id}/${index}`, {
                  state: { passedTopic: res.data },
                });
              });
            }}
          />
        ))}
      </Masonry>
      <div className="py-8">
        {isLazyLoading && <Loading />}
        {!lazyLoadingHasMore && <Text>Đến đây là hết.</Text>}
      </div>
      {<Overlay enabled={navigating} />}
    </MainLayout>
  );
};

const MAP_CATEGORY_TO_ICON: {
  [key: string]: React.FunctionComponent<
    React.SVGProps<SVGSVGElement> & {
      title?: string | undefined;
    }
  >;
} = {
  "suc-khoe": BriefcaseMedical,
  "phap-luat": DocumentSearch,
  "the-gioi": Earth,
  "giao-duc": HatGraduation,
  "kinh-doanh": Money,
  "giai-tri": Music,
  "moi-nhat": New,
  "thoi-su": News,
  "van-hoa": People,
  "the-thao": Sport,
  "cong-nghe": Technology,
};

const CategoryNavigationChip = ({
  catId,
  category,
  current,
  onClick,
}: {
  catId: string;
  category: string;
  current: boolean;
  onClick?: () => void;
}) => {
  let CatIcon:
    | React.FunctionComponent<
        React.SVGProps<SVGSVGElement> & {
          title?: string | undefined;
        }
      >
    | undefined = undefined;
  if (catId in MAP_CATEGORY_TO_ICON) {
    CatIcon = MAP_CATEGORY_TO_ICON[catId];
  }
  const stroke = current ? "outline outline-2 outline-gray-40" : "";
  return (
    <Link
      className={`flex flex-row items-center gap-2 px-3 py-1 bg-white rounded-xl group ${stroke}`}
      onClick={onClick}
      href={`/${catId}`}
    >
      {CatIcon ? <CatIcon /> : undefined}
      <Text
        fontSize="body"
        fontWeight="medium"
        className="group-hover:underline"
      >
        {category}
      </Text>
    </Link>
  );
};
