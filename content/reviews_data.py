# 이용 후기 구조화 데이터 — 화면(HTML)과 JSON-LD(Review/AggregateRating)의 단일 출처.
# 실제 이용이 확인된 예약 건 기준으로만 작성하며, 이름은 이니셜로만 표기한다.

# 지역별 후기 (목동·신월동·신정동)
AREA_REVIEWS = [
    {"author": "K", "loc": "목동", "rating": 5, "date": "2025-04-12",
     "text": "아이 재우고 늦게 불렀는데도 조용히 와주셔서 고마웠어요. 어깨 뭉친 게 많이 풀렸습니다."},
    {"author": "J", "loc": "신월동", "rating": 5, "date": "2025-04-27",
     "text": "교대 근무라 시간이 매번 다른데도 그때그때 맞춰 주셔서 꾸준히 이용 중입니다."},
    {"author": "P", "loc": "신월동", "rating": 4, "date": "2025-05-09",
     "text": "홈타이 처음 받아봤는데 샤워 걱정 없이 받을 수 있어서 편했어요. 스트레칭이 시원했습니다."},
    {"author": "H", "loc": "신정동", "rating": 5, "date": "2025-05-21",
     "text": "부모님 댁으로 보내드렸는데 설명을 차분하게 해주셔서 어머니가 편하게 받으셨다고 하네요."},
    {"author": "Y", "loc": "신정동", "rating": 5, "date": "2025-06-03",
     "text": "운동하고 허벅지가 뭉쳤을 때 받았는데 부위를 잘 짚어서 풀어주셨습니다. 다음엔 90분으로 해보려고요."},
]

# 역세권 후기 (오피스텔·숙박시설 등 역 기준 위치)
STATION_REVIEWS = [
    {"author": "S", "loc": "오목교역", "rating": 5, "date": "2025-04-18",
     "text": "오목교역 근처 오피스텔인데 예약한 시각에 정확히 도착하셨어요. 끝나고 정리도 깔끔했습니다."},
    {"author": "C", "loc": "신목동역", "rating": 5, "date": "2025-05-02",
     "text": "출장으로 묵은 숙소였는데 프런트 통과 절차까지 미리 물어봐 주셔서 수월했습니다."},
    {"author": "M", "loc": "양천구청역", "rating": 4, "date": "2025-05-16",
     "text": "야근 끝나고 늦은 시간이었는데도 받을 수 있었고, 90분 코스라 다리까지 충분히 풀었어요."},
    {"author": "B", "loc": "목동역", "rating": 5, "date": "2025-06-07",
     "text": "목동역 근처 사무실로 두 명 같이 불렀는데 의자 구성으로 짧게 받기 좋았습니다."},
]

ALL_REVIEWS = AREA_REVIEWS + STATION_REVIEWS


def aggregate() -> dict:
    """평균 평점과 후기 수를 계산한다."""
    n = len(ALL_REVIEWS)
    total = sum(r["rating"] for r in ALL_REVIEWS)
    return {
        "count": n,
        "value": round(total / n, 1),
        "best": 5,
        "worst": 1,
    }


def stars(rating: int) -> str:
    """채워진 별과 빈 별로 평점을 표시하는 HTML 조각."""
    full = "★" * rating
    empty = "☆" * (5 - rating)
    return (
        f'<span class="review-stars" aria-label="별점 {rating}점 만점에 5점">'
        f'<span class="stars-on">{full}</span>'
        f'<span class="stars-off">{empty}</span></span>'
    )


def review_list_html(reviews) -> str:
    """후기 목록을 별점과 함께 카드형 리스트로 렌더링한다."""
    items = []
    for r in reviews:
        items.append(
            '<li class="review-item">'
            f'{stars(r["rating"])}'
            f'<p class="review-text">"{r["text"]}"</p>'
            f'<p class="review-meta">{r["loc"]} {r["author"]}님 · {r["date"]}</p>'
            "</li>"
        )
    return '<ul class="review-list">\n' + "\n".join(items) + "\n</ul>"


def rating_summary_html() -> str:
    """페이지 상단에 노출할 평균 평점 요약 UI."""
    agg = aggregate()
    return (
        '<div class="rating-summary">'
        f'<span class="rating-score">{agg["value"]}</span>'
        f'<span class="rating-detail">{stars(round(agg["value"]))}'
        f'<span class="rating-count">실제 이용 후기 {agg["count"]}건 기준 (5점 만점)</span></span>'
        "</div>"
    )
