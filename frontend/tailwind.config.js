/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        arena: {
          50: "#fff1f2",
          100: "#ffe4e6",
          500: "#e11d48",
          600: "#be123c",
          700: "#9f1239",
        },
      },
    },
  },
  plugins: [],
};
