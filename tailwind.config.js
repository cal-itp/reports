module.exports = {
  purge: [
    'build/**/*.html'
  ],
  darkMode: false, // or 'media' or 'class'
  theme: {
    container: {
      center: true,
      padding: '2rem',
    },
    fontFamily: {
      sans: ['Poppins', 'sans-serif'],
      serif: ['Raleway', 'serif'],
    },
    extend: {
      typography: {
        DEFAULT: {
          css: {
            color: '#333',
            h1: {
              fontWeight: '900',
            },
            // ...
          },
        },
      },
    }
  },
  variants: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
