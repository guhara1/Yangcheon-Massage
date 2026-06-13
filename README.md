# 간다GO — 양천 출장마사지·홈타이 안내 사이트

양천구 전지역 방문 관리(출장마사지·홈타이) 안내용 정적 사이트입니다.
예약전화: **0508-202-4719**

## 구조

- 정적 HTML 사이트 — 어느 호스팅(GitHub Pages, Netlify, 일반 웹서버)에서든 그대로 서빙 가능
- `build.py` + `content/` 패키지에서 페이지를 생성하는 빌드 방식
- 생성물(각 디렉터리의 `index.html`, `sitemap.xml`, `robots.txt`)도 저장소에 포함

```
build.py            # 빌드 스크립트 (레이아웃·글자수 검사·sitemap 생성)
check.py            # 콘텐츠 모듈 단독 검증 (글자수·디스크립션 길이)
content/
  site.py           # 상호·전화·BASE_URL·메뉴 구조
  main.py           # 메인 페이지 (+ LocalBusiness/FAQPage JSON-LD)
  areas.py          # 지역별: 양천구 허브 + 목동·신월동·신정동
  stations.py       # 지하철역별: 허브 + 6개 역 (2호선 신정지선·5호선·9호선)
  themes.py         # 테마별: 허브 + 14개 테마
  info.py           # 출장마사지 안내·코스·예약·가이드·후기·고객센터·약관
  about.py          # 운영자 소개 (E-E-A-T)
assets/             # CSS, 모바일 내비 JS
```

## 빌드

```bash
python3 build.py
```

빌드 시 페이지별 본문 글자수 리포트가 출력됩니다.

## SEO 운영 원칙 (빌드에 강제됨)

- 본문 **2,000자 미만 페이지는 자동 `noindex`** 처리되고 sitemap에서 제외
- 메타 디스크립션은 네이버 기준 **80자 이내**
- 지역은 대표 동 3개만 (목동·신월동·신정동) — 숫자 행정동(목1동, 신월3동 등) 페이지 없음
- 역은 양천구 생활권 6개 역만 — 출구별 페이지 없음, 까치산역 등 인접 구 생활권 역 페이지 없음
- **지역+역+테마 조합 페이지 없음** (도어웨이 방지) — 테마는 독립 페이지로만 운영
- 상단/하위 메뉴와 푸터에 키워드·지역명·역명 대량 나열 없음
- 모든 페이지 본문은 페이지별 고유 작성 (지역명만 바꾼 복붙 없음)

## 배포 도메인

- 운영 도메인: `https://yangcheon-massage.pages.dev` (`content/site.py`의 `BASE_URL`)
- 도메인이 바뀌면 `BASE_URL`만 고치고 `python3 build.py`를 다시 돌리면 canonical·OG·sitemap·feed·robots에 일괄 반영됩니다.

## 색인 / SEO 산출물 (빌드 시 자동 생성)

| 파일 | 용도 |
|---|---|
| `sitemap.xml` | 색인 대상 34개 URL (lastmod·changefreq·priority 포함) |
| `feed.xml` | RSS 2.0 피드 — 네이버 서치어드바이저 RSS 수집·구독용 |
| `robots.txt` | 구글·빙·네이버(Yeti/NaverBot)·다음(Daumoa) 전면 허용 + 사이트맵 2종 명시 |
| `<INDEXNOW_KEY>.txt` | IndexNow 소유 확인 키 파일 (루트 게시) |

## 빠른 색인 운영 절차

```bash
python3 build.py                  # 1) sitemap.xml / feed.xml 갱신
python3 tools/indexnow.py --all   # 2) 빙·네이버 등 IndexNow 참여 엔진에 즉시 통보
```

- **IndexNow** (`tools/indexnow.py`): 빙·네이버·얀덱스 등에 변경 URL을 즉시 통보. 키 파일이 먼저 배포돼 있어야 합니다(빌드가 자동 생성). 특정 URL만 보내려면 `python3 tools/indexnow.py <url> [...]`.
- **구글 Indexing API** (`tools/google_indexing.py`): 구글은 IndexNow 미참여라 별도 경로. 서비스 계정 JSON + Search Console 소유자 등록 후 `GOOGLE_APPLICATION_CREDENTIALS`를 지정해 실행. 일반 페이지 색인은 보장되지 않으므로 **Search Console 사이트맵 제출이 구글의 기본 경로**입니다.
- **sitemap ping** (`tools/ping_sitemap.py`): 구글·빙의 ping 엔드포인트는 2023년 종료되어 효과가 없습니다. 호환용으로만 남겨 두었고, IndexNow로 대체하세요.

## 최초 1회 등록

1. **네이버 서치어드바이저**: 사이트 등록 → 소유확인(메인 페이지의 `naver-site-verification` 메타 태그) → `sitemap.xml`과 `feed.xml`(RSS) 제출.
2. **구글 Search Console**: 속성 등록 → `sitemap.xml` 제출.
3. **빙 웹마스터도구**: 사이트 등록(구글 Search Console에서 가져오기 가능) → IndexNow 키 자동 인식.

> 서비스 계정 키(`*.json`)는 절대 커밋하지 마세요. `.gitignore`에 자격증명 패턴이 포함되어 있습니다.
