import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "node:path";

// The analytical export stays in ../web. Vite serves those data artifacts
// unchanged in development and copies them with a production build.
export default defineConfig({
  plugins: [react()],
  publicDir: resolve(import.meta.dirname, "../web"),
  build: { outDir: "dist", emptyOutDir: true },
});
