module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {},
    // spacing: {
    //   1: "4px",
    //   2: "8px",
    //   3: "12px",
    //   4: "16px",
    //   5: "20px",
    //   6: "24px",
    //   7: "28px",
    //   8: "32px",
    // },
    fontSize: {
      sm: [
        "12px",
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
      xl: "24px",
      "2xl": "32px",
    },
  },
  plugins: [],
};
