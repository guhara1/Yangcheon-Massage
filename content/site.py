# 사이트 공통 설정
BASE_URL = "https://yangcheon-massage.netlify.app"

BRAND = "간다GO"
SITE_DESC = "양천구 전지역 방문 출장마사지·홈타이 예약 안내. 목동·신월동·신정동과 주요 지하철역 인근, 테마별 관리 정보를 제공합니다."
PHONE = "0508-202-4719"
PHONE_DISPLAY = "0508-202-4719"

# IndexNow 인증 키 — 루트에 {INDEXNOW_KEY}.txt 파일로도 게시된다(빌드 시 자동 생성).
# 빙·네이버·얀덱스 등 IndexNow 참여 검색엔진에 즉시 색인 통보할 때 사용한다.
INDEXNOW_KEY = "e144bd0c2d0741b78f79108f93b98bc4"

# 상단 메뉴 — 하위 메뉴에는 키워드를 반복하지 않고 지역명·역명만 표시한다.
NAV = [
    ("홈", "/", []),
    ("양천 출장마사지", "/massage/", [
        ("출장마사지 안내", "/massage/#service"),
        ("홈타이 안내", "/massage/#hometai"),
        ("전지역 방문 안내", "/massage/#coverage"),
        ("지하철역 인근 안내", "/massage/#stations"),
        ("예약 가능 시간", "/massage/#hours"),
        ("코스 선택 안내", "/massage/#course"),
        ("이용 전 확인사항", "/massage/#check"),
        ("위생·안전 안내", "/massage/#safety"),
        ("자주 묻는 질문", "/massage/#faq"),
    ]),
    ("지역별 안내", "/yangcheon/", [
        ("양천구 전체", "/yangcheon/"),
        ("목동", "/yangcheon/mok-dong/"),
        ("신월동", "/yangcheon/sinwol-dong/"),
        ("신정동", "/yangcheon/sinjeong-dong/"),
    ]),
    ("지하철역별 안내", "/yangcheon/stations/", [
        ("역 전체", "/yangcheon/stations/"),
        ("양천구청역", "/yangcheon/stations/yangcheon-gu-office-station/"),
        ("신정네거리역", "/yangcheon/stations/sinjeongnegeori-station/"),
        ("오목교역", "/yangcheon/stations/omokgyo-station/"),
        ("목동역", "/yangcheon/stations/mokdong-station/"),
        ("신정역", "/yangcheon/stations/sinjeong-station/"),
        ("신목동역", "/yangcheon/stations/sinmokdong-station/"),
    ]),
    ("테마별 안내", "/yangcheon/themes/", [
        ("전체 테마", "/yangcheon/themes/"),
        ("스웨디시", "/yangcheon/themes/swedish/"),
        ("로미로미", "/yangcheon/themes/lomilomi/"),
        ("타이마사지", "/yangcheon/themes/thai-massage/"),
        ("중국마사지", "/yangcheon/themes/chinese/"),
        ("아로마테라피", "/yangcheon/themes/aroma/"),
        ("홈케어", "/yangcheon/themes/homecare/"),
        ("호텔식마사지", "/yangcheon/themes/hotel-style/"),
        ("발마사지", "/yangcheon/themes/foot/"),
        ("스포츠·경락", "/yangcheon/themes/sports/"),
        ("스킨케어", "/yangcheon/themes/skincare/"),
        ("왁싱", "/yangcheon/themes/waxing/"),
        ("커플 관리", "/yangcheon/themes/couple/"),
        ("24시간", "/yangcheon/themes/24hours/"),
        ("수면 가능", "/yangcheon/themes/overnight/"),
    ]),
    ("코스안내", "/courses/", [
        ("전체 코스", "/courses/"),
        ("피로 회복 관리", "/courses/#recovery"),
        ("아로마 관리", "/courses/#aroma"),
        ("스포츠 관리", "/courses/#sports"),
        ("홈타이 코스", "/courses/#hometai"),
        ("커플·가족 방문 관리", "/courses/#couple"),
        ("기업·단체 방문 관리", "/courses/#group"),
        ("가격 안내", "/courses/#price"),
        ("코스 선택 가이드", "/courses/#guide"),
    ]),
    ("예약안내", "/reservation/", [
        ("예약 방법", "/reservation/#how"),
        ("예약 가능 시간", "/reservation/#hours"),
        ("방문 가능 장소", "/reservation/#place"),
        ("결제 안내", "/reservation/#payment"),
        ("변경·취소 안내", "/reservation/#change"),
        ("예약 전 체크사항", "/reservation/#check"),
    ]),
    ("이용가이드", "/guide/", [
        ("처음 이용하시는 분", "/guide/#first"),
        ("방문 전 준비사항", "/guide/#prepare"),
        ("위생 및 안전 기준", "/guide/#hygiene"),
        ("관리 후 주의사항", "/guide/#after"),
        ("금지행위 안내", "/guide/#prohibited"),
        ("이용 FAQ", "/guide/#faq"),
    ]),
    ("후기", "/reviews/", [
        ("전체 후기", "/reviews/"),
        ("지역별 후기", "/reviews/#area"),
        ("역세권 후기", "/reviews/#station"),
        ("후기 작성 안내", "/reviews/#write"),
    ]),
    ("고객센터", "/support/", [
        ("공지사항", "/support/#notice"),
        ("자주 묻는 질문", "/support/#faq"),
        ("1:1 문의", "/support/#contact"),
        ("제휴·기업 문의", "/support/#biz"),
        ("개인정보처리방침", "/support/privacy/"),
        ("이용약관", "/support/terms/"),
    ]),
]
