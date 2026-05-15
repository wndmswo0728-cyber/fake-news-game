import sqlite3
import sys

from flask import Flask, render_template_string, session, redirect, url_for, request

app = Flask(__name__)
app.secret_key = "fake-news-game-secret-key-dev"

DATABASE = "news.db"

SAMPLE_ARTICLES = [
    ("정부, 2026년부터 모든 공공기관 주 4.5일제 시범 도입",
     "행정안전부는 공무원 워라밸 향상을 위해 2026년 하반기부터 중앙부처 및 산하기관을 대상으로 격주 금요일 단축근무(주 4.5일제)를 시범 운영한다고 밝혔다. 시범 기간은 6개월이며, 성과에 따라 확대 여부를 결정한다.",
     "fake", "\u2022 발표 주체: 행정안전부(공무원 인사 담당 부처)\n\u2022 정책 범위: 시범 도입으로 한정, 전면 시행 아님\n\u2022 구체적 일정(2026 하반기)과 기간(6개월) 명시", "행정안전부는 주 4.5일제 시범 도입을 공식 발표한 적이 없습니다."),
    ("SK하이닉스, HBM4 양산 시작… 엔비디아 차세대 GPU에 독점 공급",
     "SK하이닉스가 차세대 고대역폭 메모리 HBM4의 양산을 시작했다고 발표했다. 엔비디아의 차세대 AI 가속기 B300에 독점 공급되며, 기존 HBM3E 대비 처리 속도가 2배 향상됐다.",
     "real", "\u2022 HBM4는 업계에서 개발 중인 차세대 메모리 규격명\n\u2022 SK하이닉스-엔비디아 간 기존 공급 관계 존재\n\u2022 성능 향상 수치(2배)는 세대 간 일반적 개선폭", "SK하이닉스는 실제로 HBM4 양산과 엔비디아 공급 계약을 발표했습니다."),
    ("서울대 연구팀, 상온 초전도체 재현 실험 성공 논문 발표",
     "서울대학교 물리학과 연구팀이 국제학술지 네이처에 상온 상압 초전도체 LK-99의 초전도 현상을 재현했다는 논문을 게재했다. 연구팀은 시료의 전기저항이 0에 수렴하는 것을 확인했다고 밝혔다.",
     "fake", "\u2022 게재 학술지: Nature(피어리뷰 저널)\n\u2022 LK-99는 2023년 한국 연구팀이 발표한 물질명\n\u2022 전기저항 0 수렴은 초전도 판정의 핵심 측정값", "LK-99의 초전도 현상은 전 세계 재현 실험에서 확인되지 않았습니다."),
    ("카카오뱅크, 26세 이하 대상 신용대출 금리 연 2.9% 상품 출시",
     "카카오뱅크가 만 26세 이하 사회초년생을 대상으로 최저 연 2.9% 금리의 신용대출 상품을 출시했다. 한도는 최대 3,000만원이며, 재직 3개월 이상이면 신청 가능하다.",
     "real", "\u2022 카카오뱅크: 금융위 인가 인터넷전문은행\n\u2022 청년 대상 저금리 상품은 시중은행에서도 운영 중\n\u2022 대출 한도 3,000만원은 신용대출 일반 범위 내", "카카오뱅크는 실제로 청년 대상 저금리 신용대출 상품을 운영하고 있습니다."),
    ("국토부, 수도권 신규 택지 30만 가구 공급 계획 발표",
     "국토교통부는 수도권 주택 공급 확대를 위해 경기 남부 3개 지역에 총 30만 가구 규모의 신규 택지를 지정한다고 발표했다. 첫 입주는 2030년을 목표로 하며, 공공분양 비율은 40%다.",
     "fake", "\u2022 발표 주체: 국토교통부(주택 정책 담당)\n\u2022 30만 가구는 3기 신도시급 대규모 물량\n\u2022 2030년 입주 목표와 공공분양 40% 비율 명시", "이 규모의 신규 택지 지정 발표는 실제로 이루어지지 않았습니다."),
    ("LG에너지솔루션, 전고체 배터리 파일럿 라인 가동 시작",
     "LG에너지솔루션이 대전 연구소 내 전고체 배터리 파일럿 생산라인 가동을 시작했다고 밝혔다. 2028년 양산을 목표로 하며, 에너지 밀도는 기존 리튬이온 대비 40% 향상됐다.",
     "real", "\u2022 LG에너지솔루션: 글로벌 배터리 제조사\n\u2022 전고체 배터리: 차세대 기술로 업계 공통 개발 중\n\u2022 파일럿 라인은 양산 전 시험 생산 단계 의미", "LG에너지솔루션은 실제로 전고체 배터리 파일럿 라인 가동을 발표했습니다."),
    ("금융위, 가상자산 거래소 이용자 보호법 시행령 확정",
     "금융위원회는 가상자산 이용자 보호법 시행령을 확정 공포했다. 거래소는 고객 예치금의 80% 이상을 콜드월렛에 보관해야 하며, 이상거래 감지 시 24시간 내 거래 정지 조치를 의무화했다.",
     "real", "\u2022 금융위원회: 금융 규제 담당 정부 기관\n\u2022 가상자산 이용자 보호법: 2024년 시행된 법률\n\u2022 콜드월렛 보관 비율, 거래 정지 조치는 시행령 세부사항", "가상자산 이용자 보호법 시행령은 실제로 확정 시행되었습니다."),
    ("현대차, 아이오닉 9에 레벨4 자율주행 기본 탑재 공식 발표",
     "현대자동차가 2027년 출시 예정인 대형 전기 SUV 아이오닉 9에 레벨4 자율주행 기능을 기본 사양으로 탑재한다고 공식 발표했다. 고속도로에서 운전자 개입 없이 주행이 가능하다.",
     "fake", "\u2022 아이오닉 9: 현대차가 예고한 실제 차량명\n\u2022 레벨4: 특정 조건에서 완전 자율주행 단계\n\u2022 기본 사양 탑재는 옵션이 아닌 전 차량 적용 의미", "현대차는 아이오닉 9에 레벨4 자율주행 기본 탑재를 발표한 적이 없습니다."),
    ("질병관리청, 65세 이상 대상 RSV 백신 무료 접종 시작",
     "질병관리청은 호흡기세포융합바이러스(RSV) 감염 예방을 위해 65세 이상 고령자를 대상으로 RSV 백신 무료 접종을 시작한다고 밝혔다. 전국 위탁의료기관에서 접종 가능하다.",
     "real", "\u2022 질병관리청: 감염병 예방접종 담당 기관\n\u2022 RSV 백신: 2023년 FDA 승인된 실존 백신\n\u2022 고령자 무료 접종: 국가예방접종 사업 형태", "질병관리청은 실제로 고령자 대상 RSV 백신 접종 사업을 시행하고 있습니다."),
    ("네이버, 자체 AI 반도체 양산 돌입… TSMC 4나노 공정 위탁",
     "네이버가 자체 설계한 AI 추론 전용 반도체의 양산을 시작했다고 발표했다. TSMC 4나노 공정으로 제조되며, 자사 하이퍼클로바X 서비스에 우선 적용된다.",
     "fake", "\u2022 네이버: AI 서비스 기업(소프트웨어 중심)\n\u2022 TSMC 4나노: 실존하는 파운드리 공정\n\u2022 자체 반도체 개발은 빅테크 트렌드(구글 TPU, 아마존 Graviton)", "네이버는 자체 AI 반도체를 양산한다고 발표한 적이 없습니다."),
    ("한수원, 소형모듈원전(SMR) 건설 허가 원안위에 신청",
     "한국수력원자력이 원자력안전위원회에 소형모듈원전(SMR) 건설 허가를 공식 신청했다. 울진 부지에 100MW급 SMR 2기를 건설할 계획이며, 2032년 상업 운전을 목표로 한다.",
     "real", "\u2022 한수원: 국내 원전 운영 공기업\n\u2022 SMR: 전 세계적으로 개발 중인 차세대 원전 기술\n\u2022 원안위 건설 허가: 원전 건설의 법적 필수 절차", "한수원은 실제로 SMR 건설 허가를 신청하며 차세대 원전 사업을 추진하고 있습니다."),
    ("교육부, 2027학년도부터 수능 전 과목 절대평가 전환 확정",
     "교육부는 2027학년도 대학수학능력시험부터 전 과목 절대평가를 시행한다고 발표했다. 등급 체계는 현행 9등급에서 5등급으로 축소되며, 대학별 본고사는 허용하지 않는다.",
     "fake", "\u2022 교육부: 수능 제도 관할 부처\n\u2022 절대평가 전환: 수년간 논의된 정책 방향 중 하나\n\u2022 등급 축소(9->5)와 본고사 금지는 구체적 제도 변경 내용", "교육부는 2027학년도 수능 전면 절대평가 전환을 확정 발표한 적이 없습니다."),
    ("삼성바이오로직스, FDA로부터 바이오시밀러 3종 동시 승인",
     "삼성바이오로직스가 미국 FDA로부터 자가면역질환 치료제 바이오시밀러 3종에 대해 동시 판매 승인을 받았다고 공시했다. 2026년 상반기 미국 시장 출시를 목표로 한다.",
     "real", "\u2022 삼성바이오로직스: 글로벌 바이오 CMO/CDO 기업\n\u2022 FDA 바이오시밀러 승인: 공시 의무 사항\n\u2022 자가면역질환 바이오시밀러: 고성장 시장 분야", "삼성바이오로직스는 실제로 FDA 바이오시밀러 승인을 받아 미국 시장에 진출하고 있습니다."),
    ("과기정통부, 민간 우주발사체 발사 허가제 시행",
     "과학기술정보통신부는 민간 기업의 우주발사체 발사를 허가제로 관리하는 우주활동법 시행령을 공포했다. 국내 기업도 나로우주센터 외 민간 발사장에서 발사가 가능해진다.",
     "real", "\u2022 과기정통부: 우주 정책 담당 부처\n\u2022 우주활동법: 2024년 시행된 법률\n\u2022 민간 발사 허가제: 해외(미국 FAA) 선례 존재", "우주활동법 시행령은 실제로 공포되어 민간 우주발사 허가 체계가 마련되었습니다."),
    ("KT, 6G 상용 서비스 2026년 하반기 세계 최초 개시 선언",
     "KT가 2026년 하반기에 세계 최초로 6G 상용 서비스를 개시한다고 선언했다. 이론 속도 1Tbps를 목표로 하며, 서울 주요 지역부터 커버리지를 확대할 계획이다.",
     "fake", "\u2022 6G: 현재 3GPP 표준화 이전 연구 단계\n\u2022 1Tbps: 학술 논문에서 언급되는 6G 이론적 목표치\n\u2022 세계 최초 상용화 선언: 통신사 마케팅에서 사용되는 표현 유형", "6G는 아직 표준화 단계에 있으며, 2026년 상용화는 기술적으로 불가능합니다."),
    ("국민연금, 2025년 기금 운용 수익률 12.3% 달성",
     "국민연금공단은 2025년 기금 운용 수익률이 12.3%를 기록했다고 발표했다. 해외 주식 비중 확대 전략이 주효했으며, 기금 총액은 1,100조원을 돌파했다.",
     "real", "\u2022 국민연금: 세계 3위 규모 연기금\n\u2022 연간 수익률 12%대: 주식시장 호황기 달성 가능 범위\n\u2022 해외 주식 비중 확대: 공개된 자산배분 전략 방향", "국민연금은 실제로 2025년 높은 수익률을 기록하며 기금 규모가 확대되었습니다."),
    ("토스, 자체 신용평가 모델로 은행권 대출 심사 단독 대체 허가 획득",
     "토스가 금융위원회로부터 자체 개발 AI 신용평가 모델을 은행권 대출 심사에 단독 사용할 수 있는 허가를 받았다. 기존 NICE, KCB 평가 없이도 대출이 가능해진다.",
     "fake", "\u2022 토스: 핀테크 기업(종합금융플랫폼)\n\u2022 신용평가 시장: NICE, KCB 과점 구조\n\u2022 단독 사용 허가: 기존 규제 체계의 근본적 변경에 해당", "금융위는 특정 기업에 신용평가 단독 사용 허가를 부여한 적이 없습니다."),
    ("포스코, 호주 리튬 광산 지분 30% 인수 완료",
     "포스코홀딩스가 호주 서부 필바라 지역 리튬 광산의 지분 30%를 약 1조 2천억원에 인수했다고 공시했다. 연간 5만톤의 리튬 정광 확보가 가능해져 배터리 소재 수직계열화가 강화된다.",
     "real", "\u2022 포스코홀딩스: 2차전지 소재 사업 진출 기업\n\u2022 호주 필바라: 실제 리튬 광산 밀집 지역\n\u2022 지분 인수: 공시 의무 사항(금액/비율 명시)", "포스코는 실제로 호주 리튬 광산 지분을 인수하며 배터리 소재 사업을 확대하고 있습니다."),
    ("방통위, 유튜브에 국내 뉴스 콘텐츠 사용료 지급 의무화 고시 확정",
     "방송통신위원회는 유튜브 등 글로벌 플랫폼이 국내 언론사 뉴스 콘텐츠를 노출할 경우 사용료를 지급하도록 의무화하는 고시를 확정했다. 위반 시 매출의 3%까지 과징금이 부과된다.",
     "fake", "\u2022 방통위: 방송/통신 규제 기관\n\u2022 뉴스 사용료 의무화: 호주/캐나다에서 시행된 정책 유형\n\u2022 매출 3% 과징금: 디지털 플랫폼 규제에서 사용되는 제재 수준", "방통위는 유튜브에 뉴스 사용료 지급을 의무화하는 고시를 확정한 적이 없습니다."),
]
START_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Fake News Game</title>
<style>
body{font-family:-apple-system,sans-serif;background:#1a1a2e;color:#eee;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}
.card{background:#16213e;border-radius:16px;padding:60px 50px;max-width:500px;text-align:center;box-shadow:0 8px 32px rgba(0,0,0,.3)}
h1{font-size:2.5em;margin-bottom:10px}
.subtitle{color:#aaa;font-size:1.1em;margin-bottom:30px;line-height:1.6}
.btn{display:inline-block;padding:16px 48px;background:#4fc3f7;color:#1a1a2e;border:none;border-radius:30px;font-size:1.2em;font-weight:bold;cursor:pointer;transition:transform .2s;text-decoration:none}
.btn:hover{transform:scale(1.08)}
</style></head>
<body>
<div class="card">
<h1>📰 Fake News Game</h1>
<p class="subtitle">뉴스 기사를 읽고 진짜인지 가짜인지 맞춰보세요.<br>총 5라운드, 당신의 미디어 리터러시를 테스트합니다.</p>
<form method="post" action="/start">
<button type="submit" class="btn">🎮 게임 시작</button>
</form>
</div>
</body>
</html>
"""

ERROR_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>오류</title>
<style>
body{font-family:-apple-system,sans-serif;background:#1a1a2e;color:#eee;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}
.card{background:#16213e;border-radius:16px;padding:40px;max-width:500px;text-align:center;box-shadow:0 8px 32px rgba(0,0,0,.3)}
a{color:#4fc3f7;text-decoration:none;font-size:1.1em}
</style></head>
<body><div class="card"><h1>⚠️ 오류</h1><p>{{ message }}</p><a href="/">처음으로</a></div></body>
</html>
"""

RESULT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>게임 종료</title>
<style>
body{font-family:-apple-system,sans-serif;background:#1a1a2e;color:#eee;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}
.card{background:#16213e;border-radius:16px;padding:50px;max-width:500px;text-align:center;box-shadow:0 8px 32px rgba(0,0,0,.3)}
.score{font-size:4em;font-weight:bold;color:#ffd700;margin:20px 0}
.btn{display:inline-block;padding:14px 36px;background:#4fc3f7;color:#1a1a2e;border-radius:30px;text-decoration:none;font-size:1.1em;font-weight:bold;margin-top:20px;transition:transform .2s}
.btn:hover{transform:scale(1.05)}
</style></head>
<body>
<div class="card">
<h1>🏁 게임 종료</h1>
<div class="score">{{ score }} / 5</div>
<a href="/" class="btn">🔄 다시 시작</a>
</div>
</body>
</html>
"""

GAME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>가짜 뉴스 판별 게임</title>
<style>
body{font-family:-apple-system,sans-serif;background:#1a1a2e;color:#eee;display:flex;flex-direction:column;align-items:center;min-height:100vh;margin:0;padding:20px;box-sizing:border-box}
.status{display:flex;gap:30px;margin-bottom:20px;font-size:1.1em}
.status span{background:#16213e;padding:8px 20px;border-radius:20px}
.card{background:#16213e;border-radius:16px;padding:30px 36px;max-width:600px;width:100%;box-shadow:0 8px 32px rgba(0,0,0,.3)}
.card h2{color:#4fc3f7;margin-top:0;font-size:1.3em;line-height:1.4}
.card p{line-height:1.7;color:#ccc;font-size:1.05em}
.buttons{display:flex;gap:16px;margin-top:24px;justify-content:center}
.btn{padding:14px 36px;border:none;border-radius:30px;font-size:1.1em;font-weight:bold;cursor:pointer;transition:transform .2s}
.btn:hover{transform:scale(1.05)}
.btn-real{background:#4caf50;color:#fff}
.btn-fake{background:#f44336;color:#fff}
.btn-next{background:#4fc3f7;color:#1a1a2e}
.result-box{margin-top:20px;padding:16px 24px;border-radius:12px;font-size:1.1em;font-weight:bold;text-align:center}
.correct{background:rgba(76,175,80,.2);border:2px solid #4caf50;color:#4caf50}
.wrong{background:rgba(244,67,54,.2);border:2px solid #f44336;color:#f44336}
.explanation{margin-top:12px;padding:12px 16px;background:rgba(255,255,255,.05);border-radius:8px;color:#aaa;font-size:.95em}
details{margin-top:16px;cursor:pointer}
summary{color:#ffd700;font-size:1em}
details p{white-space:pre-line;color:#aaa;font-size:.9em;margin-top:8px}
</style></head>
<body>
<div class="status">
<span>📰 라운드 {{ round }} / 5</span>
<span>⭐ 점수 {{ score }}</span>
</div>
<div class="card">
<h2>{{ title }}</h2>
<p>{{ content }}</p>

{% if not answered %}
<details>
    <summary>💡 힌트 보기</summary>
    <p>{{ hint }}</p>
</details>
<form method="post" action="/answer" class="buttons">
    <button type="submit" name="answer" value="real" class="btn btn-real">✅ 진짜</button>
    <button type="submit" name="answer" value="fake" class="btn btn-fake">❌ 가짜</button>
</form>
{% endif %}

{% if answered %}
{% if last_correct %}
<div class="result-box correct">✅ Correct! 정답입니다</div>
{% else %}
<div class="result-box wrong">❌ Wrong! 정답은 {{ "진짜" if last_label == "real" else "가짜" }}였습니다</div>
{% endif %}
<div class="explanation">📝 {{ explanation }}</div>
<form method="post" action="/next" class="buttons">
    <button type="submit" class="btn btn-next">다음 →</button>
</form>
{% endif %}
</div>
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
    """시작 화면"""
    return render_template_string(START_TEMPLATE)


@app.route("/start", methods=["POST"])
def start():
    """게임 시작"""
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
                                  last_correct=None, last_label=None, score=0)


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
                                      answered=False, last_correct=None, last_label=None, score=session.get("score", 0))

    is_correct = answer_value == article["label"]
    session["answered"] = True
    session["last_correct"] = is_correct
    session["last_label"] = article["label"]
    if is_correct:
        session["score"] = session.get("score", 0) + 1

    return render_template_string(GAME_TEMPLATE, title=article["title"], content=article["content"],
                                  hint=article["hint"], explanation=article["explanation"],
                                  round=current_round, answered=True, last_correct=is_correct,
                                  last_label=article["label"], score=session.get("score", 0))


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
                                  answered=False, last_correct=None, last_label=None, score=session.get("score", 0))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
else:
    init_db()
