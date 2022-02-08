module.exports = (ctx) => ({
    plugins: {
        autoprefixer: ctx.env === 'production' ? {} : false,
        cssnano: ctx.env === 'production' ? {} : false,
        tailwindcss: {},
    }
})
