import typescript from '@rollup/plugin-typescript';
import terser from '@rollup/plugin-terser';

export default [
  // UMD build (for script tags)
  {
    input: 'src/index.ts',
    output: {
      file: 'dist/azolute-chat.js',
      format: 'umd',
      name: 'AzoluteChat',
      exports: 'named',
    },
    plugins: [
      typescript({ tsconfig: './tsconfig.json' }),
      terser(),
    ],
  },
  // ESM build (for modern bundlers)
  {
    input: 'src/index.ts',
    output: {
      file: 'dist/azolute-chat.esm.js',
      format: 'esm',
    },
    plugins: [
      typescript({ tsconfig: './tsconfig.json' }),
      terser(),
    ],
  },
  // IIFE build (for direct browser use)
  {
    input: 'src/index.ts',
    output: {
      file: 'dist/azolute-chat.min.js',
      format: 'iife',
      name: 'AzoluteChat',
    },
    plugins: [
      typescript({ tsconfig: './tsconfig.json' }),
      terser(),
    ],
  },
];
