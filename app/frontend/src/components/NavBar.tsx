import { ReactComponent as BriefcaseMedical } from "./icons/categories/BriefcaseMedical.svg";
import { ReactComponent as DocumentSearch } from "./icons/categories/DocumentSearch.svg";
import { ReactComponent as Earth } from "./icons/categories/Earth.svg";
import { ReactComponent as HatGraduation } from "./icons/categories/HatGraduation.svg";
import { ReactComponent as Money } from "./icons/categories/Money.svg";
import { ReactComponent as Music } from "./icons/categories/Music.svg";
import { ReactComponent as New } from "./icons/categories/New.svg";
import { ReactComponent as News } from "./icons/categories/News.svg";
import { ReactComponent as People } from "./icons/categories/People.svg";
import { ReactComponent as Sport } from "./icons/categories/Sport.svg";
import { ReactComponent as Technology } from "./icons/categories/Technology.svg";
import Link from "../components/Link";
import Text from "../components/Text";
import Logo from "../components/Logo";
import { useState, useEffect, useRef } from "react";

export const NavBar = ({
  categories,
  currentCategory,
  onClick,
}: {
  categories?: { [key: string]: string };
  currentCategory?: string;
  onClick: (categoryId: string) => void;
}) => {
  const [isShrunk, setShrunk] = useState(false);
  const [isNavBarOpen, setIsNavBarOpen] = useState(false);

  useEffect(() => {
    if (isNavBarOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
  }, [isNavBarOpen]);

  useEffect(() => {
    const handler = () => {
      setShrunk((isShrunk) => {
        if (
          !isShrunk &&
          (document.body.scrollTop > 62 ||
            document.documentElement.scrollTop > 62)
        ) {
          return true;
        }

        if (
          isShrunk &&
          document.body.scrollTop <= 0 &&
          document.documentElement.scrollTop <= 0
        ) {
          return false;
        }

        return isShrunk;
      });
    };

    window.addEventListener("scroll", handler);
    return () => window.removeEventListener("scroll", handler);
  }, []);

  const horizontalScrollRef = useHorizontalScroll();

  return (
    <nav
      className={`sticky top-0 bg-gray-0 w-full transition-all duration-300 ${
        isShrunk ? "py-1 shadow-sm" : "py-8"
      }`}
    >
      <section
        className={`mobile-nav lg:hidden ${
          isNavBarOpen && "h-screen"
        } overflow-y-scroll no-scrollbar`}
      >
        <div className="flex flex-row justify-between items-center px-8">
          <Logo />
          <div
            className="hamburger space-y-1.5 cursor-pointer"
            onClick={() => setIsNavBarOpen(!isNavBarOpen)}
          >
            <span className="block h-0.5 w-6 bg-gray-80"></span>
            <span className="block h-0.5 w-6 bg-gray-80"></span>
            <span className="block h-0.5 w-6 bg-gray-80"></span>
          </div>
        </div>
        <div
          className={`mobile-nav-open ${
            isNavBarOpen ? "flex" : "hidden"
          } flex-col gap-y-2 pt-2 pb-4 px-4`}
        >
          {categories &&
            Object.entries(categories).map(([key, value]) => (
              <CategoryNavigationChip
                key={key}
                catId={key}
                category={value}
                current={currentCategory == key}
                onClick={() => {
                  onClick(key);
                  setIsNavBarOpen(false);
                }}
                mobile
              />
            ))}
          <div className="h-8" />
        </div>
      </section>
      <section
        className={`desktop-nav hidden lg:flex flex-row gap-4 items-center px-8`}
      >
        <Logo />
        <div
          className=" overflow-x-scroll no-scrollbar"
          ref={horizontalScrollRef}
        >
          <div className={`flex flex-row px-4 py-1 gap-2 mx-1`}>
            {categories &&
              Object.entries(categories).map(([key, value]) => (
                <CategoryNavigationChip
                  key={key}
                  catId={key}
                  category={value}
                  current={currentCategory == key}
                  onClick={() => onClick(key)}
                />
              ))}
            <div className="w-4 shrink-0" />
          </div>
        </div>
        <div className="w-24 h-8 bg-gradient-to-r from-gray-0/0 to-gray-0 right-8 absolute pointer-events-none" />
      </section>
    </nav>
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
  mobile,
}: {
  catId: string;
  category: string;
  current: boolean;
  onClick?: () => void;
  mobile?: boolean;
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
      className={`flex flex-row items-center gap-2 px-3 bg-white ${
        mobile ? "py-3 rounded-md" : "py-1 rounded-xl"
      } group ${stroke}`}
      onClick={onClick}
      href={`/${catId}`}
    >
      {CatIcon ? <CatIcon /> : undefined}
      <Text
        fontSize="body"
        fontWeight="medium"
        className="group-hover:underline"
        nowrap
      >
        {category}
      </Text>
    </Link>
  );
};

export function useHorizontalScroll() {
  const elRef = useRef() as React.MutableRefObject<HTMLInputElement>;
  useEffect(() => {
    const el = elRef.current;
    if (el) {
      const onWheel = (e: { deltaY: number; preventDefault: () => void }) => {
        if (e.deltaY == 0) return;
        e.preventDefault();
        el.scrollTo({
          left: el.scrollLeft + e.deltaY,
          behavior: "smooth",
        });
      };
      el.addEventListener("wheel", onWheel);
      return () => el.removeEventListener("wheel", onWheel);
    }
  }, []);
  return elRef;
}

export default NavBar;
