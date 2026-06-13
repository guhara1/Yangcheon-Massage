# 메인 페이지 — 양천구 허브. 상세 내용은 지역·역·테마 페이지로 연결한다.
import json

from .site import BASE_URL, BRAND, PHONE, PHONE_DISPLAY
from .pricing import PRICING

# FAQ는 본문과 JSON-LD에서 동일하게 사용한다.
_FAQS = [
    (
        "양천구 어느 동이든 방문 예약이 가능한가요?",
        "목동, 신월동, 신정동을 비롯한 양천구 전지역이 안내 대상입니다. 다만 예약 시간대와 관리사 배정 상황, 정확한 위치에 따라 가능 여부가 달라질 수 있어 전화 상담에서 최종 확인해 드립니다.",
    ),
    (
        "오목교역이나 목동역 근처 오피스텔로도 방문이 되나요?",
        "자택, 오피스텔, 숙소 모두 방문 대상입니다. 역 인근 정보는 양천구청역, 신정네거리역, 오목교역, 목동역, 신정역, 신목동역 페이지에서 주변 생활권과 함께 확인하실 수 있습니다.",
    ),
    (
        "목1동이나 신월3동 같은 행정동 페이지는 왜 따로 없나요?",
        "숫자로 나뉜 행정동은 생활권이 사실상 이어져 있어 목동, 신월동, 신정동 대표 페이지에서 묶어 안내합니다. 비슷한 페이지를 늘리기보다 한 페이지의 정확도를 높이기 위한 원칙입니다.",
    ),
    (
        "새벽 시간에도 예약 상담이 가능한가요?",
        "예약 상담은 24시간 받고 있습니다. 다만 심야와 주말에는 배정이 일찍 마감될 수 있으므로 한두 시간 이상 여유를 두고 연락해 주시면 원하시는 시간에 맞추기 수월합니다.",
    ),
    (
        "코스와 테마는 어떻게 고르면 되나요?",
        "관리 유형은 테마별 안내 페이지에서, 시간은 60·90·120분 코스 중에서 고르시면 됩니다. 선택이 어려우시면 전화로 그날의 컨디션을 말씀해 주세요. 상담에서 함께 정해 드립니다.",
    ),
]

_FAQ_JSONLD = json.dumps(
    {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in _FAQS
        ],
    },
    ensure_ascii=False,
    indent=2,
)

_JSONLD = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "HealthAndBeautyBusiness",
  "name": "{BRAND}",
  "telephone": "{PHONE}",
  "url": "{BASE_URL}/",
  "image": "{BASE_URL}/assets/og-image.png",
  "description": "양천구 전지역 방문 출장마사지·홈타이 예약 안내",
  "areaServed": {{
    "@type": "AdministrativeArea",
    "name": "서울특별시 양천구"
  }},
  "openingHours": "Mo-Su 00:00-24:00",
  "priceRange": "₩90,000 - ₩180,000"
}}
</script>
<script type="application/ld+json">
{_FAQ_JSONLD}
</script>
"""

_HERO = f"""<section class="hero">
  <div class="hero-inner">
    <p class="hero-badge">Premium Visiting Care · 양천구 전지역</p>
    <h1>양천 출장마사지·홈타이<br>예약 안내</h1>
    <p class="hero-lead">이동도 대기도 없이, 머무시는 공간이 그대로 관리실이 됩니다.<br>위치와 시간만 알려주시면 {BRAND}가 바로 확인해 드립니다.</p>
    <div class="hero-actions">
      <a class="hero-btn primary" href="tel:{PHONE}">📞 {PHONE_DISPLAY}</a>
      <a class="hero-btn" href="/courses/">코스 안내 보기</a>
    </div>
    <ul class="hero-stats">
      <li><strong>3개</strong><span>대표 지역</span></li>
      <li><strong>6개</strong><span>역세권 안내</span></li>
      <li><strong>14개</strong><span>관리 테마</span></li>
      <li><strong>24시간</strong><span>예약 상담</span></li>
    </ul>
  </div>
