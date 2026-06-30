#!/usr/bin/env python3
"""간다GO — 양천 출장마사지·홈타이 정적 사이트 빌드 스크립트.

content/ 패키지의 페이지 정의를 읽어 정적 HTML을 생성한다.

규칙(자동 적용):
  - 본문 텍스트 2,000자 미만 페이지는 robots noindex 처리
  - sitemap.xml 에는 index 허용 페이지만 포함
  - 지역+역+테마 조합 경로는 생성 자체가 불가능한 구조
"""
import html
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone

from content import PAGES
from content.site import (BASE_URL, BRAND, NAV, PHONE, PHONE_DISPLAY)
from content.reviews_data import ALL_REVIEWS, aggregate

try:
    from content.site import SITE_DESC
except ImportError:
    SITE_DESC = ""
try:
    from content.site import INDEXNOW_KEY
except ImportError:
    INDEXNOW_KEY = ""

ROOT = os.path.dirname(os.path.abspath(__file__))
MIN_INDEX_CHARS = 2000


def text_length(body_html: str) -> int:
    """태그를 제거한 본문 글자수(공백 포함, 연속 공백은 1자).
    공통 요금 블록은 페이지 고유 본문이 아니므로 측정에서 제외한다."""
    text = re.sub(r'<section class="pricing">.*?</section>', " ", body_html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text)


def render_nav(current_path: str) -> str:
    items = []
    for label, href, children in NAV:
        active = " is-active" if href == "/" + current_path else ""
        if children:
            sub = "".join(
                f'<li><a href="{c_href}">{c_label}</a></li>'
                for c_label, c_href in children
            )
            items.append(
                f'<li class="nav-item has-sub{active}">'
                f'<a href="{href}">{label}</a>'
                f'<ul class="sub-menu">{sub}</ul></li>'
            )
        else:
            items.append(
                f'<li class="nav-item{active}"><a href="{href}">{label}</a></li>'
            )
    return "".join(items)


def render_breadcrumb(crumbs) -> str:
    if not crumbs:
        return ""
    parts = ['<nav class="breadcrumb" aria-label="현재 위치"><ol>']
    parts.append('<li><a href="/">홈</a></li>')
    for label, href in crumbs:
        if href:
            parts.append(f'<li><a href="{href}">{label}</a></li>')
        else:
            parts.append(f"<li><span>{label}</span></li>")
    parts.append("</ol></nav>")
    return "".join(parts)


def inject_toc(body: str):
    """본문 섹션(h2)에 id를 보장하고 좌측 목차 데이터를 만든다."""
    items = []
    counter = [0]

    def repl(m):
        attrs, title = m.group(1), m.group(2)
        idm = re.search(r'id="([^"]+)"', attrs)
        if idm:
            sid = idm.group(1)
            opening = f"<section{attrs}>"
        else:
            counter[0] += 1
            sid = f"sec-{counter[0]}"
            opening = f'<section id="{sid}"{attrs}>'
        label = re.sub(r"<[^>]+>", "", title).strip()
        items.append((sid, label))
        return f"{opening}<h2>{title}</h2>"

    body = re.sub(r"<section([^>]*)>\s*<h2>(.*?)</h2>", repl, body, flags=re.S)
    return body, items


def render_toc(items) -> str:
    if len(items) < 3:
        return ""
    links = "".join(
        f'<li><a href="#{sid}">{label}</a></li>' for sid, label in items
    )
    return (
        '<aside class="page-toc"><nav aria-label="페이지 목차">'
        '<p class="toc-title">목차</p>'
        f"<ul>{links}</ul></nav></aside>"
    )


# ── 구조화 데이터(JSON-LD) ──────────────────────────────────────────────
_BASE = BASE_URL.rstrip("/")
_BUSINESS_ID = _BASE + "/#business"

AREAS = {
    "mok-dong": "목동", "sinwol-dong": "신월동", "sinjeong-dong": "신정동",
}
STATIONS = {
    "yangcheon-gu-office-station": "양천구청역",
    "sinjeongnegeori-station": "신정네거리역",
    "omokgyo-station": "오목교역",
    "mokdong-station": "목동역",
    "sinjeong-station": "신정역",
    "sinmokdong-station": "신목동역",
}
THEMES = {
    "swedish": "스웨디시", "lomilomi": "로미로미", "thai-massage": "타이마사지",
    "chinese": "중국마사지", "aroma": "아로마테라피", "homecare": "홈케어",
    "hotel-style": "호텔식마사지", "foot": "발마사지", "sports": "스포츠·경락",
    "skincare": "스킨케어", "waxing": "왁싱", "couple": "커플 관리",
    "24hours": "24시간", "overnight": "수면 가능",
}

