import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,       // use global functions like describe, it, expect
    environment: 'jsdom' // simulate browser DOM
  }
});
