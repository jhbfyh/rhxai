#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""站点离线化与部署结构整理。

做三件事：
  1. 下载第三方 JS / GeoJSON 到 vendor/，使站点不再依赖任何外网运行时资源；
  2. 把站点源码从 src/ 提升到站点根目录，序言页改名为 index.html；
  3. 按新位置重写全部相对引用（HTML 的 src/href、CSS 的 url()、JS 的 fetch 路径）。

脚本可重复执行：已存在的 vendor 文件默认跳过下载，路径改写为幂等替换。
运行：python tools/bootstrap_offline.py
"""

import json
import os
import re
import shutil
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VENDOR = [
    ("echarts.min.js", "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"),
    ("echarts-gl.min.js", "https://cdn.jsdelivr.net/npm/echarts-gl@2.0.9/dist/echarts-gl.min.js"),
    ("d3.min.js", "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"),
    ("geo/world.json", "https://cdn.jsdelivr.net/npm/echarts@4.9.0/map/json/world.json"),
    ("geo/china.json", "https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json"),
]

# 章节文件从 src/chapters/ 移到 chapters/，序言页提到根目录并改名
MOVES = {
    "src/chapters/00-intro.html": "index.html",
    "src/chapters/01-online.html": "chapters/01-online.html",
    "src/chapters/02-cocoon.html": "chapters/02-cocoon.html",
    "src/chapters/03-wound.html": "chapters/03-wound.html",
    "src/chapters/04-breaking.html": "chapters/04-breaking.html",
    "src/chapters/05-backmatter.html": "chapters/05-backmatter.html",
    "src/components/common.js": "components/common.js",
    "src/components/crowd.js": "components/crowd.js",
    "src/components/people-sprites.js": "components/people-sprites.js",
    "src/data/data.js": "data/data.js",
    "src/styles/theme.css": "styles/theme.css",
}


def dl(rel, url):
    path = os.path.join(ROOT, "vendor", rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path) and os.path.getsize(path) > 1024:
        print("  skip (exists)  %-22s %8d B" % (rel, os.path.getsize(path)))
        return
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = resp.read()
    with open(path, "wb") as fh:
        fh.write(data)
    print("  download       %-22s %8d B" % (rel, len(data)))


def move_tree():
    for src_rel, dst_rel in MOVES.items():
        src = os.path.join(ROOT, src_rel)
        dst = os.path.join(ROOT, dst_rel)
        if not os.path.exists(src):
            print("  skip (moved)   %-28s -> %s" % (src_rel, dst_rel))
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
        print("  move           %-28s -> %s" % (src_rel, dst_rel))
    src_dir = os.path.join(ROOT, "src")
    if os.path.isdir(src_dir):
        shutil.rmtree(src_dir)
        print("  remove         src/")


def rewrite(path, rules):
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    before = text
    total = 0
    for pattern, repl in rules:
        text, n = re.subn(pattern, repl, text)
        total += n
    if text != before:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        print("  rewrite %3d    %s" % (total, os.path.relpath(path, ROOT)))
    return total


CDN_RULES_CHAPTER = [
    (r'https://cdn\.jsdelivr\.net/npm/echarts@5\.4\.3/dist/echarts\.min\.js', '../vendor/echarts.min.js'),
    (r'https://cdn\.jsdelivr\.net/npm/echarts-gl@2\.0\.9/dist/echarts-gl\.min\.js', '../vendor/echarts-gl.min.js'),
    (r'https://cdn\.jsdelivr\.net/npm/d3@7\.9\.0/dist/d3\.min\.js', '../vendor/d3.min.js'),
]

CDN_RULES_ROOT = [
    (r'https://cdn\.jsdelivr\.net/npm/echarts@5\.4\.3/dist/echarts\.min\.js', 'vendor/echarts.min.js'),
    (r'https://cdn\.jsdelivr\.net/npm/echarts-gl@2\.0\.9/dist/echarts-gl\.min\.js', 'vendor/echarts-gl.min.js'),
    (r'https://cdn\.jsdelivr\.net/npm/d3@7\.9\.0/dist/d3\.min\.js', 'vendor/d3.min.js'),
]


def rewrite_index():
    path = os.path.join(ROOT, "index.html")
    rules = CDN_RULES_ROOT + [
        (r'"\.\./styles/theme\.css"', '"styles/theme.css"'),
        (r'"\.\./components/([a-z\-]+\.js)"', r'"components/\1"'),
        (r'"\.\./data/data\.js"', '"data/data.js"'),
        (r'"\.\./\.\./assets/', '"assets/'),
        # 章节互链：序言指向自身改为 index.html，其余章节落到 chapters/
        (r'href="00-intro\.html"', 'href="index.html"'),
        (r'href="(0[1-5]-[a-z\-]+\.html)"', r'href="chapters/\1"'),
        # 中国地图 GeoJSON 改本地
        (r"fetch\('https://geo\.datav\.aliyun\.com/areas_v3/bound/100000_full\.json'\)",
         "fetch('vendor/geo/china.json')"),
    ]
    return rewrite(path, rules)


def rewrite_chapters():
    total = 0
    chapters = ["01-online.html", "02-cocoon.html", "03-wound.html", "04-breaking.html", "05-backmatter.html"]
    for name in chapters:
        path = os.path.join(ROOT, "chapters", name)
        rules = CDN_RULES_CHAPTER + [
            (r'"\.\./\.\./assets/', '"../assets/'),
            # 序言页已改名并上移一层；同目录章节链接保持原样
            (r'href="00-intro\.html"', 'href="../index.html"'),
            # 世界地图 GeoJSON：两个外网源合并为本地单文件
            (r"'https://cdn\.jsdelivr\.net/npm/echarts@4\.9\.0/map/json/world\.json',?\s*\n\s*'https://geo\.datav\.aliyun\.com/areas_v3/bound/world\.json'",
             "'../vendor/geo/world.json'"),
        ]
        total += rewrite(path, rules)
    return total


def rewrite_preview():
    path = os.path.join(ROOT, "archive", "previews", "04-breaking-planA-demo.html")
    if not os.path.exists(path):
        return 0
    rules = [
        (r'https://cdn\.jsdelivr\.net/npm/echarts@5\.4\.3/dist/echarts\.min\.js', '../../vendor/echarts.min.js'),
    ]
    return rewrite(path, rules)


def verify():
    print("\n== 校验 ==")
    bad = []
    for dirpath, _dirs, files in os.walk(ROOT):
        if os.path.relpath(dirpath, ROOT).split(os.sep)[0] in ("docs", "archive"):
            continue
        for f in files:
            if not f.endswith((".html", ".css", ".js")):
                continue
            p = os.path.join(dirpath, f)
            with open(p, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            for m in re.finditer(r'https?://[^\s"\'()<>]+', text):
                url = m.group(0)
                # 外链（文章出处、SVG 命名空间）不算运行时依赖
                if "cdn.jsdelivr.net" in url or "geo.datav.aliyun.com" in url:
                    bad.append((os.path.relpath(p, ROOT), url))
    if bad:
        print("  仍有外网运行时依赖：")
        for p, u in bad:
            print("   ", p, u)
    else:
        print("  OK：站点代码中已无任何 CDN / GeoJSON 外网运行时依赖")

    # 本地引用完整性
    broken = []
    checked = 0
    for dirpath, _dirs, files in os.walk(ROOT):
        rel_top = os.path.relpath(dirpath, ROOT).split(os.sep)[0]
        if rel_top in ("docs",):
            continue
        for f in files:
            if not f.endswith((".html", ".css")):
                continue
            p = os.path.join(dirpath, f)
            with open(p, "r", encoding="utf-8") as fh:
                text = fh.read()
            refs = re.findall(r'(?:src|href)="([^"]+)"', text) + re.findall(r'url\(["\']?([^"\')]+)', text)
            for ref in refs:
                if ref.startswith(("http", "//", "data:", "#", "javascript:", "mailto:")):
                    continue
                if "' +" in ref or '" +' in ref:
                    continue
                checked += 1
                target = os.path.normpath(os.path.join(dirpath, ref.split("?")[0].split("#")[0]))
                if not os.path.exists(target):
                    broken.append((os.path.relpath(p, ROOT), ref))
    print("  本地引用 %d 条，失效 %d 条" % (checked, len(broken)))
    for p, ref in broken:
        print("   ", p, "->", ref)


def main():
    print("== 1. 下载第三方依赖到 vendor/ ==")
    for rel, url in VENDOR:
        try:
            dl(rel, url)
        except Exception as exc:
            print("  FAIL           %-22s %s" % (rel, exc))
            return 1

    print("\n== 2. 重排目录（站点置顶） ==")
    move_tree()

    print("\n== 3. 改写引用为本地相对路径 ==")
    n_index = rewrite_index()
    n_ch = rewrite_chapters()
    n_pre = rewrite_preview()
    print("  index.html %d 处，章节 %d 处，预览页 %d 处" % (n_index, n_ch, n_pre))

    print("\n== 4. 生成 Cloudflare Pages 配置 ==")
    headers = (
        "/*\n"
        "  X-Content-Type-Options: nosniff\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n"
        "\n"
        "/assets/*\n"
        "  Cache-Control: public, max-age=31536000, immutable\n"
        "\n"
        "/vendor/*\n"
        "  Cache-Control: public, max-age=31536000, immutable\n"
        "\n"
        "/*.html\n"
        "  Cache-Control: public, max-age=0, must-revalidate\n"
        "\n"
        "/index.html\n"
        "  Cache-Control: public, max-age=0, must-revalidate\n"
    )
    with open(os.path.join(ROOT, "_headers"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(headers)
    print("  write          _headers")

    verify()
    return 0


if __name__ == "__main__":
    sys.exit(main())
