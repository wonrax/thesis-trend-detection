export type Article = {
  id: string;
  imageUrl?: string;
  title?: string;
  description?: string;
  publishDate?: Date;
  sourceName?: string;
  sourceLogoUrl?: string;
  positiveRate?: number;
  negativeRate?: number;
  neutralRate?: number;
};

export default Article;
