import React from "react";

export const Link = ({
  className,
  onClick,
  href,
  children,
}: {
  className?: string;
  onClick?: () => void;
  href: string;
  children?: React.ReactNode;
}) => {
  function _onClick(e: React.MouseEvent<HTMLAnchorElement>) {
    if (onClick) {
      onClick();
    }
    e.preventDefault();
  }

  return (
    <a href={href} onClick={_onClick} className={className}>
      {children}
    </a>
  );
};

export default Link;
