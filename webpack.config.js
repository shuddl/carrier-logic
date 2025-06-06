const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  mode: 'development', // or 'production' based on the script
  entry: './src/index.js', // Update the path if different
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
    clean: true, // Cleans the output directory before each build
  },
  devServer: {
    static: {
      directory: path.join(__dirname, 'build'),
    },
    port: 8000,
    hot: false,
    open: true,
    proxy: {
      '/api': 'http://localhost:8000',
    },
    historyApiFallback: {
      rewrites: [
        { from: /^\/api/, to: context => context.parsedUrl.pathname }, // Exclude API routes from history fallback
      ],
    },
    liveReload: false,
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/, // Handles both .js and .jsx files
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react'],
            plugins: ['@babel/plugin-transform-private-property-in-object']
          }
        }
      },
      {
        test: /\.css$/, // Handles CSS files
        use: ['style-loader', 'css-loader', 'postcss-loader'],
      },
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx'], // Allows importing without specifying extensions
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './build/index.html', // Updated path to match the existing file
    }),
  ],
};