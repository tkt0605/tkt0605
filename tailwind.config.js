/** @type {import('tailwindcss').Config} */
export default {
    content: ["./templates/**/*.html", "./src/**/*/py"],
    theme: {
        extend: {}
    },
    plugins: [
        require("@tailwindcss/typography")
    ]
}