#!/usr/bin/env python3
"""
ContentAI Blog - Sitemap Generator
Reads posts from posts.json and generates a sitemap.xml file.
Usage: python3 gen_sitemap.py [--base-url URL] [--output FILE]
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring, indent

# Defaults
DEFAULT_BASE_URL = "https://yourdomain.com"
DEFAULT_POSTS_JSON = os.path.expanduser("~/blog-seo/posts.json")
DEFAULT_OUTPUT = os.path.expanduser("~/blog-seo/sitemap.xml")


def load_posts(posts_json_path: str) -> list:
    """Load posts from posts.json index file."""
    if not os.path.exists(posts_json_path):
        print(f"⚠️  Plik {posts_json_path} nie istnieje. Generuję sitemap仅 z bazowymi URL.")
        return []

    with open(posts_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Support both formats: list of posts or dict with "posts" key
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "posts" in data:
        return data["posts"]
    else:
        print("⚠️  Nieprawidłowy format posts.json")
        return []


def get_last_modified(post: dict) -> str:
    """Extract last modified date from post, fallback to current date."""
    for key in ("lastModified", "last_modified", "dateModified", "modified", "date", "published"):
        if key in post:
            try:
                dt = datetime.fromisoformat(post[key].replace("Z", "+00:00"))
                return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
            except (ValueError, AttributeError):
                continue
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


def get_changefreq(post: dict) -> str:
    """Determine change frequency based on post metadata."""
    for key in ("changefreq", "changeFreq", "frequency"):
        if key in post:
            return post[key]
    return "weekly"


def generate_sitemap(base_url: str, posts: list, output_path: str):
    """Generate sitemap.xml content and write to file."""
    # Remove trailing slash from base URL
    base_url = base_url.rstrip("/")

    # Create XML root
    urlset = Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    urlset.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    urlset.set(
        "xsi:schemaLocation",
        "http://www.sitemaps.org/schemas/sitemap/0.9 "
        "http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd"
    )

    # Add homepage
    homepage = SubElement(urlset, "url")
    SubElement(homepage, "loc").text = f"{base_url}/"
    SubElement(homepage, "lastmod").text = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    SubElement(homepage, "changefreq").text = "daily"
    SubElement(homepage, "priority").text = "1.0"

    # Add category pages
    categories = set()
    for post in posts:
        cat = post.get("category", post.get("tag", ""))
        if cat:
            categories.add(cat)

    for cat in sorted(categories):
        cat_url = SubElement(urlset, "url")
        SubElement(cat_url, "loc").text = f"{base_url}/category/{cat.lower().replace(' ', '-')}/"
        SubElement(cat_url, "lastmod").text = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        SubElement(cat_url, "changefreq").text = "weekly"
        SubElement(cat_url, "priority").text = "0.7"

    # Add post pages
    for post in posts:
        slug = post.get("slug", post.get("id", post.get("title", "untitled")))
        url = SubElement(urlset, "url")
        SubElement(url, "loc").text = f"{base_url}/posts/{slug}/"
        SubElement(url, "lastmod").text = get_last_modified(post)
        SubElement(url, "changefreq").text = get_changefreq(post)
        SubElement(url, "priority").text = "0.8"

    # Pretty print XML
    indent(urlset, space="  ")
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content = xml_declaration + tostring(urlset, encoding="unicode")

    # Write to file
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    print(f"✅ Sitemap wygenerowany pomyślnie!")
    print(f"   📄 Plik: {output_path}")
    print(f"   🔗 URL bazowy: {base_url}")
    print(f"   📊 Liczba stron: {len(posts) + len(categories) + 1}")
    print(f"      - Strona główna: 1")
    print(f"      - Kategorie: {len(categories)}")
    print(f"      - Artykuły: {len(posts)}")


def main():
    parser = argparse.ArgumentParser(description="Generator sitemap.xml dla ContentAI Blog")
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"URL bazowy bloga (domyślnie: {DEFAULT_BASE_URL})"
    )
    parser.add_argument(
        "--posts-json",
        default=DEFAULT_POSTS_JSON,
        help=f"Ścieżka do pliku posts.json (domyślnie: {DEFAULT_POSTS_JSON})"
    )
    parser.add_argument(
        "--output", "-o",
        default=DEFAULT_OUTPUT,
        help=f"Ścieżka wyjściowa sitemap.xml (domyślnie: {DEFAULT_OUTPUT})"
    )

    args = parser.parse_args()

    print("🗺️  ContentAI Blog - Generator Sitemap")
    print("=" * 40)

    posts = load_posts(args.posts_json)
    generate_sitemap(args.base_url, posts, args.output)


if __name__ == "__main__":
    main()
