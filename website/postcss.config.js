module.exports = (ctx) => ({
    plugins: [
        require('tailwindcss'),
        ctx.env === 'production' ? require('autoprefixer') : null,
        ctx.env === 'production' ? require('cssnano') : null,
    ],
})
