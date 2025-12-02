import streamlit as st
from backend import recommend_knn, emotions
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import uuid

# ──────────────────────────────
# 사용자 ID 생성
# ──────────────────────────────
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())


# ──────────────────────────────
# Google Sheets 연결
# ──────────────────────────────
def connect_to_gsheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key("10uxFwwOHTrZ5Hw1aUw_5M4JlKY-YZz8sRQ_X3NGTGeA").sheet1
    return sheet


# ──────────────────────────────
# Google Sheets 저장 함수
# ──────────────────────────────
def save_to_sheet(recs, emo1, emo2, pop_level, rating=None, mood_after=None):
    sheet = connect_to_gsheet()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = st.session_state.user_id

    for r in recs:
        sheet.append_row([
            timestamp,
            user_id,
            emo1,
            emo2 if emo2 else "",
            pop_level,
            r["title"],
            r["artist"],
            r["similarity"],
            rating if rating else "",
            mood_after if mood_after else ""
        ])


# ──────────────────────────────
# Streamlit UI — Premium 스타일 적용
# ──────────────────────────────
st.set_page_config(page_title="감정 기반 음악 추천", page_icon="🎵")

st.markdown("""
    <style>
        /* Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Pretendard', sans-serif;
        }

        /* Title Gradient */
        .title-text {
            font-size: 36px;
            font-weight: 700;
            background: linear-gradient(90deg, #7F7FD5, #86A8E7, #91EAE4);
            -webkit-background-clip: text;
            color: transparent;
            text-shadow: 0px 2px 12px rgba(0,0,0,0.15);
            padding-bottom: 5px;
        }

        .cute-box {
            padding: 20px 22px;
            border-radius: 18px;
            background-color: #FFFFFF;
            box-shadow: 0px 4px 16px rgba(0,0,0,0.08);
            margin-bottom: 15px;
        }

        .colored-box {
            background: linear-gradient(135deg, #D9F1FF, #EAF7FF);
            box-shadow: 0px 3px 14px rgba(140,180,255,0.25);
        }
    </style>
""", unsafe_allow_html=True)

# ──────────────────────────────
# UI 상단 안내 박스
# ──────────────────────────────
st.markdown(
    """
<div class="cute-box">
    <div class="title-text">🎵 감정 기반 음악 추천 시스템</div>
    지금 감정에 따라 딱 맞는 음악을 추천받아보세요! <br>
    선택한 감정과 인기도(pop_level)를 기반으로 음악을 추천해주는 시스템입니다 🎧  
</div>
""",
    unsafe_allow_html=True
)

st.markdown(
    """
<div class="cute-box colored-box">
    <div class="title-text">✨ 선택 가능한 감정</div>
    happy · sad · relaxed · angry · focus · confident
</div>

<div class="cute-box colored-box">
    <div class="title-text">🔥 인기도 (pop_level)</div>
    0 : 60–70 <br>
    1 : 71–80 <br>
    2 : 81–99
</div>

<div class="cute-box">
    지금 내 분위기에 딱 맞는 음악을 찾아보자! 🌈    
</div>
""",
    unsafe_allow_html=True
)


# ──────────────────────────────
# 사용자 입력
# ──────────────────────────────
emo1 = st.selectbox("첫 번째 감정 선택", [""] + emotions)
emo2 = st.selectbox("두 번째 감정 선택(없어도 됨)", [""] + emotions)
pop_level = st.selectbox("인기도 레벨(pop_level)", [0, 1, 2])

# ──────────────────────────────
# 추천 버튼
# ──────────────────────────────
if st.button("추천 받기"):
    if emo1 == "":
        st.warning("⚠ 첫 번째 감정을 선택해주세요.")
    else:
        user_emotions = [emo1]
        if emo2 != "":
            user_emotions.append(emo2)

        st.session_state.recs = recommend_knn(user_emotions, pop_level)
        st.session_state.emo1 = emo1
        st.session_state.emo2 = emo2
        st.session_state.pop_level = pop_level

        st.success("추천이 생성되었어요! 🎶")


# ──────────────────────────────
# 추천 결과 출력 + 저장
# ──────────────────────────────
if "recs" in st.session_state:
    st.subheader("🎶 추천 결과")

    for r in st.session_state.recs:
        st.write(f"- **{r['title']}** — *{r['artist']}*  (유사도 {r['similarity']})")

    # 자동 로그 저장
    save_to_sheet(
        st.session_state.recs,
        st.session_state.emo1,
        st.session_state.emo2,
        st.session_state.pop_level
    )

    # ──────────────────────────────
    # 피드백 입력 UI
    # ──────────────────────────────
    st.subheader("📝 추천 피드백")

    rating = st.slider("추천 만족도 (1~5)", 1, 5, 3)
    mood_after = st.radio(
        "추천 후 기분 변화는?",
        ["더 좋아졌어요 🙂", "그대로예요 😐", "별로였어요 🙁"]
    )

    if st.button("피드백 제출"):
        save_to_sheet(
            st.session_state.recs,
            st.session_state.emo1,
            st.session_state.emo2,
            st.session_state.pop_level,
            rating,
            mood_after
        )
        st.success("💜 피드백이 저장되었습니다!")
