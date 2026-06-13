#!/usr/bin/env python3
"""사이트맵 ping.

주의: 구글과 빙의 sitemap ping 엔드포인트(/ping?sitemap=)는 2023년 6월 공식 종료되어
더 이상 색인에 영향을 주지 않습니다. 빠른 색인 통보는 IndexNow(tools/indexnow.py)와
각 웹마스터 도구의 사이트맵 등록이 정식 경로입니다.

이 스크립트는 호환 차원에서 남겨 둔 것으로, 실제 색인 촉진 효과는 기대하지 마세요.
권장 흐름:
  1) python3 build.py            # sitemap.xml / feed.xml 갱신
  2) python3 tools/indexnow.py --all      # 빙·네이버 등 즉시 통보
  3) Google Search Console / 네이버 서치어드바이저에 sitemap.xml·feed.xml 등록(최초 1회)
"""
import os
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from content.site import BASE_URL

SITEMAP = BASE_URL.rstrip("/") + "/sitemap.xml"
# 종료된 엔드포인트 — 200을 반환할 수 있으나 색인에는 반영되지 않음
LEGACY = [
    "https://www.google.com/ping?sitemap=",
    "https://www.bing.com/ping?sitemap=",
]


def main():
    enc = urllib.parse.quote(SITEMAP, safe="")
    print("⚠ 구글·빙 sitemap ping은 종료된 기능입니다. IndexNow 사용을 권장합니다.\n")
    for base in LEGACY:
        url = base + enc
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                print(f"{r.status}  {url}")
        except Exception as e:  # noqa: BLE001
            print(f"ERR  {url}  ({e})")


if __name__ == "__main__":
    main()
