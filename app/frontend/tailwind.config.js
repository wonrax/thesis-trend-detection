module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      screens: {
        mobile: "300px",
      },
    },
    fontSize: {
      sm: [
        "12px",
        {
          lineHeight: "1.25em",
        },
      ],
      body: [
        "15px",
        {
          lineHeight: "1.25em",
        },
      ],
      lg: [
        "24px",
        {
          letterSpacing: "-0.02em",
          lineHeight: "1.25em",
        },
      ],
      xl: [
        "28px",
        {
          letterSpacing: "-0.03em",
          lineHeight: "1.25em",
        },
      ],
    },
    colors: {
      white: "#ffffff",
      gray: {
        100: "#252025",
        80: "#413D43",
        60: "#605F64",
        40: "#888A8E",
        20: "#BBBEBE",
        0: "#F2F3F2",
      },
      red: "#DF4C6F",
      green: "#329F7F",
    },
    borderRadius: {
      DEFAULT: "0",
      xs: "4px",
      md: "16px",
      lg: "24px",
      xl: "32px",
    },
  },
  safelist: [
    {
      pattern: /text-(gray|white|red|green)(-(100|80|60|40|20|0))?/,
    },
    {
      pattern: /text-(sm|body|lg|xl)/,
    },
    {
      pattern: /text-(left|center|right)/,
    },
    {
      pattern: /leading-(normal|tight)/,
    },
    {
      pattern: /font-(normal|bold|medium)/,
    },
  ],
  plugins: [],
};
