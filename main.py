import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="삿포로 관광 지도", layout="wide")

st.title("🗾 삿포로 관광 명소 추천 지도")
st.markdown("""
삿포로에서 한국인들에게 인기 있는 명소 3곳과, 주변의 꼭 먹어야 할 맛집을 소개합니다.  
각 마커를 눌러 정보를 확인하세요!
""")

# 중심 좌표: 삿포로 시청 근처
center = [43.0618, 141.3545]
m = folium.Map(location=center, zoom_start=13)

# 명소 및 맛집 리스트
locations = [
    {
        "name": "삿포로 맥주 박물관 🍺",
        "coords": [43.0731, 141.3616],
        "popup": "삿포로 맥주의 역사와 시음을 즐길 수 있는 박물관",
        "restaurant": {
            "name": "삿포로 맥주 가든 🍖",
            "coords": [43.0737, 141.3618],
            "popup": "징기스칸과 생맥주가 유명한 레스토랑"
        }
    },
    {
        "name": "오도리 공원 🌸",
        "coords": [43.0606, 141.3429],
        "popup": "사계절 축제와 산책을 즐길 수 있는 도심 공원",
        "restaurant": {
            "name": "스스키노 라멘 골목 🍜",
            "coords": [43.0546, 141.3534],
            "popup": "현지 라멘 맛집이 모인 거리"
        }
    },
    {
        "name": "홋카이도 구 본청사 🏛️",
        "coords": [43.0642, 141.3468],
        "popup": "붉은 벽돌로 지어진 역사적인 건물",
        "restaurant": {
            "name": "농학교 소프트 아이스크림 🍦",
            "coords": [43.0663, 141.3508],
            "popup": "홋카이도 우유로 만든 고소한 소프트 아이스크림"
        }
    },
]

# 지도에 마커 추가
for loc in locations:
    folium.Marker(loc["coords"], popup=loc["popup"], tooltip=loc["name"], icon=folium.Icon(color="blue")).add_to(m)
    folium.Marker(loc["restaurant"]["coords"], popup=loc["restaurant"]["popup"], tooltip=loc["restaurant"]["name"], icon=folium.Icon(color="green", icon="cutlery")).add_to(m)

# 지도 표시
st_data = st_folium(m, width=1000, height=600)
