import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  // Root directory for source files
  root: path.resolve(__dirname, 'src'),
  
  build: {
    // Output directly to Django's static directory
    outDir: path.resolve(__dirname, '../static/music_app/js'),
    emptyOutDir: false,
    sourcemap: true,
    
    // Library mode - build individual TypeScript files
    rollupOptions: {
      input: {
        // Add my TypeScript entry points here
        passwordToggle: path.resolve(__dirname, './src/showPassword.ts'),
        validateEmail: path.resolve(__dirname, './src/validateEmail.ts'),
        validatePassword: path.resolve(__dirname, './src/validatePassword.ts'),
        validateStreamingLink: path.resolve(__dirname, './src/validateStreamingLink.ts'),
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]',
      }
    }
  },
  
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});