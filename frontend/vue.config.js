const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  publicPath: process.env.NODE_ENV === 'production' ? '/static/' : '/',
  outputDir: '../backend/static',
  indexPath: '../templates/index.html'
}) 