#!/usr/bin/env python3
import os
import re
from pathlib import Path
from datetime import datetime

def parse_frontmatter(content):
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        return {}, content
    
    frontmatter = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()
    
    return frontmatter, match.group(2)

def markdown_to_html(md):
    html = md
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
    
    paragraphs = []
    for block in html.split('\n\n'):
        block = block.strip()
        if block and not block.startswith('<h'):
            paragraphs.append(f'<p>{block}</p>')
        elif block:
            paragraphs.append(block)
    
    return '\n\n'.join(paragraphs)

def build_post(md_file):
    with open(md_file, 'r') as f:
        content = f.read()
    
    meta, body = parse_frontmatter(content)
    html_content = markdown_to_html(body)
    
    title = meta.get('title', 'Untitled')
    date = meta.get('date', '')
    
    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%B %d, %Y')
        except:
            formatted_date = date
    else:
        formatted_date = ''
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Teo Bucci</title>
    <link rel="stylesheet" href="../style.css">
    <style>
        body {{ justify-content: flex-start; padding-top: 4rem; }}
        main {{ max-width: 650px; text-align: left; }}
        .back-link {{ display: inline-block; margin-bottom: 2rem; color: #666; text-decoration: none; }}
        .back-link:hover {{ color: #1a1a1a; }}
        .post-header {{ margin-bottom: 3rem; }}
        .post-title {{ font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; }}
        .post-date {{ color: #999; font-size: 0.95rem; }}
        .post-content {{ color: #333; line-height: 1.8; }}
        .post-content p {{ margin-bottom: 1.5rem; }}
        .post-content h2 {{ font-size: 1.5rem; margin: 2rem 0 1rem; }}
        .post-content code {{ background: #f5f5f5; padding: 0.2rem 0.4rem; border-radius: 3px; font-size: 0.9em; }}
        .post-content a {{ color: #0066cc; }}
    </style>
</head>
<body>
    <main>
        <a href="./" class="back-link">← All posts</a>
        
        <header class="post-header">
            <h1 class="post-title">{title}</h1>
            <time class="post-date">{formatted_date}</time>
        </header>
        
        <article class="post-content">
{html_content}
        </article>
    </main>
</body>
</html>'''
    
    output_file = md_file.replace('.md', '.html')
    with open(output_file, 'w') as f:
        f.write(html)
    
    return {
        'title': title,
        'date': date,
        'formatted_date': formatted_date,
        'slug': Path(md_file).stem
    }

def build_index(posts):
    posts_html = []
    for post in sorted(posts, key=lambda p: p['date'], reverse=True):
        posts_html.append(f'''            <article class="post">
                <h2 class="post-title"><a href="{post['slug']}.html">{post['title']}</a></h2>
                <time class="post-date">{post['formatted_date']}</time>
            </article>''')
    
    if not posts_html:
        posts_html = ['            <article class="post">\n                <p style="color: #999; font-style: italic;">No posts yet. Check back soon!</p>\n            </article>']
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog - Teo Bucci</title>
    <link rel="stylesheet" href="../style.css">
    <style>
        body {{ justify-content: flex-start; padding-top: 4rem; }}
        main {{ max-width: 650px; text-align: left; }}
        .back-link {{ display: inline-block; margin-bottom: 2rem; color: #666; text-decoration: none; }}
        .back-link:hover {{ color: #1a1a1a; }}
        .posts {{ display: flex; flex-direction: column; gap: 2rem; }}
        .post {{ padding-bottom: 2rem; border-bottom: 1px solid #e5e5e5; }}
        .post:last-child {{ border-bottom: none; }}
        .post-title {{ font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem; }}
        .post-date {{ color: #999; font-size: 0.9rem; }}
        .post a {{ color: #1a1a1a; text-decoration: none; }}
        .post a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <main>
        <a href="../" class="back-link">← Back</a>
        <h1 style="margin-bottom: 3rem;">Blog</h1>
        
        <div class="posts">
{chr(10).join(posts_html)}
        </div>
    </main>
</body>
</html>'''
    
    with open('blog/index.html', 'w') as f:
        f.write(html)

if __name__ == '__main__':
    blog_dir = Path('blog')
    md_files = list(blog_dir.glob('*.md'))
    
    posts = []
    for md_file in md_files:
        print(f'Building {md_file.name}...')
        post_meta = build_post(str(md_file))
        posts.append(post_meta)
    
    print('Building index...')
    build_index(posts)
    print(f'Done! Built {len(posts)} post(s).')
