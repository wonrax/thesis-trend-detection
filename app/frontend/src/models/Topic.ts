import Article from "./Article";

export type Topic = {
  articles: Article[];
  keywords?: string[];
  averagePositiveRate?: number;
  averageNegativeRate?: number;
  averageNeutralRate?: number;
  totalNumberOfArticles?: number;
  hasMoreArticles?: boolean;
};

export default Topic;
