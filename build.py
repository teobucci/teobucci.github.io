#!/usr/bin/env python3
"""
Blog builder for teobucci.github.io
Converts markdown posts to HTML using Jinja2 templates.
"""
import sys
from pathlib import Path
from datetime import datetime

import markdown
from jinja2 import Environment, FileSystemLoader


def parse_frontmatter(content):
    """Parse YAML-style frontmatter from markdown content."""
    if not content.strip():
        return {}, content
    
    lines = content.split('\n')
    if not lines[0].strip() == '---':
        return {}, content
    
    frontmatter = {}
    body_start = None
    
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            body_start = i + 1
            break
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()
    
    if body_start is None:
        return {}, content
    
    body = '\n'.join(lines[body_start:]).strip()
    return frontmatter, body


def build_post(md_file, template, md_converter):
    """Build a single blog post from markdown file."""
    try:
        content = md_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading {md_file.name}: {e}", file=sys.stderr)
        return None
    
    meta, body = parse_frontmatter(content)
    
    if not meta.get('title'):
        print(f"Warning: {md_file.name} missing 'title' in frontmatter", file=sys.stderr)
        return None
    
    if not meta.get('date'):
        print(f"Warning: {md_file.name} missing 'date' in frontmatter", file=sys.stderr)
        return None
    
    # Validate date format
    try:
        date_obj = datetime.strptime(meta['date'], '%Y-%m-%d')
        formatted_date = date_obj.strftime('%B %d, %Y')
    except ValueError:
        print(f"Error: {md_file.name} has invalid date format (expected YYYY-MM-DD)", file=sys.stderr)
        return None
    
    # Convert markdown to HTML
    html_content = md_converter.convert(body)
    md_converter.reset()
    
    # Render post template
    html = template.render(
        title=meta['title'],
        formatted_date=formatted_date,
        content=html_content
    )
    
    # Write HTML file
    output_file = md_file.with_suffix('.html')
    try:
        output_file.write_text(html, encoding='utf-8')
    except Exception as e:
        print(f"Error writing {output_file.name}: {e}", file=sys.stderr)
        return None
    
    return {
        'title': meta['title'],
        'date': meta['date'],
        'formatted_date': formatted_date,
        'slug': md_file.stem
    }


def build_index(posts, template):
    """Build the blog index page."""
    sorted_posts = sorted(posts, key=lambda p: p['date'], reverse=True) if posts else []
    html = template.render(posts=sorted_posts)
    
    index_file = Path('blog/index.html')
    try:
        index_file.write_text(html, encoding='utf-8')
    except Exception as e:
        print(f"Error writing index.html: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main build process."""
    blog_dir = Path('blog')
    templates_dir = Path('templates')
    
    if not blog_dir.exists():
        print(f"Error: blog directory not found: {blog_dir}", file=sys.stderr)
        sys.exit(1)
    
    if not templates_dir.exists():
        print(f"Error: templates directory not found: {templates_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(str(templates_dir)))
    post_template = env.get_template('post.html')
    index_template = env.get_template('index.html')
    
    # Setup markdown converter
    md_converter = markdown.Markdown(extensions=['fenced_code', 'codehilite', 'tables'])
    
    # Find all markdown files
    md_files = list(blog_dir.glob('*.md'))
    if not md_files:
        print("No markdown files found in blog/", file=sys.stderr)
    
    # Build posts
    posts = []
    for md_file in md_files:
        print(f'Building {md_file.name}...')
        post_meta = build_post(md_file, post_template, md_converter)
        if post_meta:
            posts.append(post_meta)
    
    # Build index
    print('Building index...')
    build_index(posts, index_template)
    
    print(f'Done! Built {len(posts)} post(s).')


if __name__ == '__main__':
    main()