</section>
"""

_FAQ_HTML = "\n".join(
    f'<div class="faq-item">\n<h3>{q}</h3>\n<p>{a}</p>\n</div>' for q, a in _FAQS
)

_BODY = f"""
<section id="service">
<h2>양천 출장마사지·홈타이 서비스 안내</h2>
<p>양천구에서 방문 마사지나 홈타이를 알아보실 때 가장 먼저 궁금한 것은 우리 집까지 오는지, 비용이 얼마인지, 어떻게 예약하는지일 것입니다. 이 페이지는 그 세 가지 질문에 답하는 양천구 전체 안내의 출발점입니다. {BRAND}는 양천구를 대상으로 예약 상담과 방문 관리를 직접 운영하며, 동별·역별 세부 내용은 각 상세 페이지에 나누어 정리했습니다.</p>
</section>

<section id="coverage">
<h2>양천구 전지역 방문 가능 안내</h2>
<p>양천구의 행정동은 목1동부터 목5동, 신월1동부터 신월7동, 신정1동부터 신정4동과 신정6동·신정7동으로 나뉘지만, 지역 안내 페이지는 목동, 신월동, 신정동 세 개 대표 동으로 통합해 운영합니다. 숫자 동마다 페이지를 따로 두면 같은 생활권 설명이 반복될 뿐이기 때문입니다. 어느 행정동에 계시든 해당 대표 동 페이지에서 방문 조건을 확인하시면 됩니다.</p>
</section>

<section id="areas">
<h2>지역별 안내</h2>
<p>대표 동 페이지에서는 각 생활권의 특징, 가까운 지하철역, 자주 선택되는 시간대와 어울리는 테마를 동마다 다른 내용으로 다룹니다. 지금 계신 동을 선택해 주세요.</p>
<ul class="card-grid">
<li><a href="/yangcheon/mok-dong/">목동</a></li>
<li><a href="/yangcheon/sinwol-dong/">신월동</a></li>
<li><a href="/yangcheon/sinjeong-dong/">신정동</a></li>
</ul>
<p>세 지역의 전체 구조는 <a href="/yangcheon/">양천구 전체 안내</a>에서 한눈에 비교하실 수 있습니다.</p>
</section>

<section id="stations">
<h2>지하철역 인근 안내</h2>
<p>양천구는 2호선 신정지선이 양천구청역과 신정네거리역을, 5호선이 오목교역·목동역·신정역을, 9호선이 신목동역을 지납니다. 역별 페이지에서는 인근 생활권과 대표 동, 방문 전 준비사항을 안내하며, 출구별 페이지나 역과 테마를 조합한 페이지는 만들지 않습니다.</p>
<ul class="card-grid">
<li><a href="/yangcheon/stations/yangcheon-gu-office-station/">양천구청역</a></li>
<li><a href="/yangcheon/stations/sinjeongnegeori-station/">신정네거리역</a></li>
<li><a href="/yangcheon/stations/omokgyo-station/">오목교역</a></li>
<li><a href="/yangcheon/stations/mokdong-station/">목동역</a></li>
<li><a href="/yangcheon/stations/sinjeong-station/">신정역</a></li>
<li><a href="/yangcheon/stations/sinmokdong-station/">신목동역</a></li>
</ul>
<p>역 전체 목록과 노선 구조는 <a href="/yangcheon/stations/">지하철역별 안내</a>에서 확인해 주세요.</p>
</section>

