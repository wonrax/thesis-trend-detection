import Topic from "./Topic";

export type Category = {
  topics: Topic[];
  creationDate: Date;
  categoryName: string;
};

export default Category;
