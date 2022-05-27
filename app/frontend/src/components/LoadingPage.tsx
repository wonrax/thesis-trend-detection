import Text from "./Text";

export const LoadingPage = ({ error }: { error?: string }) => {
  return (
    <div className="w-screen h-screen flex flex-col gap-2 items-center justify-center bg-gray-0">
      <Text
        fontSize="xxl"
        fontWeight="medium"
        className={!error ? "animate-pulse" : undefined}
      >
        Xu hướng
      </Text>
      {error && <Text color="red">{error}</Text>}
    </div>
  );
};

export default LoadingPage;
