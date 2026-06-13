#!/usr/bin/env python3
"""IndexNow 즉시 색인 통보 — 빙·네이버·얀덱스 등 IndexNow 참여 검색엔진에 변경 URL을 알린다.
(구글은 IndexNow 미참여 — 구글은 tools/google_indexing.py 또는 Search Console 사용)

사용법:
  # sitemap.xml의 모든 URL 제출
  python3 tools/indexnow.py --all

  # 특정 URL만 제출(여러 개 가능)
  python3 tools/indexnow.py https://yangcheon-massage.pages.dev/yangcheon/mok-dong/

키 파일(https://<도메인>/<KEY>.txt)이 먼저 배포되어 있어야 한다(build.py가 자동 생성).
"""
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from content.site import BASE_URL, INDEXNOW_KEY

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENDPOINT = "https://api.indexnow.org/indexnow"  # 단일 제출로 참여 엔진 전체에 공유


def sitemap_urls():
    tree = ET.parse(os.path.join(ROOT, "sitemap.xml"))
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text for loc in tree.findall(".//s:loc", ns)]


def submit(urls):
    base = BASE_URL.rstrip("/")
    host = base.split("://", 1)[-1]
    payload = {
        "host": host,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{base}/{INDEXNOW_KEY}.txt",
        "urlList": urls,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"IndexNow → HTTP {resp.status} ({len(urls)} URLs 수락됨)")
            body = resp.read().decode("utf-8", "replace").strip()
            if body:
                print(body)
    except urllib.error.HTTPError as e:
        print(f"IndexNow → HTTP {e.code}")
        if e.code == 403:
            print(f"  키 검증 실패: {base}/{INDEXNOW_KEY}.txt 가 배포되어 공개 접근 "
                  "가능한지 먼저 확인하세요(사이트 배포 후 재실행).")
        else:
            print("  " + e.read().decode("utf-8", "replace").strip()[:300])
        sys.exit(1)
    except urllib.error.URLError as e:
        sys.exit(f"네트워크 오류: {e.reason}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    if not INDEXNOW_KEY:
        sys.exit("content/site.py 에 INDEXNOW_KEY 가 비어 있습니다.")
    urls = sitemap_urls() if args[0] == "--all" else args
    if not urls:
        sys.exit("제출할 URL이 없습니다.")
    submit(urls)


if __name__ == "__main__":
    main()