_FAQ_RE = re.compile(
    r'<div class="faq-item">\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>', re.S
)


def _plain(text: str) -> str:
    """태그를 제거해 JSON-LD용 순수 텍스트로 만든다."""
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _business_node(with_rating=False, with_reviews=False) -> dict:
    node = {
        "@type": "HealthAndBeautyBusiness",
        "@id": _BUSINESS_ID,
        "name": BRAND,
        "telephone": PHONE,
        "url": _BASE + "/",
        "image": _BASE + "/assets/og-image.png",
        "description": "양천구 전지역 방문 출장마사지·홈타이 예약 안내",
        "areaServed": {"@type": "AdministrativeArea", "name": "서울특별시 양천구"},
        "address": {
            "@type": "PostalAddress",
            "addressRegion": "서울특별시",
            "addressLocality": "양천구",
            "addressCountry": "KR",
        },
        "openingHoursSpecification": {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday",
                          "Friday", "Saturday", "Sunday"],
            "opens": "00:00", "closes": "23:59",
        },
        "priceRange": "₩90,000 - ₩180,000",
    }
    if with_rating:
        agg = aggregate()
        node["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": agg["value"],
            "reviewCount": agg["count"],
            "bestRating": agg["best"],
            "worstRating": agg["worst"],
        }
    if with_reviews:
        node["review"] = [
            {
                "@type": "Review",
                "author": {"@type": "Person", "name": f'{r["loc"]} {r["author"]}님'},
                "datePublished": r["date"],
                "reviewRating": {
                    "@type": "Rating", "ratingValue": r["rating"],
                    "bestRating": 5, "worstRating": 1,
                },
                "reviewBody": r["text"],
            }
            for r in ALL_REVIEWS
        ]
    return node


def _breadcrumb_node(page: dict, canonical: str) -> dict:
    crumbs = page.get("breadcrumb") or []
    items = [{"@type": "ListItem", "position": 1, "name": "홈", "item": _BASE + "/"}]
    pos = 2
    for label, href in crumbs:
        item = _BASE + href if href else canonical
        items.append({"@type": "ListItem", "position": pos, "name": label, "item": item})
        pos += 1
    return {"@type": "BreadcrumbList", "itemListElement": items}


def _service_node(name: str, canonical: str) -> dict:
    return {
        "@type": "Service",
        "name": f"양천 {name} 출장마사지·홈타이",
        "serviceType": name,
        "provider": {"@id": _BUSINESS_ID},
        "areaServed": {"@type": "AdministrativeArea", "name": "서울특별시 양천구"},
        "url": canonical,
        "offers": {
            "@type": "AggregateOffer",
            "priceCurrency": "KRW",
            "lowPrice": "90000",
            "highPrice": "180000",
        },
    }


def build_jsonld(page: dict, canonical: str) -> str:
    """페이지 유형에 맞는 JSON-LD를 @graph 하나로 생성한다."""
    path = page["path"]
    is_home = path == ""
    is_reviews = path == "reviews/"

    nodes = [_business_node(with_rating=is_reviews, with_reviews=is_reviews)]

    if is_home:
        nodes.append({
            "@type": "WebSite", "@id": _BASE + "/#website",
            "name": BRAND, "url": _BASE + "/", "inLanguage": "ko",
            "publisher": {"@id": _BUSINESS_ID},
        })

    if page.get("breadcrumb"):
        nodes.append(_breadcrumb_node(page, canonical))

    faqs = [
        {"@type": "Question", "name": _plain(q),
         "acceptedAnswer": {"@type": "Answer", "text": _plain(a)}}
        for q, a in _FAQ_RE.findall(page["body"])
    ]
    if faqs:
        nodes.append({"@type": "FAQPage", "mainEntity": faqs})

    # 테마 상세 페이지와 출장마사지 안내 페이지에 Service 노드
    if path.startswith("yangcheon/themes/") and path != "yangcheon/themes/":
        slug = path.split("/")[2]
        nodes.append(_service_node(THEMES.get(slug, "방문 관리"), canonical))
    elif path == "massage/":
        nodes.append(_service_node("출장마사지·홈타이", canonical))

    graph = {"@context": "https://schema.org", "@graph": nodes}
    return ('<script type="application/ld+json">\n'
            + json.dumps(graph, ensure_ascii=False, indent=2)
            + "\n</script>\n")