<section id="themes">
<h2>테마별 관리 안내</h2>
<p>관리 유형은 열네 가지 테마로 나누어 각각 독립 페이지에서 특징과 추천 대상, 예약 전 확인사항을 설명합니다. 위치와 무관하게 어느 테마든 선택하실 수 있으니, 유형을 먼저 정하신 뒤 예약 시 주소를 알려주시면 됩니다. 전체 비교는 <a href="/yangcheon/themes/">테마별 안내</a>에 있습니다.</p>
<ul class="card-grid">
<li><a href="/yangcheon/themes/swedish/">스웨디시</a></li>
<li><a href="/yangcheon/themes/lomilomi/">로미로미</a></li>
<li><a href="/yangcheon/themes/thai-massage/">타이마사지</a></li>
<li><a href="/yangcheon/themes/chinese/">중국마사지</a></li>
<li><a href="/yangcheon/themes/aroma/">아로마테라피</a></li>
<li><a href="/yangcheon/themes/homecare/">홈케어</a></li>
<li><a href="/yangcheon/themes/hotel-style/">호텔식마사지</a></li>
<li><a href="/yangcheon/themes/foot/">발마사지</a></li>
<li><a href="/yangcheon/themes/sports/">스포츠·경락</a></li>
<li><a href="/yangcheon/themes/skincare/">스킨케어</a></li>
<li><a href="/yangcheon/themes/waxing/">왁싱</a></li>
<li><a href="/yangcheon/themes/couple/">커플 관리</a></li>
<li><a href="/yangcheon/themes/24hours/">24시간</a></li>
<li><a href="/yangcheon/themes/overnight/">수면 가능</a></li>
</ul>
</section>

<section id="course">
<h2>코스 선택 안내</h2>
<p>시간은 60분, 90분, 120분 가운데 고르시면 됩니다. 가볍게 풀고 싶은 날은 60분, 아로마를 포함해 균형 있게 받고 싶다면 90분, 누적 피로가 큰 날은 120분이 무난한 기준입니다. 목적별 추천 구성은 <a href="/courses/">코스안내</a>에 정리했으며, 고민되시면 상담 전화에서 그날의 상태를 말씀해 주시면 알맞은 코스를 권해 드립니다.</p>
</section>

<section id="how">
<h2>예약 진행 방식</h2>
<p>전화 한 통으로 위치 확인, 시간 확인, 코스·인원 결정, 배정 확인, 예약 확정까지 이어집니다. 저녁과 주말은 문의가 몰리는 시간대이므로 미리 연락 주시는 편이 좋습니다. 단계별 설명은 <a href="/reservation/">예약안내</a>를 참고해 주세요.</p>
</section>

<section id="check">
<h2>이용 전 확인사항</h2>
<p>방문 전에 정확한 주소와 공동현관 출입 방법, 주차 또는 정차 가능 여부, 관리할 수 있는 조용한 공간을 확인해 주시면 진행이 매끄럽습니다. 오피스텔이나 숙소라면 호수와 출입 절차, 예약 시간대에 연락 가능한 번호를 함께 알려주세요. 준비물 목록 전체는 <a href="/guide/">이용가이드</a>에 있습니다.</p>
</section>

<section id="safety">
<h2>위생 및 안전 안내</h2>
<p>{BRAND}는 건전한 방문 관리만을 운영합니다. 관리사는 방문마다 소독된 도구와 교체된 준비물을 사용하며, 예약 정보는 방문 확인 목적 외에 쓰지 않습니다. 서비스 범위를 벗어나는 요청과 불법적인 요청은 어떤 경우에도 거절하며, 이 기준은 상담 단계에서부터 동일하게 적용됩니다.</p>
</section>

<section id="faq">
<h2>자주 묻는 질문</h2>
{_FAQ_HTML}
</section>

{PRICING}
<section id="contact" class="cta">
<h2>예약문의</h2>
<p>양천구 방문 관리 상담은 전화가 가장 빠릅니다. 위치와 희망 시간을 알려주시면 가능 여부를 바로 확인해 드립니다.</p>
<a class="cta-phone" href="tel:{PHONE}">{PHONE_DISPLAY}</a>
</section>
"""

PAGE = {
    "path": "",
    "title": "양천 출장마사지·홈타이 | 양천구 전지역 방문 마사지 예약 안내",
    "desc": "양천 출장마사지·홈타이 안내. 목동·신월동·신정동, 오목교역·목동역 등 양천구 주요 지역과 역 인근 예약 정보를 확인해보세요.",
    "h1": "양천 출장마사지·홈타이 예약 안내",
    "body": _BODY,
    "extra_head": '<meta name="naver-site-verification" content="79a0881380aafdc13c603dc32de892b0da564c56">\n' + _JSONLD,
    "breadcrumb": [],
    "hero": _HERO,
}
