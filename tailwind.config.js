/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./class_captain/templates/**/*.{html,js}",
    "./node_modules/tw-elements/dist/js/**/*.js",
  ],
  theme: {
    extend: {
      fontFamily: {
        'roboto-mono': ["'Roboto Mono'",'mono','sans-serif'],
        'secondary': ["'Raleway'",'sans-serif'],
        'primary': ["'Playfair Display'",'sans-serif'],
      }
    },
  },
  darkMode: "class",
  plugins: [
    require("tw-elements/dist/plugin.cjs"),
    require('@tailwindcss/forms')
  ],
};