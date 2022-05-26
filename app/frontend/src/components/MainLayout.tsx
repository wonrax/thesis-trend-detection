export const MainLayout = ({
  isTopicDetail,
  children,
}: {
  isTopicDetail?: boolean;
  children: React.ReactNode;
}) => {
  return (
    <div className="w-full bg-gray-0">
      <div
        className={`flex flex-col items-center min-h-screen m-auto py-8 px-2 sm:px-16 md:px-8 xl:px-0 ${
          isTopicDetail
            ? "md:max-w-[960px] xl:w-[960px]"
            : "md:max-w-[1280px] xl:w-[1280px]"
        }`}
      >
        {children}
      </div>
    </div>
  );
};
