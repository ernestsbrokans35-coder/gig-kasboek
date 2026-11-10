#!/bin/sh
# Rebuild the app and publish the app/ folder to the live site (GitHub Pages, gh-pages branch).
set -e
cd "$(dirname "$0")"
py src/build.py
git add -A
git diff --cached --quiet || git commit -m "${1:-Update app}"
git push origin main
git push origin "$(git subtree split --prefix app main)":refs/heads/gh-pages --force
