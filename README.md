# challenge-bot-test

A test repository for the challenge bot.

## Hello World (GitHub Pages)

This repo includes a small, modern, self-contained **Hello World** page under `docs/`, ready for **GitHub Pages**
deployment.

- Source: `docs/index.html`
- GitHub Pages target: `master` branch, `/docs` folder

### View locally

Option A: open the file directly

- Open `docs/index.html` in your browser.

Option B: serve the `docs/` folder (recommended)

```bash
python3 -m http.server --directory docs 8000
```

Then visit `http://localhost:8000`.

### Publish with GitHub Pages

In the GitHub repository settings:

1. Go to **Settings → Pages**
2. Set **Source** to **Deploy from a branch**
3. Select **Branch**: `master`
4. Select **Folder**: `/docs`

The site will then be available at: `https://<org-or-user>.github.io/test-dev/`.

## Tests

Basic checks validate that the docs site exists, contains the expected "Hello World" content, and stays
dependency-free.

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```
