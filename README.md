# joaorodrigues.github.io

Personal site built with [Hugo](https://gohugo.io/) and the
[hello-friend-ng](https://github.com/rhazdon/hugo-theme-hello-friend-ng) theme.

## Running locally

### 1. Clone with the theme submodule

```bash
git clone https://github.com/joaorodrigues/joaorodrigues.github.io.git
cd joaorodrigues.github.io
git submodule update --init --recursive
```

If you already cloned without `--recursive`, the last command fills in `themes/hello-friend-ng`.

### 2. Install Hugo (extended) and Dart Sass

The CI build uses Hugo `0.123.7` (extended edition) and Dart Sass. On macOS:

```bash
brew install hugo sass/sass/sass
```

Check the install:

```bash
hugo version   # should include "extended"
sass --version
```

Any Hugo version at or above 0.123.7 should work, but matching CI avoids surprises.

### 3. Start the dev server

```bash
hugo server -D
```

Then open <http://localhost:1313/>. The server reloads automatically when you edit content, layouts, or config.

The `-D` flag includes draft posts. Drop it to preview only published content.

### 4. Build the static site (optional)

```bash
hugo --gc --minify
```

This writes the output to `public/`, the same way the GitHub Actions workflow does (`.github/workflows/hugo.yaml`).

## Updating publications (optional)

`scripts/fetch_publications.py` scrapes Google Scholar and writes `data/publications.json`. Run it from the site root:

```bash
python3 scripts/fetch_publications.py
```

## Deployment

Pushing to `main` triggers the GitHub Actions workflow, which builds the site and deploys it to GitHub Pages. There is no need to commit `public/`; it is git-ignored.
