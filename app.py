import sqlite3
import sys

from flask import Flask, render_template_string, session, redirect, url_for, request

app = Flask(__name__)
app.secret_key = "fake-news-game-secret-key-dev"

DATABASE = "news.db"

SAMPLE_ARTICLES = [
    ("서울시, 2024년 대중교통 무료 환승 시간 30분에서 40분으로 확대",
     "서울시는 시민 편의를 위해 대중교통 무료 환승 허용 시간을 기존 30분에서 40분으로 확대한다고 발표했다. 이번 정책은 장거리 통근자들의 교통비 부담을 줄이기 위한 조치로, 내년 1월부터 시행될 예정이다.",
     "real", "서울시 교통정책 공식 발표를 확인해보세요.", "서울시는 실제로 환승 시간 확대 정책을 발표한 바 있습니다."),
    ("WHO, 커피 하루 3잔 이상 섭취 시 수명 연장 효과 확인",
     "세계보건기구(WHO)는 대규모 역학 연구를 통해 하루 3잔 이상의 커피 섭취가 심혈관 질환 위험을 낮추고 평균 수명을 2년 연장시킨다는 연구 결과를 발표했다.",
     "fake", "WHO가 특정 식품의 수명 연장 효과를 공식 발표한 적이 있는지 생각해보세요.", "WHO는 커피의 수명 연장 효과를 공식 확인한 적이 없습니다. 과장된 주장입니다."),
    ("삼성전자, 반도체 미세공정 기술 3나노 양산 본격화",
     "삼성전자가 세계 최초로 3나노미터 GAA 공정 기반 반도체 양산을 본격화했다. 기존 5나노 대비 성능 23% 향상, 전력 소모 45% 절감 효과가 있으며, 주요 고객사 납품이 시작됐다.",
     "real", "삼성전자의 반도체 기술 로드맵을 떠올려보세요.", "삼성전자는 실제로 3나노 GAA 공정 양산을 발표했습니다."),
    ("NASA, 화성에서 미생물 화석 발견 공식 발표",
     "미국 항공우주국(NASA)은 화성 탐사 로버 퍼서비어런스가 수집한 암석 샘플에서 고대 미생물 화석을 발견했다고 공식 발표했다.",
     "fake", "이 정도 발견이라면 전 세계 뉴스에서 대대적으로 보도됐을 것입니다.", "NASA는 화성에서 미생물 화석을 공식 발견한 적이 없습니다."),
    ("한국은행, 기준금리 0.25%p 인하 결정",
     "한국은행 금융통화위원회는 경기 둔화에 대응하기 위해 기준금리를 0.25%포인트 인하하기로 결정했다. 이번 인하로 기준금리는 연 3.25%가 되며, 가계 대출 금리 하락이 예상된다.",
     "real", "한국은행의 최근 통화정책 방향을 생각해보세요.", "한국은행은 실제로 경기 상황에 따라 기준금리를 조정합니다."),
    ("일본 정부, 2025년부터 주 4일 근무제 전면 의무화",
     "일본 정부는 저출산 문제 해결과 워라밸 개선을 위해 2025년부터 모든 기업에 주 4일 근무제를 의무화한다고 발표했다. 위반 기업에는 최대 1억 엔의 벌금이 부과된다.",
     "fake", "'전면 의무화'와 '1억 엔 벌금'이라는 표현의 현실성을 생각해보세요.", "일본은 주 4일제를 권장하고 있지만, 전면 의무화한 적은 없습니다."),
    ("국내 연구진, 폐배터리 재활용 기술로 리튬 회수율 95% 달성",
     "한국과학기술연구원(KIST) 연구팀이 폐배터리에서 리튬을 95% 이상 회수할 수 있는 친환경 재활용 기술을 개발했다. 기존 방식 대비 비용은 40% 절감된다.",
     "real", "국내 연구기관의 배터리 재활용 연구 동향을 생각해보세요.", "KIST는 실제로 폐배터리 재활용 기술 연구를 활발히 진행하고 있습니다."),
    ("애플, 아이폰 17에 홀로그램 디스플레이 탑재 확정",
     "애플이 차기 아이폰 17에 공중에 3D 홀로그램을 투사하는 디스플레이 기술을 탑재할 것이라고 공식 확인했다. 별도의 안경 없이 맨눈으로 입체 영상을 볼 수 있다.",
     "fake", "현재 홀로그램 기술 수준이 스마트폰에 탑재 가능한 단계인지 생각해보세요.", "공중 홀로그램 디스플레이는 아직 상용화되지 않은 기술입니다."),
    ("정부, 청년 월세 지원금 월 20만원에서 30만원으로 인상",
     "국토교통부는 청년 주거 안정을 위해 청년 월세 특별지원 사업의 지원 금액을 월 최대 20만원에서 30만원으로 인상한다고 발표했다.",
     "real", "정부의 청년 주거 지원 정책 방향을 생각해보세요.", "정부는 실제로 청년 월세 지원 사업을 운영하며 지원금을 확대해왔습니다."),
    ("중국, 인공 태양 실험 성공으로 무한 에너지 상용화 선언",
     "중국 과학원은 핵융합 실험 장치 EAST에서 1억도 플라즈마를 무한 시간 유지하는 데 성공했다며, 2026년부터 가정용 무한 에너지 공급을 시작한다고 선언했다.",
     "fake", "'무한 시간 유지'와 '2026년 상용화'라는 표현이 현실적인지 생각해보세요.", "핵융합 상용화는 아직 수십 년이 걸릴 것으로 예상됩니다. 과장된 주장입니다."),
    ("네이버, AI 검색 서비스 '큐(Cue:)' 정식 출시",
     "네이버가 생성형 AI 기반 검색 서비스 '큐(Cue:)'를 정식 출시했다. 기존 검색과 달리 대화형으로 질문에 답변하며, 출처를 함께 제공해 신뢰성을 높였다.",
     "real", "네이버의 최근 AI 서비스 출시 동향을 떠올려보세요.", "네이버는 실제로 AI 검색 서비스를 출시하며 AI 전환을 추진하고 있습니다."),
    ("유럽연합, 스마트폰 배터리 교체 의무화 법안 시행",
     "EU는 2025년부터 모든 스마트폰 제조사에 사용자가 직접 배터리를 교체할 수 있는 설계를 의무화하는 법안을 시행한다.",
     "real", "EU의 전자제품 관련 규제 동향을 생각해보세요.", "EU는 실제로 배터리 교체 가능 설계를 의무화하는 규정을 통과시켰습니다."),
    ("테슬라, 완전 자율주행 차량으로 서울~부산 무인 운행 성공",
     "테슬라가 FSD v13을 탑재한 모델3로 서울에서 부산까지 약 400km를 운전자 개입 없이 완주했다고 발표했다.",
     "fake", "한국에서 완전 자율주행이 법적으로 허용되는지 생각해보세요.", "한국에서는 완전 자율주행 공도 실험이 법적으로 허용되지 않습니다."),
    ("카카오, 택시 호출 기본요금 인상 반영 시작",
     "카카오모빌리티는 각 지역 택시 기본요금 인상에 맞춰 앱 내 예상 요금 산정 기준을 업데이트했다고 밝혔다. 서울 기준 기본요금은 4,800원에서 5,400원으로 올랐다.",
     "real", "최근 택시 요금 인상 뉴스를 본 적이 있는지 생각해보세요.", "택시 기본요금은 실제로 인상되었으며, 카카오택시 앱에 반영됩니다."),
    ("구글, 검색 결과에서 AI가 거짓으로 판단한 뉴스 자동 삭제 시작",
     "구글이 AI 알고리즘을 통해 허위 정보로 판단된 뉴스 기사를 검색 결과에서 자동 삭제하는 기능을 전 세계에 적용했다.",
     "fake", "구글이 뉴스를 '자동 삭제'하는 것이 언론 자유 측면에서 가능한지 생각해보세요.", "구글은 AI 판단만으로 뉴스를 자동 삭제하는 정책은 시행하지 않습니다."),
    ("현대차, 전기차 배터리 보증 기간 10년으로 확대",
     "현대자동차가 신규 출시되는 전기차 모델부터 배터리 보증 기간을 기존 8년에서 10년으로 확대한다고 발표했다.",
     "real", "전기차 제조사들의 배터리 보증 경쟁 동향을 생각해보세요.", "현대차는 실제로 전기차 배터리 보증을 확대하는 추세입니다."),
    ("일론 머스크, 뇌에 칩 이식한 원숭이와 텔레파시 통화 성공 주장",
     "일론 머스크는 뉴럴링크가 뇌에 칩을 이식한 원숭이 두 마리 간 생각만으로 의사소통하는 '텔레파시 통화'에 성공했다고 게시했다.",
     "fake", "'텔레파시 통화'라는 표현이 과학적으로 가능한 수준인지 생각해보세요.", "뉴럴링크는 뇌-컴퓨터 인터페이스를 연구하지만, 동물 간 텔레파시 통화는 달성된 적 없습니다."),
    ("기상청, 올여름 역대 최고 폭염 예보 발표",
     "기상청은 올해 여름 평균 기온이 평년보다 1.5도 이상 높을 것으로 예측하며, 역대 최고 수준의 폭염이 예상된다고 발표했다.",
     "real", "기상청이 계절 예보를 발표하는 것이 일반적인 업무인지 생각해보세요.", "기상청은 매년 계절 전망을 발표하며, 폭염 예보는 실제 업무 범위입니다."),
    ("삼성전자, 갤럭시 S25에 체온 측정 기능 탑재 확정",
     "삼성전자가 갤럭시 S25 시리즈에 손가락을 대면 체온을 측정할 수 있는 적외선 센서를 탑재한다고 공식 발표했다.",
     "fake", "스마트폰으로 의료용 수준의 체온 측정이 가능한지 생각해보세요.", "갤럭시 S25에 체온 측정 기능이 탑재된다는 공식 발표는 없었습니다."),
    ("국회, 주 52시간 근무제 예외 업종 확대 법안 통과",
     "국회 본회의에서 IT, 게임, 연구개발 등 특정 업종에 대해 주 52시간 근무제 예외를 허용하는 근로기준법 개정안이 통과됐다.",
     "real", "근로시간 유연화에 대한 최근 국회 논의를 생각해보세요.", "근로시간 유연화 법안은 실제로 국회에서 논의되고 있는 사안입니다."),
]


