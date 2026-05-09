import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#102a43",
        mint: "#4fd1c5",
        cream: "#fff8e8"
      }
    }
  },
  plugins: []
};

export default config;
