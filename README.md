# test-dev

This repository includes a simple, modern “Hello World” web page intended for GitHub Pages.

## View the page locally

From the repo root:

```bash
python3 -m http.server --directory docs 8000
```

Then open `http://localhost:8000/`.

## GitHub Pages

This repo is set up to serve a static site from `docs/`.

Enable GitHub Pages in the repo settings:

1. `Settings` → `Pages`
2. Under “Build and deployment”, set “Source” to `Deploy from a branch`
3. Select branch `master` and folder `/docs`, then save

The site will be available at:

- `https://mini-bot-2.github.io/test-dev/`

## Tests

Run the lightweight validation suite (HTML presence + local link checks):

```bash
python3 -m unittest discover -v
```
