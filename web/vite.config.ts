import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => ({
  base: mode === "development" ? "/" : "/Heryx/",
  plugins: [react()],
  build: {
    target: ["chrome89", "edge89", "firefox89", "safari15"]
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts"
  }
}));
