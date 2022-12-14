import css from "rollup-plugin-import-css";
import multi from '@rollup/plugin-multi-entry';
import resolve from '@rollup/plugin-node-resolve';
import terser from '@rollup/plugin-terser';

// workaround for bug:
// https://github.com/rollup/plugins/issues/1366#issuecomment-1345358157
import { fileURLToPath } from 'url';
const __filename = fileURLToPath(import.meta.url);
global['__filename'] = __filename;
// end workaround

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
        isProduction && terser(),
    ],
    onwarn(warning, warn) {
        // suppress some wontfix warnings in d3
        // see https://github.com/d3/d3-selection/issues/168#issuecomment-451983830
        if (warning.code === 'CIRCULAR_DEPENDENCY') {
            if (warning.message.includes('node_modules/d3-')) return;
        };
        warn(warning);
    }
}))();
