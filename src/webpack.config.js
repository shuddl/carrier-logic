const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
// Enable error handling for JSON parsing
process.on('unhandledRejection', (err) => {
    console.error('Unhandled promise rejection:', err);
});

const WEBPACK_PORT = 9000;
module.exports = {
    mode: 'development',
    entry: './src/index.jsx',  // Updated to .jsx
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: 'bundle.js',
        publicPath: '/'
    },
    devServer: {
        static: {
            directory: path.join(__dirname, '../build'),
        },
        port: 9000,
        proxy: {
            '/api': {
                target: 'http://localhost:9000',
                secure: false,
                changeOrigin: true,
            },
'/carriers': {
    target: 'http://localhost:9000',
    secure: false,
    changeOrigin: true,
    onError: (err, req, res) => {
        console.error('Proxy error:', err);
        res.writeHead(500, {
            'Content-Type': 'application/json'
        });
        res.end(JSON.stringify({ error: 'Proxy error' }));
    },
    onProxyRes: (proxyRes, req, res) => {
        proxyRes.headers['Content-Type'] = 'application/json';
    }
}
        },
        historyApiFallback: {
            rewrites: [
                { from: /^\/api\/.*$/, to: context => context.parsedUrl.path },
                { from: /./, to: '/index.html' },
            ],
        },
        hot: false,
        liveReload: false,
        open: true,
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: ['babel-loader']
            },
            {
                test: /\.css$/,
                use: [
                    'style-loader',
                    'css-loader',
                    'postcss-loader'
                ]
            }
        ]
    },
    resolve: {
        extensions: ['.js', '.jsx', '.css'],
        modules: [path.resolve(__dirname, 'src'), 'node_modules']
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: path.resolve(__dirname, '../build/index.html')
        })
    ]
};