# reports

GTFS data quality reports for California transit providers

## How it works

- Python script `generate.py` loads JSON from `data` directory and applies it to `index.html` template
- HTML template written with [Jinja](https://jinja.palletsprojects.com/en/3.0.x/)
- CSS written with [SCSS](https://sass-lang.com/documentation/syntax#scss) and [Tailwind](https://tailwindcss.com/docs) via [PostCSS](https://postcss.org/)
- Build scripts via [NPM](https://www.npmjs.com/)

## How to use it

1. (Recommended) `source .venv/bin/activate` to activate Python virtual environment
1. `pip install -r requirements.txt` to download Python dependencies
1. `npm install` to download npm dependencies
1. `npm run build` to get a slim build or `npm run watch` to monitor the source files for changes and run dev builds automatically
1. Load `build/index.html` in a browser, preferably via an HTTP server
