import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

def get_top_10_companies():
    """
    글로벌 시가총액 Top 10 기업 (대략적인 기준)의 티커 심볼을 반환합니다.
    YFinance에서 직접 시가총액 순위를 가져오는 API는 없으므로,
    대략적으로 알려진 Top 기업들을 수동으로 지정합니다.
    실제 시가총액 순위는 변동될 수 있습니다.
    """
    return {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "NVIDIA": "NVDA", # 최근 상승세 반영
        "Amazon": "AMZN",
        "Alphabet (Google)": "GOOGL", # GOOG도 함께 (클래스 A)
        "Meta Platforms": "META",
        "Tesla": "TSLA",
        "Berkshire Hathaway": "BRK-B",
        "Eli Lilly": "LLY", # 최근 상승세 반영
        "TSMC": "TSM",
    }

def get_stock_data(ticker, start_date, end_date):
    """
    YFinance를 사용하여 특정 티커의 주가 데이터를 가져옵니다.
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        return data
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

def plot_stock_data(data, company_name, ticker):
    """
    Plotly를 사용하여 주가 데이터를 그립니다.
    """
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                        open=data['Open'],
                                        high=data['High'],
                                        low=data['Low'],
                                        close=data['Close'],
                                        name='Candlestick')])
    fig.update_layout(
        title=f'{company_name} ({ticker}) 주가 변동 (최근 3년)',
        xaxis_title='날짜',
        yaxis_title='주가',
        xaxis_rangeslider_visible=False, # 하단 범위 슬라이더 숨기기
        template="plotly_white", # 깔끔한 배경
        hovermode="x unified" # 호버 시 정보 통합 표시
    )
    return fig

# Streamlit 앱 시작
st.set_page_config(layout="wide", page_title="글로벌 시총 TOP 10 주가 분석 📈")

st.title("🌐 글로벌 시총 Top 10 기업 주가 변동 분석 📈")
st.markdown("최근 3년간 주요 글로벌 기업들의 주가 변동을 확인해 보세요.")

st.sidebar.header("설정")
st.sidebar.markdown("📈 차트를 보고 싶은 기업을 선택하세요.")

companies = get_top_10_companies()
company_names = list(companies.keys())

# 다중 선택을 가능하게 합니다.
selected_companies = st.sidebar.multiselect(
    "기업을 선택하세요:",
    company_names,
    default=company_names[:3] # 기본적으로 상위 3개 선택
)

# 날짜 범위 설정 (최근 3년)
end_date = datetime.now()
start_date = end_date - timedelta(days=3 * 365) # 3년 전

if not selected_companies:
    st.warning("분석할 기업을 하나 이상 선택해주세요. ☝️")
else:
    for company_name in selected_companies:
        ticker = companies[company_name]
        st.subheader(f"📊 {company_name} ({ticker}) 주가 차트")

        with st.spinner(f"🚀 {company_name} 주가 데이터를 불러오는 중..."):
            stock_data = get_stock_data(ticker, start_date, end_date)

        if stock_data is not None and not stock_data.empty:
            st.plotly_chart(plot_stock_data(stock_data, company_name, ticker), use_container_width=True)
            st.markdown("---") # 기업별 구분선
        elif stock_data is not None and stock_data.empty:
            st.warning(f"⚠️ {company_name} ({ticker})에 대한 지난 3년간의 주가 데이터를 찾을 수 없습니다. 다시 시도해 주세요.")
        # 데이터가 None인 경우는 get_stock_data에서 이미 에러 메시지 출력됨

st.sidebar.markdown("---")
st.sidebar.info("데이터는 Yahoo Finance에서 제공됩니다.")
st.sidebar.markdown(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
