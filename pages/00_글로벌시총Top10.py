import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime, timedelta

st.set_page_config(page_title="글로벌 시총 Top10 주가변동", layout="wide")
st.title("🌐 글로벌 시가총액 Top10 기업 주가 변동 (최근 3년)")

# 1. 시총 기준 Top10 기업 리스트
companies = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Saudi Aramco": "2222.SR",
    "Alphabet (Google)": "GOOGL",
    "Amazon": "AMZN",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",
    "Meta (Facebook)": "META",
    "Berkshire Hathaway": "BRK-B",
    "TSMC": "TSM"
}

# 2. 데이터 수집
end_date = datetime.today()
start_date = end_date - timedelta(days=3 * 365)

st.markdown("데이터를 가져오고 있습니다. 잠시만 기다려 주세요...")

data = {}
for name, ticker in companies.items():
    try:
        df = yf.download(ticker, start=start_date, end=end_date)
        df["Name"] = name
        data[name] = df
    except Exception as e:
        st.warning(f"{name} 데이터 오류: {e}")

# 3. Plotly 그래프
fig = go.Figure()

for name, df in data.items():
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        mode="lines",
        name=name
    ))

fig.update_layout(
    title="📈 최근 3년간 글로벌 시가총액 Top10 기업의 주가",
    xaxis_title="날짜",
    yaxis_title="종가 (USD)",
    legend_title="기업명",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)
