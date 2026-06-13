#!/usr/bin/env python3
"""콘텐츠 모듈 단독 검증: python3 check.py <module이름>
본문 글자수(2,000~2,500)와 메타 디스크립션 길이(80자 이내)를 검사한다."""
import html
import importlib.util
import re
import sys
import types


def load(name):
    spec = importlib.util.spec_from_file_location(f"content.{name}", f"content/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"content.{name}"] = mod
    spec.loader.exec_module(mod)
    return mod


def chars(body):
    t = re.sub(r'<section class="pricing">.*?</section>', " ", body, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    return len(re.sub(r"\s+", " ", t).strip())


pkg = types.ModuleType("content")
pkg.__path__ = ["content"]
sys.modules["content"] = pkg
load("site")
load("pricing")

m = load(sys.argv[1])
pages = getattr(m, "PAGES", None) or [m.PAGE]
bad = 0
for p in pages:
    c = chars(p["body"])
    d = len(p["desc"])
    ok_body = p.get("noindex") or 2000 <= c <= 2500
    ok_desc = d <= 80
    bad += (not ok_body) + (not ok_desc)
    print(f"{p['path'] or '/':55} body={c:5} [{'OK' if ok_body else 'FIX'}]  desc={d:3} [{'OK' if ok_desc else 'TOO LONG'}]")
print("PASS" if bad == 0 else f"FAIL ({bad})")
