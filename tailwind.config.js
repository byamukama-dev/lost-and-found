/** Tailwind CSS configuration — CampusFind */
module.exports = {
  content: ['./*.html', './static/js/**/*.js'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eefbf5',
          100: '#d5f5e6',
          200: '#adead1',
          300: '#78d9b4',
          400: '#3fc093',
          500: '#17a578',
          600: '#0b8662',
          700: '#096b51',
          800: '#0a5542',
          900: '#094637',
        },
        ink: {
          50: '#f7f8f8',
          100: '#eef1f0',
          200: '#d9e0de',
          300: '#b3c1bd',
          400: '#849a94',
          500: '#627a74',
          600: '#4a615b',
          700: '#3a4d48',
          800: '#2b3a36',
          900: '#14211e',
          950: '#0b1513',
        },
        sand: {
          50: '#fbfaf7',
          100: '#f5f2ea',
          200: '#ebe5d7',
          300: '#ddd3bd',
        },
        coral: {
          50: '#fff5f2',
          100: '#ffe7e0',
          200: '#ffcbbc',
          300: '#ffa88f',
          400: '#fb7f5c',
          500: '#ef5b35',
          600: '#d9421f',
          700: '#b53418',
        },
      },
      fontFamily: {
        sans: ['"DM Sans"', 'ui-sans-serif', 'system-ui', 'Segoe UI', 'sans-serif'],
        display: ['Manrope', '"DM Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 1px 2px rgba(20, 33, 30, 0.04), 0 12px 32px -12px rgba(20, 33, 30, 0.12)',
        lift: '0 2px 4px rgba(20, 33, 30, 0.05), 0 24px 48px -20px rgba(20, 33, 30, 0.25)',
        glow: '0 18px 45px -15px rgba(11, 134, 98, 0.45)',
      },
      backgroundImage: {
        grid: "linear-gradient(to right, rgba(20,33,30,.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(20,33,30,.05) 1px, transparent 1px)",
        dots: 'radial-gradient(rgba(20,33,30,.12) 1px, transparent 1px)',
      },
      backgroundSize: {
        grid: '44px 44px',
        dots: '18px 18px',
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(14px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        shimmer: {
          '100%': { transform: 'translateX(100%)' },
        },
      },
      animation: {
        'fade-up': 'fade-up .55s cubic-bezier(.2,.7,.3,1) both',
        'fade-in': 'fade-in .4s ease both',
        float: 'float 7s ease-in-out infinite',
        shimmer: 'shimmer 1.6s infinite',
      },
    },
  },
  plugins: [],
};
