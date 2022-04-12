export type Article = {
  id: string;
  thumbnailUrl?: string;
  title?: string;
  articleUrl?: string;
  description?: string;
  publishDate?: Date;
  sourceName?: string;
  sourceLogoUrl?: string;
  positiveRate?: number;
  negativeRate?: number;
  neutralRate?: number;
};

export default Article;