# ── 내부 링크 강화(롱테일 관련 안내) ────────────────────────────────────
# 지역 ↔ 인근 역 ↔ 추천 테마 매핑 (각 페이지 본문의 문맥과 일치)
_AREA_LINKS = {
    "mok-dong": (["omokgyo-station", "mokdong-station", "sinmokdong-station"],
                 ["aroma", "couple"], ["sinjeong-dong"]),
    "sinwol-dong": (["sinjeong-station"], ["homecare", "24hours"], ["sinjeong-dong"]),
    "sinjeong-dong": (["yangcheon-gu-office-station", "sinjeongnegeori-station",
                       "sinjeong-station"], ["sports"], ["mok-dong"]),
}
# 역 → 소속 지역, 추천 테마
_STATION_LINKS = {
    "yangcheon-gu-office-station": ("sinjeong-dong", ["sports", "homecare"]),
    "sinjeongnegeori-station": ("sinjeong-dong", ["foot", "chinese"]),
    "omokgyo-station": ("mok-dong", ["swedish", "sports", "24hours"]),
    "mokdong-station": ("mok-dong", ["thai-massage", "aroma"]),
    "sinjeong-station": ("sinjeong-dong", ["lomilomi", "homecare"]),
    "sinmokdong-station": ("mok-dong", ["foot", "swedish", "couple"]),
}
# 테마 → 연관 테마
_THEME_LINKS = {
    "swedish": ["aroma", "sports"], "lomilomi": ["swedish", "chinese"],
    "thai-massage": ["swedish", "chinese"], "chinese": ["sports", "lomilomi"],
    "aroma": ["lomilomi", "overnight"], "homecare": ["swedish", "thai-massage"],
    "hotel-style": ["couple", "homecare"], "foot": ["swedish", "sports"],
    "sports": ["chinese", "foot"], "skincare": ["swedish", "waxing"],
    "waxing": ["skincare", "couple"], "couple": ["hotel-style", "homecare"],
    "24hours": ["overnight", "homecare"], "overnight": ["aroma", "24hours"],
}


def _area_href(slug):
    return (f"/yangcheon/{slug}/", f"{AREAS[slug]} 출장마사지·홈타이")


def _station_href(slug):
    return (f"/yangcheon/stations/{slug}/", f"{STATIONS[slug]} 인근 방문 마사지")


def _theme_href(slug):
    return (f"/yangcheon/themes/{slug}/", f"양천 {THEMES[slug]} 마사지 안내")


