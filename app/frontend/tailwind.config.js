module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {},
    fontSize: {
      sm: [
        "13px",
        {
          lineHeight: "1.5em",
        },
      ],
      body: [
        "15px",
        {
          lineHeight: "1.5em",
        },
      ],
      lg: [
        "20px",
        {
          letterSpacing: "-0.02em",
          lineHeight: "1.25em",
        },
      ],
      xl: [
        "24px",
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
      xl: "24px",
      "2xl": "32px",
    },
  },
  safelist: [
    {
      pattern: /text-(gray|white|red|green)(-(100|80|60|40|20|0))?/,
    },
    {
      pattern: /text-(sm|body|lg|xl)/,
    },
  ],
  plugins: [],
};
