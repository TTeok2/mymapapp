import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="시총 Top 10 미국 기업 주가 현황",
    page_icon="📈",
    layout="wide"
)

# 미국 시총 Top 10 기업 (2024년 기준)
TOP_10_COMPANIES = {
    "Apple": "AAPL",
    "Microsoft": "MSFT", 
    "Alphabet": "GOOGL",
    "Amazon": "AMZN",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",
    "Meta": "META",
    "Berkshire Hathaway": "BRK-B",
    "Visa": "V",
    "UnitedHealth Group": "UNH"
}

@st.cache_data
def get_stock_data(ticker, period="3y"):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        return data
    except Exception as e:
        st.error(f"{ticker} 데이터를 가져오는 중 오류 발생: {e}")
        return None

@st.cache_data
def get_company_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'name': info.get('longName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'marketCap': info.get('marketCap', 0),
            'currentPrice': info.get('currentPrice', 0)
        }
    except:
        return {'name': 'N/A', 'sector': 'N/A', 'marketCap': 0, 'currentPrice': 0}

def format_market_cap(market_cap):
    if market_cap >= 1e12:
        return f"${market_cap/1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"${market_cap/1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"${market_cap/1e6:.2f}M"
    else:
        return f"${market_cap:,.0f}"

def main():
    st.title("🇺🇸 시총 Top 10 미국 기업 주가 현황")
    st.markdown("최근 3~5년간 미국 대형주 주가 데이터를 시각화해보세요.")

    # 사이드바
    st.sidebar.header("기업 선택")
    selected_companies = st.sidebar.multiselect(
        "분석할 기업을 선택하세요:",
        options=list(TOP_10_COMPANIES.keys()),
        default=list(TOP_10_COMPANIES.keys())[:3]
    )
    if not selected_companies:
        st.warning("최소 하나의 기업을 선택해주세요.")
        return

    period_options = {
        "1년": "1y", "2년": "2y", "3년": "3y", "5년": "5y"
    }
    selected_period = st.sidebar.selectbox("기간 선택:", options=list(period_options.keys()), index=2)
    chart_type = st.sidebar.radio("차트 타입:", ["라인 차트", "캔들스틱 차트"])

    # 데이터 불러오기
    with st.spinner("데이터를 불러오는 중..."):
        stock_data = {}
        company_info = {}
        for company in selected_companies:
            ticker = TOP_10_COMPANIES[company]
            data = get_stock_data(ticker, period_options[selected_period])
            info = get_company_info(ticker)
            if data is not None and not data.empty:
                stock_data[company] = data
                company_info[company] = info

    if not stock_data:
        st.error("선택한 기업의 데이터를 불러올 수 없습니다.")
        return

    # 기업 정보
    st.header("📊 선택된 기업 정보")
    cols = st.columns(len(selected_companies))
    for i, company in enumerate(selected_companies):
        if company in company_info:
            info = company_info[company]
            with cols[i]:
                st.metric(
                    label=f"{company}",
                    value=f"${info['currentPrice']:.2f}",
                    delta=f"시총: {format_market_cap(info['marketCap'])}"
                )
                st.caption(f"섹터: {info['sector']}")

    # 차트 출력
    st.header("📈 주가 차트")
    if chart_type == "라인 차트":
        fig = go.Figure()
        colors = px.colors.qualitative.Set1[:len(selected_companies)]
        for i, (company, data) in enumerate(stock_data.items()):
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name=company,
                line=dict(color=colors[i], width=2),
                hovertemplate=f'<b>{company}</b><br>Date: %{x}<br>Price: $%{{y:.2f}}<extra></extra>'
            ))
        fig.update_layout(
            title=f"주가 추이 - {selected_period}",
            xaxis_title="날짜", yaxis_title="주가 (USD)",
            hovermode='x unified', height=600, template='plotly_white'
        )
    else:
        company = selected_companies[0]
        data = stock_data[company]
        fig = go.Figure(data=go.Candlestick(
            x=data.index,
            open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'],
            name=company
        ))
        fig.update_layout(
            title=f"{company} 캔들스틱 차트 - {selected_period}",
            xaxis_title="날짜", yaxis_title="주가 (USD)",
            height=600, template='plotly_white'
        )
    st.plotly_chart(fig, use_container_width=True)

    # 성과 비교
    st.header("📊 성과 비교")
    performance_data = []
    for company, data in stock_data.items():
        start_price = data['Close'].iloc[0]
        end_price = data['Close'].iloc[-1]
        total_return = ((end_price - start_price) / start_price) * 100
        performance_data.append({
            '기업': company,
            '시작 가격': f"${start_price:.2f}",
            '현재 가격': f"${end_price:.2f}",
            '총 수익률': f"{total_return:.2f}%",
            '최고가': f"${data['Close'].max():.2f}",
            '최저가': f"${data['Close'].min():.2f}",
            '변동성': f"{data['Close'].std():.2f}"
        })
    st.dataframe(pd.DataFrame(performance_data), use_container_width=True)

    # 거래량 분석
    st.header("📊 거래량 분석")
    fig_volume = go.Figure()
    for i, (company, data) in enumerate(stock_data.items()):
        fig_volume.add_trace(go.Scatter(
            x=data.index,
            y=data['Volume'],
            mode='lines',
            name=company,
            line=dict(color=colors[i % len(colors)], width=2),
            hovertemplate=f'<b>{company}</b><br>Date: %{x}<br>Volume: %{y:,.0f}<extra></extra>'
        ))
    fig_volume.update_layout(
        title=f"거래량 추이 - {selected_period}",
        xaxis_title="날짜", yaxis_title="거래량",
        hovermode='x unified', height=400, template='plotly_white'
    )
    st.plotly_chart(fig_volume, use_container_width=True)

    # 미국 증시 폭락 사례
    st.header("📉 최근 미국 주식시장 급락 사례")
    st.markdown("""
    다음은 최근 5년간 미국 주식시장의 대표적인 급락 사례입니다:
    
    | 시기 | 원인 |
    |------|------|
    | **2020.03** | 코로나 팬데믹 → 공급망 붕괴, 소비 위축 |
    | **2022 상반기** | 연준의 급격한 금리 인상 → 기술주 중심 하락 |
    | **2023.03** | 실리콘밸리은행(SVB) 파산 → 금융시스템 불안정 |

    🔎 이와 같은 사건은 시장 전반의 **변동성 증가** 및 투자 심리 위축으로 이어질 수 있습니다.
    """)

    # 주의사항
    st.header("ℹ️ 참고 및 주의사항")
    st.info("""
    **데이터 출처**: Yahoo Finance
    
    **주의**: 본 데이터는 정보 제공용이며, 투자 조언이 아닙니다. 실제 투자 결정은 전문가와 상담하세요.
    """)

if __name__ == "__main__":
    main()