def related_links(path: str):
    """페이지 경로에 맞는 롱테일 관련 링크 목록 (href, label)."""
    links = []
    if path == "":
        links = [
            _area_href("mok-dong"), _station_href("omokgyo-station"),
            _theme_href("swedish"), _theme_href("24hours"),
            ("/reviews/", "양천 출장마사지 이용 후기"),
            ("/courses/", "코스·요금 안내"),
        ]
    elif path in (f"yangcheon/{s}/" for s in AREAS):
        slug = path.split("/")[1]
        stations, themes, others = _AREA_LINKS[slug]
        links = [_station_href(s) for s in stations]
        links += [_theme_href(t) for t in themes]
        links += [_area_href(o) for o in others]
        links.append(("/reviews/", "지역별 이용 후기"))
    elif path.startswith("yangcheon/stations/") and path != "yangcheon/stations/":
        slug = path.split("/")[2]
        area, themes = _STATION_LINKS[slug]
        links = [_area_href(area)]
        links += [_theme_href(t) for t in themes]
        links += [("/yangcheon/stations/", "양천 지하철역별 안내"),
                  ("/reservation/", "예약 방법·시간 안내")]
    elif path.startswith("yangcheon/themes/") and path != "yangcheon/themes/":
        slug = path.split("/")[2]
        links = [_theme_href(t) for t in _THEME_LINKS.get(slug, [])]
        links += [("/yangcheon/", "양천구 지역별 안내"),
                  ("/yangcheon/stations/", "양천 지하철역별 안내"),
                  ("/courses/", "코스·요금 안내")]
    elif path == "yangcheon/":
        links = [_area_href("mok-dong"), _area_href("sinwol-dong"),
                 _area_href("sinjeong-dong"),
                 ("/yangcheon/stations/", "양천 지하철역별 안내"),
                 ("/yangcheon/themes/", "양천 테마별 관리 안내")]
    elif path == "yangcheon/stations/":
        links = [_station_href("omokgyo-station"), _station_href("mokdong-station"),
                 ("/yangcheon/", "양천구 지역별 안내"),
                 ("/yangcheon/themes/", "양천 테마별 관리 안내"),
                 ("/reviews/", "역세권 이용 후기")]
    elif path == "yangcheon/themes/":
        links = [_theme_href("swedish"), _theme_href("aroma"),
                 _theme_href("sports"),
                 ("/yangcheon/", "양천구 지역별 안내"),
                 ("/courses/", "코스·요금 안내")]
    elif path == "massage/":
        links = [("/yangcheon/", "양천구 지역별 안내"),
                 ("/yangcheon/stations/", "양천 지하철역별 안내"),
                 ("/yangcheon/themes/", "양천 테마별 관리 안내"),
                 ("/courses/", "코스·요금 안내"),
                 ("/reservation/", "예약 방법 안내")]
    elif path == "courses/":
        links = [("/yangcheon/themes/", "양천 테마별 관리 안내"),
                 ("/reservation/", "예약 방법 안내"),
                 ("/massage/", "양천 출장마사지 안내"),
                 ("/reviews/", "이용 후기")]
    elif path == "reservation/":
        links = [("/guide/", "이용 가이드"),
                 ("/courses/", "코스·요금 안내"),
                 ("/massage/", "양천 출장마사지 안내"),
                 ("/yangcheon/", "양천구 지역별 안내")]
    elif path == "guide/":
        links = [("/reservation/", "예약 방법 안내"),
                 ("/massage/", "양천 출장마사지 안내"),
                 ("/reviews/", "이용 후기"),
                 ("/support/", "고객센터")]
    elif path == "reviews/":
        links = [("/yangcheon/", "양천구 지역별 안내"),
                 ("/yangcheon/stations/", "양천 지하철역별 안내"),
                 ("/guide/", "이용 가이드"),
                 ("/reservation/", "예약 방법 안내")]
    elif path == "support/":
        links = [("/reservation/", "예약 방법 안내"),
                 ("/guide/", "이용 가이드"),
                 ("/about/", "운영자 소개")]
    elif path == "about/":
        links = [("/massage/", "양천 출장마사지 안내"),
                 ("/support/", "고객센터"),
                 ("/reviews/", "이용 후기")]
    return links


def render_related(path: str) -> str:
    links = related_links(path)
    if not links:
        return ""
    cards = "".join(
        f'<li><a href="{href}">{label}</a></li>' for href, label in links
    )
    return (
        '<section class="related-links" aria-label="관련 안내">'
        "<h2>함께 보면 좋은 안내</h2>"
        f'<ul class="card-grid">{cards}</ul></section>'
    )


