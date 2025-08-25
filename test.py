import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import date
import time

st.set_page_config(page_title="세계 숲 지도", layout="wide")
st.title("🌍 숲 세계 지도")

# ====== 나라별 데이터 (15개국) ======
countries = {
    "한국": {"coords":[36.5,127.8],"tree":["🌱","🌿","🌲","🌳"],"tree_info":"소나무는 한국의 대표 나무입니다.","animal":"🦌 고라니","animal_info":"한국 산림의 대표 동물"},
    "일본": {"coords":[36.2,138.3],"tree":["🌱","🌿","🌸","🌳"],"tree_info":"벚나무는 일본을 대표하는 나무입니다.","animal":"🦢 학","animal_info":"평화의 상징 새"},
    "중국": {"coords":[35.9,104.2],"tree":["🌱","🌿","🎋","🌳"],"tree_info":"대나무는 중국 전역에서 자랍니다.","animal":"🐼 판다","animal_info":"대나무 숲 상징 동물"},
    "인도": {"coords":[20.6,78.9],"tree":["🌱","🌿","🌴","🌳"],"tree_info":"망고나무는 인도의 대표 과일나무입니다.","animal":"🐘 코끼리","animal_info":"숲을 개척하는 동물"},
    "태국": {"coords":[15.8,101.0],"tree":["🌱","🌿","🍌","🌴"],"tree_info":"바나나 나무는 열대 아시아에서 중요한 자원입니다.","animal":"🐒 원숭이","animal_info":"열대우림 서식"},
    "인도네시아": {"coords":[-0.8,113.9],"tree":["🌱","🌿","🌴","🌳"],"tree_info":"야자나무는 열대 기후에서 중요한 자원입니다.","animal":"🐅 수마트라호랑이","animal_info":"열대우림 최상위 포식자"},
    "러시아": {"coords":[61.5,105.3],"tree":["🌱","🌿","🌲","🌳"],"tree_info":"자작나무는 러시아 전역에 분포합니다.","animal":"🐻 불곰","animal_info":"북방 숲 대표 포식자"},
    "핀란드": {"coords":[61.9,25.7],"tree":["🌱","🌿","🌲","🌳"],"tree_info":"자작나무는 북유럽 숲 대표 수종입니다.","animal":"🦌 순록","animal_info":"북유럽 자연 상징"},
    "독일": {"coords":[51.1,10.4],"tree":["🌱","🌿","🌳","🌳"],"tree_info":"참나무는 독일 숲의 상징입니다.","animal":"🐗 멧돼지","animal_info":"유럽 숲 대표 동물"},
    "프랑스": {"coords":[46.2,2.2],"tree":["🌱","🌿","🍇","🌳"],"tree_info":"포도나무는 프랑스 문화의 상징입니다.","animal":"🦊 여우","animal_info":"프랑스 농촌 동물"},
    "브라질": {"coords":[-14.2,-51.9],"tree":["🌱","🌿","🌴","🌳"],"tree_info":"아마존 고무나무는 지구의 허파 역할을 합니다.","animal":"🐆 재규어","animal_info":"아마존 최상위 포식자"},
    "케냐": {"coords":[0.0,37.9],"tree":["🌱","🌿","🌳","🌳"],"tree_info":"바오밥나무는 물 저장 능력이 뛰어납니다.","animal":"🦒 기린","animal_info":"사바나 상징 동물"},
    "캐나다": {"coords":[56.1,-106.3],"tree":["🌱","🌿","🌲","🌳"],"tree_info":"단풍나무는 캐나다 상징입니다.","animal":"🦫 비버","animal_info":"하천 생태계 유지"},
    "호주": {"coords":[-25.3,133.8],"tree":["🌱","🌿","🌳","🌳"],"tree_info":"유칼립투스는 호주 대표 나무입니다.","animal":"🦘 캥거루","animal_info":"호주 상징 동물"},
    "미국": {"coords":[37.1,-95.7],"tree":["🌱","🌿","🌲","🌳"],"tree_info":"세쿼이아는 세계에서 가장 큰 나무 중 하나입니다.","animal":"🦅 흰머리독수리","animal_info":"미국 상징 새"}
}

# ====== 세션 상태 초기화 ======
if "growth" not in st.session_state:
    st.session_state.growth = {country: 0 for country in countries}
if "last_watered" not in st.session_state:
    st.session_state.last_watered = {country: None for country in countries}
if "score" not in st.session_state:
    st.session_state.score = 0
if "my_forest" not in st.session_state:
    st.session_state.my_forest = []

# ====== 탭 구성 ======
tab1, tab2 = st.tabs(["🌍 세계 지도", "🌳 나만의 숲"])

# ---------------- 세계 지도 ----------------
with tab1:
    st.metric("지구 건강 점수", f"{st.session_state.score} 점")
    st.progress(min(st.session_state.score/100, 1.0))
    
    m = folium.Map(location=[20,0], zoom_start=2)
    for country, data in countries.items():
        folium.Marker(location=data["coords"], popup=country, tooltip="나무 보기").add_to(m)
    st_map = st_folium(m, width=700, height=500)
    
    if st_map["last_object_clicked_popup"]:
        selected_country = st_map["last_object_clicked_popup"]
        if selected_country in countries:
            info = countries[selected_country]
            growth_stage = st.session_state.growth[selected_country]
            tree_emoji = info["tree"][growth_stage]
            
            st.subheader(f"{selected_country}의 나무: {tree_emoji}")
            today = date.today()
            
            if st.session_state.last_watered[selected_country] != today:
                if st.button("💧 물주기"):
                    if growth_stage < len(info["tree"]) - 1:
                        placeholder = st.empty()
                        for stage in range(growth_stage, growth_stage+2):
                            if stage < len(info["tree"]):
                                placeholder.subheader(f"나무 성장 중... {info['tree'][stage]}")
                                time.sleep(0.5)
                        st.session_state.growth[selected_country] += 1
                        growth_stage += 1
                        
                        if growth_stage == len(info["tree"]) - 1:
                            st.session_state.score += 10
                            st.session_state.my_forest.append(f"{selected_country} {info['tree'][-1]} {info['animal']}")
                    
                    st.session_state.last_watered[selected_country] = today
                    st.experimental_rerun()
            else:
                st.info("오늘은 이미 물을 줬습니다. 내일 다시 와주세요 🌞")
            
            st.success(info["tree_info"])
            if growth_stage == len(info["tree"]) - 1:
                st.subheader(f"대표 동물: {info['animal']}")
                st.info(info["animal_info"])
                st.markdown("🌍👣 **환경을 지키는 발자국에 한걸음 움직이는 중**")

# ---------------- 나만의 숲 ----------------
with tab2:
    st.write("여기에는 당신이 키운 나무들이 모여 숲을 이룹니다 🌱🌿🌳")
    if st.session_state.my_forest:
        st.success("당신의 숲:")
        for tree in st.session_state.my_forest:
            st.markdown(f"- {tree}")
    else:
        st.info("아직 숲에 나무가 없습니다. 세계 지도에서 물을 주고 숲을 키워보세요!")
