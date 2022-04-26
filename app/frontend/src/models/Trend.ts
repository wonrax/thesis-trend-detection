import Topic from "./Topic";

export type Trend = {
  id: string;
  topics: Topic[];
  creationDate: Date;
  categoryName: string;
};

export default Trend;
