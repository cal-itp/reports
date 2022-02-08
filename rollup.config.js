import resolve from '@rollup/plugin-node-resolve';

const isProduction = process.env.NODE_ENV === 'production';

export default (async () => ({
    input: 'assets/js/main.js',
    output: {
        file: 'build/js/bundle.js',
        format: 'iife',
    },
    plugins: [
        resolve(),
        isProduction && (await import('rollup-plugin-terser')).terser(),
    ],
}))();
