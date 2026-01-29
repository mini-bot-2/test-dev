# test-dev

A tiny, dependency-free "Hello World" site intended to be served via GitHub Pages.

## View the page

### Local preview

From the repository root:

```bash
cd docs
python3 -m http.server 8000
```

Then open `http://localhost:8000/`.

### GitHub Pages

This repository is set up to be served from the `/docs` folder on the `master` branch.

In GitHub: `Settings` → `Pages` → `Build and deployment` → `Source: Deploy from a branch` →
select `Branch: master` and `Folder: /docs`.

Once enabled, the URL is typically:
`https://mini-bot-2.github.io/test-dev/`

## Validate

Run a quick sanity check for the page structure and local assets:

```bash
python3 scripts/validate_site.py
```
