export const OUTPUT_DIR = 'dist'

export const PROXY_CONFIG = {
  // /**
  //  * @desc    替换匹配值
  //  * @请求路径  http://localhost:3100/api/user
  //  * @转发路径  http://localhost:9999/api/v1 +/user
  //  */
  // '/api': {
  //   target: 'http://localhost:9999/api/v1',
  //   changeOrigin: true,
  //   rewrite: (path) => path.replace(new RegExp('^/api'), ''),
  // },
  /**
   * @desc    不替换匹配值
   * @请求路径  http://localhost:3100/api/v1/user
   * @转发路径  http://localhost:9999/api/v1/user
   */
  '/api/v1': {
    target: 'http://127.0.0.1:9999',
    changeOrigin: true,
  },
  /**
   * @desc    静态文件代理
   * @请求路径  http://localhost:3100/static/uploads/images/xxx.jpg
   * @转发路径  http://localhost:9999/static/uploads/images/xxx.jpg
   */
  '/static': {
    target: 'http://127.0.0.1:9999',
    changeOrigin: true,
    headers: {
      Accept: 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    },
  },
}