def render_page(page: dict) -> str:
    path = page["path"]
    title = page["title"]
    desc = page["desc"]
    h1 = page["h1"]
    body = page["body"]
    crumbs = page.get("breadcrumb") or []
    extra_head = page.get("extra_head", "")
    hero = page.get("hero", "")

    chars = text_length(body)
    noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
    robots = (
        '<meta name="robots" content="noindex,follow">'
        if noindex
        else '<meta name="robots" content="index,follow">'
    )
    canonical = BASE_URL.rstrip("/") + "/" + path

    # 히어로가 있는 페이지(메인)는 H1을 히어로 안에서 출력한다.
    if hero:
        page_head = hero
    else:
        page_head = ""

    h1_html = "" if hero else f"<h1>{h1}</h1>"

    body, toc_items = inject_toc(body)
    toc_html = render_toc(toc_items)
    layout_cls = "page-layout has-toc" if toc_html else "page-layout"

    # 롱테일 관련 안내 섹션을 CTA 직전에 삽입 (없으면 본문 끝에)
    related_html = render_related(path)
    if related_html:
        if '<section class="cta"' in body:
            body = body.replace('<section class="cta"', related_html + '<section class="cta"', 1)
        else:
            body += related_html

    jsonld = build_jsonld(page, canonical)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:image" content="{BASE_URL.rstrip('/')}/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE_URL.rstrip('/')}/assets/og-image.png">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta name="theme-color" content="#0a1120">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@600;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
{extra_head}{jsonld}</head>
<body>
<header class="site-header">
  <div class="header-accent" aria-hidden="true"></div>
  <div class="header-top">
    <div class="header-inner">
      <a class="brand" href="/"><span class="brand-mark">G</span> <span class="brand-text">{BRAND}</span></a>
      <p class="header-tagline"><span class="tag-gem">◆</span> 양천구 전지역 방문 관리 <span class="tag-gem">◆</span> 24시간 상담</p>
      <a class="header-call" href="tel:{PHONE}"><span class="call-label">예약전화</span> {PHONE_DISPLAY}</a>
      <button class="nav-toggle" aria-label="메뉴 열기" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </div>
  <nav class="main-nav" aria-label="주 메뉴">
    <div class="nav-inner"><ul class="nav-list">{render_nav(path)}</ul></div>
  </nav>
</header>
{page_head}<main class="site-main">
  <div class="container {layout_cls}">
    {toc_html}
    <article class="page-content">
      {render_breadcrumb(crumbs)}
      {h1_html}
      {body}
    </article>
  </div>
</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <div class="footer-col footer-about">
      <p class="footer-brand">{BRAND}</p>
      <p class="footer-desc">양천구 전지역 방문 출장마사지·홈타이 안내 사이트입니다. 모든 서비스는 안내된 관리 범위와 위생·안전 기준 안에서만 제공됩니다.</p>
      <address class="footer-contact">
        <span class="footer-contact-row"><span class="footer-label">예약전화</span> <a href="tel:{PHONE}">{PHONE_DISPLAY}</a></span>
        <span class="footer-contact-row"><span class="footer-label">상담시간</span> 연중무휴 24시간</span>
        <span class="footer-contact-row"><span class="footer-label">서비스 지역</span> 서울특별시 양천구 전지역</span>
      </address>
    </div>
    <nav class="footer-col" aria-label="서비스 안내">
      <p class="footer-title">서비스</p>
      <ul>
        <li><a href="/massage/">양천 출장마사지</a></li>
        <li><a href="/yangcheon/">지역별 안내</a></li>
        <li><a href="/yangcheon/stations/">지하철역별 안내</a></li>
        <li><a href="/yangcheon/themes/">테마별 안내</a></li>
        <li><a href="/courses/">코스안내</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="이용 안내">
      <p class="footer-title">이용 안내</p>
      <ul>
        <li><a href="/reservation/">예약안내</a></li>
        <li><a href="/guide/">이용가이드</a></li>
        <li><a href="/reviews/">이용 후기</a></li>
        <li><a href="/support/">고객센터</a></li>
        <li><a href="/support/#faq">자주 묻는 질문</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="정책 및 기준">
      <p class="footer-title">정책</p>
      <ul>
        <li><a href="/about/">운영자 소개</a></li>
        <li><a href="/support/privacy/">개인정보처리방침</a></li>
        <li><a href="/support/terms/">이용약관</a></li>
        <li><a href="/guide/#hygiene">위생·안전 기준</a></li>
        <li><a href="/guide/#prohibited">금지행위 안내</a></li>
        <li><a href="/support/#biz">제휴·기업 문의</a></li>
      </ul>
    </nav>
  </div>
  <div class="footer-bottom">
    <div class="container footer-bottom-inner">
      <p class="footer-copy">&copy; {BRAND}. All rights reserved.</p>
      <p class="footer-note">건전한 방문 관리 서비스를 운영하며, 불법적인 요청은 어떤 경우에도 응하지 않습니다.</p>
      <a class="footer-made" href="https://t.me/googleseolab" target="_blank" rel="noopener nofollow">웹사이트 제작문의 ↗</a>
    </div>
  </div>