ERROR_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>오류</title></head>
<body>
<h1>오류</h1>
<p>{{ message }}</p>
<a href="/">처음으로</a>
</body>
</html>
"""

RESULT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>게임 종료</title></head>
<body>
<h1>게임 종료</h1>
<p style="font-size:2em;">{{ score }}/5</p>
<a href="/">다시 시작</a>
</body>
</html>
"""

GAME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>가짜 뉴스 판별 게임</title></head>
<body>
<h1>라운드 {{ round }}/5</h1>
<h2>{{ title }}</h2>
<p>{{ content }}</p>

{% if not answered %}
<details>
    <summary>💡 힌트 보기</summary>
    <p><em>{{ hint }}</em></p>
</details>
<br>
<form method="post" action="/answer">
    <button type="submit" name="answer" value="real">진짜</button>
    <button type="submit" name="answer" value="fake">가짜</button>
</form>
{% endif %}

{% if answered %}
{% if last_correct %}
<p><strong>✅ 정답!</strong></p>
{% else %}
<p><strong>❌ 오답!</strong> 정답은 {{ "진짜" if last_label == "real" else "가짜" }}였습니다.</p>
{% endif %}
<p style="color:gray;">📝 {{ explanation }}</p>
<form method="post" action="/next">
    <button type="submit">다음</button>
