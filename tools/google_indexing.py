#!/usr/bin/env python3
"""구글 Indexing API 색인 요청.

구글은 IndexNow에 참여하지 않으므로 별도 경로가 필요하다. 구글 Indexing API는
공식적으로 JobPosting·BroadcastEvent 구조화 데이터 페이지를 대상으로 하지만,
URL_UPDATED 통보로 크롤 우선순위를 올리는 용도로 널리 쓰인다. 일반 페이지는
효과가 보장되지 않으므로, 구글 색인의 기본은 Search Console 사이트맵 제출이다.

사전 준비:
  1) Google Cloud 프로젝트에서 'Indexing API' 사용 설정
  2) 서비스 계정 생성 → JSON 키 발급
  3) Search Console 속성에 서비스 계정 이메일을 '소유자'로 추가
  4) pip install google-auth requests

사용법:
  export GOOGLE_APPLICATION_CREDENTIALS=/path/service-account.json
  python3 tools/google_indexing.py --all
  python3 tools/google_indexing.py https://yangcheon-massage.pages.dev/yangcheon/mok-dong/
"""
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"


def sitemap_urls():
    tree = ET.parse(os.path.join(ROOT, "sitemap.xml"))
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text for loc in tree.findall(".//s:loc", ns)]


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        sys.exit("의존성 필요: pip install google-auth requests")

    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path or not os.path.exists(cred_path):
        sys.exit("GOOGLE_APPLICATION_CREDENTIALS 환경변수에 서비스 계정 JSON 경로를 지정하세요.")

    creds = service_account.Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    session = AuthorizedSession(creds)

    urls = sitemap_urls() if args[0] == "--all" else args
    for url in urls:
        body = {"url": url, "type": "URL_UPDATED"}
        r = session.post(ENDPOINT, json=body, timeout=30)
        print(f"{r.status_code}  {url}")
        if r.status_code != 200:
            print("   ", r.text.strip()[:300])


if __name__ == "__main__":
    main()
