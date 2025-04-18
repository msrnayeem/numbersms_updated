/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/templates/**/*.html"],
  theme: {
    fontFamily: {
      arima: ["Arima", "system-ui"],
    },
    container: {
      center: true,
      padding: {
        DEFAULT: "1rem",
        sm: "1rem",
        lg: "7rem",
        xl: "8rem",
        "2xl": "9rem",
      },
    },
    extend: {
      colors: {
        primary: "#3E376C",
        bg: "#FDF9F0",
        dark: "#23282E",
        secondary: "#FC5D19",
      },
    },
  },
  plugins: [],
};
