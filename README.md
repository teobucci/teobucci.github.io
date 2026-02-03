# teobucci.github.io

Personal website hosted on GitHub Pages.

## Local Development

Open `index.html` in your browser to preview locally.

## Setup

Create a virtual environment and install dependencies using `uv`:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

## Blog Posts

Write blog posts as markdown files in the `blog/` directory with frontmatter:

```markdown
---
title: My Post Title
date: 2026-02-03
---

Your content here...
```

Build HTML from markdown:

```bash
uv run python build.py
```

The script will:
- Validate frontmatter (title and date are required)
- Convert markdown to HTML using the `markdown` library
- Apply Jinja2 templates from `templates/` directory
- Generate individual post HTML files and the blog index

Commit both the `.md` and generated `.html` files.

## Deployment

Automatically deploys to GitHub Pages on push to `main` branch.

Visit: https://teobucci.github.io

## Deployment

Automatically deploys to GitHub Pages on push to `main` branch.

Visit: https://teobucci.github.io
