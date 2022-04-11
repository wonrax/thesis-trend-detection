import { LoremIpsum } from "lorem-ipsum";

function getRandomArticle() {
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

  const positiveRate = Math.random() * 100;
  const negativeRate = Math.random() * (100 - positiveRate);
  const neutralRate = 100 - positiveRate - negativeRate;

  const now = new Date();
  const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

  let sourceLogoUrl = "https://source.unsplash.com/random/64x64";
  if (Math.random() > 0.5) {
    sourceLogoUrl = "https://source.unsplash.com/random/256x64";
  }

  return {
    id: Math.floor(Math.random() * 1000).toString(),
    imageUrl: `https://source.unsplash.com/random/600x400?a=${Math.random()}`,
    title: loremGenerator.generateSentences(1),
    description: loremGenerator.generateSentences(2),
    publishDate: getRandomDate(oneDayAgo, now),
    sourceName: formatTitleCase(
      sourceNameGenerator.generateSentences(1).replace(".", "")
    ),
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
