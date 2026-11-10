"""Builds app/index.html from src/. Run: py src/build.py"""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
src = (root / 'src' / 'index.src.html').read_text(encoding='utf-8')
css = re.search(r'<style>(.*?)</style>', (root / 'artifact' / 'kasboek.src.html').read_text(encoding='utf-8'), re.S).group(1).strip()
out = src.replace('/*__CSS__*/', css).replace('/*__PARSER__*/', (root / 'src' / 'parse.js').read_text(encoding='utf-8'))
(root / 'app' / 'index.html').write_text(out, encoding='utf-8', newline='\n')
print('built app/index.html', len(out), 'bytes')
