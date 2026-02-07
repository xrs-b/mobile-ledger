import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'AutoImport'
import styleImport from 'vite-plugin-style-import'
import { resolve } from 'path'
import pxtorem from 'postcss-pxtorem'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [
        (name) => {
          if (name === 'VanIcon') {
            return { importName: name, path: 'vant' }
          }
          if (['Button', 'Cell', 'CellGroup', 'Toast', 'Dialog', 'Notify'].includes(name)) {
            return { importName: name, path: 'vant' }
          }
          return { name, package: 'vant' }
        }
      ],
      imports: ['vue', 'vue-router', 'pinia'],
      dts: 'src/auto-imports.d.ts',
    }),
    styleImport({
      resolvers: [
        { resolveStyle(name) { return `vant/es/${name}/style/index.js` } },
      ],
    }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  css: {
    postcss: {
      plugins: [
        pxtorem({
          rootValue: 37.5, // 基于375px设计稿
          propList: ['*'],
          selectorBlackList: ['.norem'],
          unitPrecision: 5,
          minPixelValue: 1,
        }),
      ],
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
