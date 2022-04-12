import classnames from "classnames";

const MAP_FONT_SIZE_TO_TAG = {
  sm: "p",
  body: "p",
  lg: "h4",
  xl: "h3",
};

export const Text = ({
  className,
  fontSize = "body",
  fontWeight = "normal",
  color = "gray-100",
  textAlign = "left",
  renderAs,
  uppercase = false,
  capitalize = false,
  ellipsis = false,
  nowrap = false,
  leading = "normal",
  children,
  ...props
}: {
  className?: string;
  fontSize?: "sm" | "body" | "lg" | "xl";
  fontWeight?: "normal" | "bold" | "medium";
  color?:
    | "gray-100"
    | "gray-80"
    | "gray-60"
    | "gray-40"
    | "gray-20"
    | "gray-0"
    | "red"
    | "green"
    | "white";
  textAlign?: "left" | "center" | "right";
  renderAs?: string;
  uppercase?: boolean;
  capitalize?: boolean;
  ellipsis?: boolean;
  nowrap?: boolean;
  leading?: "normal" | "tight";
  children: React.ReactNode;
}) => {
  const classNames = classnames(
    `text-${fontSize}`,
    `font-${fontWeight}`,
    `text-${color}`,
    `text-${textAlign}`,
    `leading-${leading}`,
    className,
    {
      uppercase: uppercase,
      capitalize: capitalize,
      truncate: ellipsis,
      "overflow-hidden": ellipsis,
      "whitespace-nowrap": nowrap,
    }
  );

  const Tag =
    (renderAs as keyof JSX.IntrinsicElements) ||
    (MAP_FONT_SIZE_TO_TAG[fontSize] as keyof JSX.IntrinsicElements);

  return (
    <Tag className={classNames} {...props}>
      {children}
    </Tag>
  );
};
