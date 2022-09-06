import resolve from '@rollup/plugin-node-resolve';
import { terser } from 'rollup-plugin-terser';

// `npm run build` -> `production` is true
// `npm run dev` -> `production` is false
const production = !process.env.ROLLUP_WATCH;

export default {
	input: 'javascript/main.js',
	output: {
		file: 'javascript-dist/bundle.js',
		format: 'iife',
		sourcemap: true
	},
	plugins: [
		resolve(), // tells Rollup how to find date-fns in node_modules
		production && terser() // minify, but only in production
	]
};