</form>
{% endif %}
</body>
</html>
"""


def init_db():
    """DB 파일이 없으면 테이블 생성 및 샘플 데이터 삽입"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                label TEXT NOT NULL CHECK(label IN ('real', 'fake')),
                hint TEXT NOT NULL DEFAULT '',
                explanation TEXT NOT NULL DEFAULT ''
            )
            """
        )
        conn.commit()
    except Exception as e:
        print(f"Error creating database: {e}")
        sys.exit(1)

    try:
        cursor.execute("SELECT COUNT(*) FROM articles")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.executemany(
                "INSERT INTO articles (title, content, label, hint, explanation) VALUES (?, ?, ?, ?, ?)",
                SAMPLE_ARTICLES,
            )
            conn.commit()
    except Exception as e:
        print(f"Error inserting sample data: {e}")
        conn.close()
        sys.exit(1)

    conn.close()


def get_random_articles(count: int = 5) -> list[int]:
    """DB에서 랜덤으로 count개의 기사 ID를 선택하여 반환"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM articles")
    total = cursor.fetchone()[0]
    if total < count:
        conn.close()
        raise ValueError(f"Not enough articles. Need {count}, have {total}.")
    cursor.execute("SELECT id FROM articles ORDER BY RANDOM() LIMIT ?", (count,))
    article_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return article_ids


