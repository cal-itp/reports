import css from "rollup-plugin-import-css";
import multi from '@rollup/plugin-multi-entry';
import resolve from '@rollup/plugin-node-resolve';

const isProduction = process.env.NODE_ENV === 'production';

export default (async () => ({
    input: [
        'assets/js/main.js',
        'assets/js/report.js',
    ],
    output: {
        file: 'build/js/bundle.js',
        format: 'iife',
    },
    plugins: [
        css({
            alwaysOutput: true,
        }),
        multi(),
        resolve(),
        isProduction && (await import('rollup-plugin-terser')).terser(),
    ],
}))();
