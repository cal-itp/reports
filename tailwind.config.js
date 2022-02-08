module.exports = {
  purge: {
    enabled: process.env.NODE_ENV === 'production',
    content: [
      'build/**/*.html'
    ],
  },
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
      colors: {
        'itp-teal': {
          DEFAULT: '#2EA8CE',
          bold: '#136C97',
          light: '#DFF2F2',
        },
        'itp-yellow': {
          DEFAULT: '#F4D837',
          bold: '#F6BF16',
          light: '#F7ECCF',
        },
        'itp-slate': {
          DEFAULT: '#8CBCCB',
          bold: '#7790A3',
          light: '#DEE1E6',
        },
        'itp-purple': {
          DEFAULT: '#9487C0',
          bold: '#5B559C',
          light: '#E3E0F0',
        },
        'itp-orange': {
          DEFAULT: '#EB9F3C',
          bold: '#E16B26',
          light: '#FAE7D0',
        },
        'itp-green': {
          DEFAULT: '#51BF9D',
          bold: '#00896B',
          light: '#DCEFE7',
        },
      },
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
