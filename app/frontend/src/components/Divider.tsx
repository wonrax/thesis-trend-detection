import classNames from "classnames";

export const Divider = ({
  darker,
  className,
}: {
  darker?: boolean;
  className?: string;
}) => {
  const cs = classNames(
    `w-full h-[1px] ${darker ? "bg-gray-10" : "bg-gray-0"}`,
    className
  );
  return <div className={cs} />;
};

export default Divider;
