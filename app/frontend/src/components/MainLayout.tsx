export const MainLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="w-full bg-gray-0">
      <div className="flex flex-col items-center min-h-screen m-auto py-8 px-2 sm:px-16 md:px-4 xl:px-0 xl:w-[1280px]">
        {children}
      </div>
    </div>
  );
};
