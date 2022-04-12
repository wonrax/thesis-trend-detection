import { LoremIpsum } from "lorem-ipsum";
import Article from "../models/Article";

function getRandomArticle(): Article {
  const loremGenerator = new LoremIpsum({
    wordsPerSentence: {
      max: 14,
      min: 4,
    },
  });

  const sourceNameGenerator = new LoremIpsum({
    wordsPerSentence: {
      max: 3,
      min: 2,
    },
  });

  let positiveRate = undefined;
  let negativeRate = undefined;
  let neutralRate = undefined;

  if (Math.random() > 0.4) {
    positiveRate = Math.random() * 100;
    negativeRate = Math.random() * (100 - positiveRate);
    neutralRate = 100 - positiveRate - negativeRate;
  }

  const now = new Date();
  const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

  let sourceLogoUrl = undefined;
  if (Math.random() > 0.5) {
    sourceLogoUrl = `https://source.unsplash.com/random/64x64?a=${Math.random()}`;
  }
  if (Math.random() > 0.5) {
    sourceLogoUrl = `https://source.unsplash.com/random/256x64?a=${Math.random()}`;
  }

  return {
    id: Math.floor(Math.random() * 1000).toString(),
    thumbnailUrl:
      Math.random() > 0.1
        ? `https://source.unsplash.com/random/600x400?a=${Math.random()}`
        : undefined,
    title: loremGenerator.generateSentences(1),
    articleUrl: Math.random() > 0.1 ? "#" : undefined,
    description:
      Math.random() > 0.1 ? loremGenerator.generateSentences(2) : undefined,
    publishDate:
      Math.random() > 0.01 ? getRandomDate(oneDayAgo, now) : undefined,
    sourceName:
      Math.random() > 0.1
        ? formatTitleCase(
            sourceNameGenerator.generateSentences(1).replace(".", "")
          )
        : undefined,
    sourceLogoUrl,
    positiveRate,
    negativeRate,
    neutralRate,
  };
}

function getRandomDate(from: Date, to: Date) {
  const fromTime = from.getTime();
  const toTime = to.getTime();
  return new Date(fromTime + Math.random() * (toTime - fromTime));
}

const formatTitleCase = (string: string) =>
  string
    .toLowerCase()
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.substring(1))
    .join(" ");

const MockData = { getRandomArticle };
export default MockData;