</footer>
<a class="call-fab" href="tel:{PHONE}" aria-label="전화 예약 {PHONE_DISPLAY}">
  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
  <span class="call-fab-label">예약 전화</span>
</a>
<script src="/assets/nav.js"></script>
</body>
</html>
"""


def build() -> None:
    base = BASE_URL.rstrip("/")
    report = []
    sitemap_items = []  # (url, page)

    for page in PAGES:
        path = page["path"]  # "" 또는 "yangcheon/mok-dong/" 형태
        out_dir = os.path.join(ROOT, path)
        os.makedirs(out_dir, exist_ok=True)
        html_out = render_page(page)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_out)

        chars = text_length(page["body"])
        noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
        if not noindex:
            sitemap_items.append((base + "/" + path, page))
        report.append((path or "/", chars, "noindex" if noindex else "index"))

    now = datetime.now(timezone.utc)
    lastmod = now.strftime("%Y-%m-%d")

    # sitemap.xml — 메인은 우선순위 1.0/일간, 그 외 0.8/주간
    rows = []
    for url, page in sitemap_items:
        is_home = page["path"] == ""
        rows.append(
            f"  <url><loc>{html.escape(url)}</loc>"
            f"<lastmod>{lastmod}</lastmod>"
            f"<changefreq>{'daily' if is_home else 'weekly'}</changefreq>"
            f"<priority>{'1.0' if is_home else '0.8'}</priority></url>"
        )
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(rows)
            + "\n</urlset>\n"
        )

    # feed.xml (RSS 2.0) — sitemap에 포함된 페이지를 항목으로 게시
    pubdate = now.strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = []
    for url, page in sitemap_items:
        items.append(
            "  <item>\n"
            f"    <title>{html.escape(page['title'])}</title>\n"
            f"    <link>{html.escape(url)}</link>\n"
            f"    <guid isPermaLink=\"true\">{html.escape(url)}</guid>\n"
            f"    <description>{html.escape(page['desc'])}</description>\n"
            f"    <pubDate>{pubdate}</pubDate>\n"
            "  </item>"
        )
    with open(os.path.join(ROOT, "feed.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
            "<channel>\n"
            f"  <title>{html.escape(BRAND)} — 양천 출장마사지·홈타이</title>\n"
            f"  <link>{base}/</link>\n"
            f"  <description>{html.escape(SITE_DESC)}</description>\n"
            "  <language>ko</language>\n"
            f"  <lastBuildDate>{pubdate}</lastBuildDate>\n"
            f'  <atom:link href="{base}/feed.xml" rel="self" type="application/rss+xml"/>\n'
            + "\n".join(items)
            + "\n</channel>\n</rss>\n"
        )

    # robots.txt — 주요 검색엔진(구글·빙·네이버·다음) 전면 허용 + 사이트맵 명시
    bots = ["Googlebot", "Googlebot-Image", "bingbot", "Yeti", "Daumoa", "NaverBot"]
    lines = ["User-agent: *", "Allow: /", ""]
    for bot in bots:
        lines += [f"User-agent: {bot}", "Allow: /", ""]
    lines += [
        f"Sitemap: {base}/sitemap.xml",
        f"Sitemap: {base}/feed.xml",
        "",
    ]
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # IndexNow 키 파일 — 루트에 {KEY}.txt 로 게시(소유 확인용)
    if INDEXNOW_KEY:
        with open(os.path.join(ROOT, f"{INDEXNOW_KEY}.txt"), "w", encoding="utf-8") as f:
            f.write(INDEXNOW_KEY + "\n")

    # .nojekyll (정적 호스팅에서 _ 디렉터리 보존)
    open(os.path.join(ROOT, ".nojekyll"), "w").close()

    width = max(len(p) for p, _, _ in report)
    print(f"{'PATH'.ljust(width)}  CHARS  ROBOTS")
    for p, c, r in sorted(report):
        flag = "" if (r == "noindex" or MIN_INDEX_CHARS <= c <= 2500) else "  ⚠"
        print(f"{p.ljust(width)}  {str(c).rjust(5)}  {r}{flag}")
    print(f"\n{len(report)} pages built, {len(sitemap_items)} in sitemap/feed.")
    if INDEXNOW_KEY:
        print(f"IndexNow key file: /{INDEXNOW_KEY}.txt")


if __name__ == "__main__":
    build()
