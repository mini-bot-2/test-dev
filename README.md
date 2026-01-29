# test-dev

A small test repository for the mini-bot-2 challenge workflows.

## Hello World (GitHub Pages)

This repo includes a modern static “Hello World” page under `docs/`, designed to be deployed with GitHub Pages.

### View locally

- Open `docs/index.html` directly in your browser, or
- Serve it locally:
  - `cd docs && python3 -m http.server 8000`
  - Visit `http://localhost:8000`

### View on GitHub Pages

Enable GitHub Pages to serve from the `docs/` folder:

- GitHub repository → **Settings** → **Pages**
- **Build and deployment** → **Source: Deploy from a branch**
- Select **Branch: `master`** and **Folder: `/docs`**

If Pages is enabled for the repository, the site will be available at:
`https://mini-bot-2.github.io/test-dev/`

### Validate the site

Run:

- `python3 scripts/validate_site.py`
