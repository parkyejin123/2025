import streamlit as st

st.set_page_config(page_title="환경을 지키자!", page_icon="🌱")

# 나라별 대표 나무 데이터
nation_data = {
    "대한민국": "소나무",
    "일본": "벚나무",
    "미국": "참나무",
    "호주": "유칼립투스",
    "브라질": "아마존 고무나무",
    "중국": "대나무",
    "인도": "망고나무",
    "이집트": "종려나무",
}

# 세션 상태 초기화
if "trees" not in st.session_state:
    st.session_state.trees = {country: 0 for country in nation_data.keys()}

# 나무 성장 단계
def get_stage(level):
    stages = ["🌱 묘목", "🌿 어린나무", "🌳 큰 나무"]
    return stages[min(level, len(stages)-1)]

# 앱 제목
st.title("🌍 환경을 지키자! 세계 나무 성장 앱")

# 나라 선택
choice = st.selectbox("나라를 선택하세요:", list(nation_data.keys()))

# 물 주기 버튼
if st.button(f"💧 {choice}에 물 주기"):
    st.session_state.trees[choice] += 1

# 나무 상태 표시
level = st.session_state.trees[choice]
st.subheader(f"{choice}의 나무: {nation_data[choice]}")
st.write(f"성장 단계: {get_stage(level)}")

# 전체 나무 상태 표시
st.write("---")
st.subheader("🌳 모든 나라의 나무 상태")
for country, tree_level in st.session_state.trees.items():
    st.write(f"{country}: {get_stage(tree_level)}")
