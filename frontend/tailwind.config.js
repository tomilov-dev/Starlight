/** @type {import('tailwindcss').Config} */

const { createThemes } = require("tw-colors");

module.exports = {
  content: ["./src/**/*.{html,ts}", "./node_modules/flowbite/**/*.js"],
  theme: {
    extend: {},
  },
  plugins: [
    require("flowbite/plugin"),
    createThemes({
      light: {
        "primary-100": "#FFF75C",
        "primary-200": "#FFF533",
        primary: "#FFF400",
        "primary-300": "#E0D500",
        "primary-400": "#B8AE00",

        "secondary-100": "#EEC76D",
        "secondary-200": "#EAB948",
        secondary: "#E6AD25",
        "secondary-300": "#C99418",
        "secondary-400": "#A47913",

        "accent-100": "#746EED",
        "accent-200": "#5149E9",
        accent: "#251BE0",
        "accent-300": "#2119C8",
        "accent-400": "#1B14A3",

        "neutral-100": "#5E5D98",
        "neutral-200": "#4F4E7E",
        neutral: "#3E3C61",
        "neutral-300": "#383659",
        "neutral-400": "#302F4C",

        info: "#0072C3",
        success: "#22AA4B",
        warning: "#EAB308",
        error: "#ED3131",

        "base-0": "#FFFFFF",
        "base-100": "#FBF7EE",
        "base-200": "#F7F0DE",
        "base-300": "#F3E8CE",
        "base-400": "#EFE0BD",
      },
    }),
  ],
};
