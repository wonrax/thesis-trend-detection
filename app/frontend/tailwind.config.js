module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {},
    spacing: {
      1: "4px",
      2: "8px",
      3: "12px",
      4: "16px",
      5: "20px",
      6: "24px",
      7: "28px",
      8: "32px",
    },
    fontSize: {
      sm: [
        "12px",
        {
          letterSpacing: "1em",
          lineHeight: "1.5em",
        },
      ],
      body: [
        "15px",
        {
          letterSpacing: "1em",
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
  },
  plugins: [],
};
