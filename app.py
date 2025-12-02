import streamlit as st
from backend import recommend_knn, emotions

st.set_page_config(page_title="감정 기반 음악 추천", page_icon="🎵")

st.title("🎵 감정 기반 음악 추천 시스템")

st.markdown("""
감정 목록: **happy, sad, relaxed, angry, focus, confident**  
pop_level: **0(60-70), 1(71-80), 2(81-99)**
""")

# 선택 입력
emo1 = st.selectbox("첫 번째 감정 선택", [""] + emotions)
emo2 = st.selectbox("두 번째 감정 선택(없어도 됨)", [""] + emotions)

pop_level = st.selectbox("인기도 레벨(pop_level)", [0, 1, 2])

if st.button("추천 받기"):
    if emo1 == "":
        st.warning("⚠ 첫 번째 감정을 반드시 선택해주세요.")
    else:
        user_emotions = [emo1]
        if emo2 != "":
            user_emotions.append(emo2)

        recs = recommend_knn(user_emotions, pop_level)

        st.subheader("🎶 추천 결과")
        for r in recs:
            st.write(f"- **{r['title']}** — *{r['artist']}*  (❗유사도 {r['similarity']})")