def get_article(article_id: int) -> dict | None:
    """ID로 기사 조회"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content, label, hint, explanation FROM articles WHERE id = ?", (article_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


@app.route("/", methods=["GET"])
def index():
    """게임 시작/재시작"""
    session.clear()
    try:
        article_ids = get_random_articles(5)
    except ValueError:
        return render_template_string(ERROR_TEMPLATE, message="기사가 충분하지 않습니다. 최소 5개 필요합니다.")
    session["article_ids"] = article_ids
    session["current_round"] = 1
    session["score"] = 0
    session["answered"] = False
    session["last_correct"] = None
    session["last_label"] = None

    article = get_article(article_ids[0])
    return render_template_string(GAME_TEMPLATE, title=article["title"], content=article["content"],
                                  hint=article["hint"], explanation="", round=1, answered=False,
                                  last_correct=None, last_label=None)


@app.route("/answer", methods=["POST"])
def answer():
    """답 제출"""
    if "article_ids" not in session or "current_round" not in session:
        return redirect(url_for("index"))

    answer_value = request.form.get("answer", "")
    current_round = session["current_round"]
    article_id = session["article_ids"][current_round - 1]
    article = get_article(article_id)

    if article is None:
        return render_template_string(ERROR_TEMPLATE, message="기사를 찾을 수 없습니다.")

    if answer_value not in ("real", "fake"):
        return render_template_string(GAME_TEMPLATE, title=article["title"], content=article["content"],
                                      hint=article["hint"], explanation="", round=current_round,
                                      answered=False, last_correct=None, last_label=None)

    is_correct = answer_value == article["label"]
    session["answered"] = True
    session["last_correct"] = is_correct
    session["last_label"] = article["label"]
    if is_correct:
        session["score"] = session.get("score", 0) + 1

    return render_template_string(GAME_TEMPLATE, title=article["title"], content=article["content"],
                                  hint=article["hint"], explanation=article["explanation"],
                                  round=current_round, answered=True, last_correct=is_correct,
                                  last_label=article["label"])


@app.route("/result", methods=["GET"])
def result():
    """게임 종료 화면"""
    if "score" not in session:
        return redirect(url_for("index"))
    return render_template_string(RESULT_TEMPLATE, score=session["score"])


@app.route("/next", methods=["POST"])
def next_round():
    """다음 라운드"""
    if "article_ids" not in session or "current_round" not in session:
        return redirect(url_for("index"))

    if session["current_round"] >= 5:
        return redirect(url_for("result"))

    session["current_round"] += 1
    session["answered"] = False
    session["last_correct"] = None
    session["last_label"] = None

    article_id = session["article_ids"][session["current_round"] - 1]
    article = get_article(article_id)

    return render_template_string(GAME_TEMPLATE, title=article["title"], content=article["content"],
                                  hint=article["hint"], explanation="", round=session["current_round"],
                                  answered=False, last_correct=None, last_label=None)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
else:
    init_db()
