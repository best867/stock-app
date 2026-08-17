import streamlit as st
import yfinance as yf
import plotly.graph_objects as go


# ---------------------------------------------------------
# 페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="주식 비교 대시보드",
    page_icon="📈",
    layout="wide"
)


# ---------------------------------------------------------
# 따뜻한 크림·노란색 톤의 화면 스타일
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        .stApp {
            background-color: #FFF8E7;
        }

        h1, h2, h3 {
            color: #5C4326;
        }

        .description {
            color: #806A4A;
            font-size: 1.05rem;
            line-height: 1.7;
            margin-bottom: 1rem;
        }

        .metric-card {
            background-color: #FFFDF5;
            border: 1px solid #E8C96A;
            border-radius: 16px;
            padding: 18px;
            box-shadow: 0 4px 12px rgba(120, 90, 40, 0.08);
            min-height: 115px;
        }

        .metric-title {
            color: #806A4A;
            font-size: 0.95rem;
            margin-bottom: 8px;
        }

        .metric-value {
            color: #5C4326;
            font-size: 1.55rem;
            font-weight: 700;
        }

        div.stButton > button {
            background-color: #FFF1C2;
            color: #5C4326;
            border: 1px solid #E8C96A;
            border-radius: 10px;
            font-weight: 600;
        }

        div.stButton > button:hover {
            background-color: #F5D77A;
            color: #4B351C;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# 제목과 설명
# ---------------------------------------------------------
st.title("📈 주식 비교 대시보드")

st.markdown(
    """
    <div class="description">
        최대 2개의 종목을 입력해서 주가 흐름을 비교해 보세요.
        <br>
        예: <b>005930.KS</b> (삼성전자), <b>AAPL</b> (애플)
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# 종목 입력창 2개
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    ticker1 = st.text_input(
        "🔎 첫 번째 종목",
        value="005930.KS",
        placeholder="예: 005930.KS"
    ).strip().upper()

with col2:
    ticker2 = st.text_input(
        "🔎 두 번째 종목 (선택)",
        value="AAPL",
        placeholder="예: AAPL"
    ).strip().upper()


# ---------------------------------------------------------
# 기간 선택 버튼
# ---------------------------------------------------------
st.markdown("### 🗓️ 조회 기간")

period_options = {
    "1개월": "1mo",
    "6개월": "6mo",
    "1년": "1y",
    "5년": "5y"
}

# 세션 상태에 선택된 기간을 저장합니다.
if "selected_period" not in st.session_state:
    st.session_state.selected_period = "1년"

period_cols = st.columns(4)

for index, period_name in enumerate(period_options.keys()):
    with period_cols[index]:
        if st.button(
            period_name,
            use_container_width=True,
            key=f"period_{period_name}"
        ):
            st.session_state.selected_period = period_name

selected_period_name = st.session_state.selected_period
selected_period = period_options[selected_period_name]

st.caption(f"현재 선택된 기간: **{selected_period_name}**")


# ---------------------------------------------------------
# 주가 데이터 가져오기
# ---------------------------------------------------------
def get_stock_data(ticker, period):
    """yfinance에서 선택한 기간의 주가 데이터를 가져옵니다."""
    if not ticker:
        return None

    stock = yf.Ticker(ticker)

    # auto_adjust=False로 원래 종가 데이터를 사용합니다.
    data = stock.history(
        period=period,
        auto_adjust=False
    )

    if data.empty:
        return None

    return stock, data


# ---------------------------------------------------------
# 숫자를 보기 좋은 가격 문자열로 변환
# ---------------------------------------------------------
def format_price(price, currency):
    """통화에 따라 가격을 보기 쉽게 표시합니다."""
    if currency == "KRW":
        return f"{price:,.0f}원"

    return f"{price:,.2f}"


# ---------------------------------------------------------
# 종목 하나의 지표 카드 표시
# ---------------------------------------------------------
def show_stock_metrics(ticker, stock, data):
    """현재가, 등락률, 최고가, 최저가, 평균가를 표시합니다."""

    # 최근 종가
    current_price = float(data["Close"].iloc[-1])

    # 기간 시작 가격
    start_price = float(data["Close"].iloc[0])

    # 선택한 기간 동안의 등락률
    change_rate = ((current_price - start_price) / start_price) * 100

    # 기간 내 최고가 / 최저가 / 평균가
    highest_price = float(data["High"].max())
    lowest_price = float(data["Low"].min())
    average_price = float(data["Close"].mean())

    # 통화 정보 가져오기
    try:
        currency = stock.fast_info.get("currency", "")
    except Exception:
        currency = ""

    current_text = format_price(current_price, currency)
    highest_text = format_price(highest_price, currency)
    lowest_text = format_price(lowest_price, currency)
    average_text = format_price(average_price, currency)

    # 등락률 표시
    if change_rate > 0:
        change_text = f"▲ {change_rate:.2f}%"
    elif change_rate < 0:
        change_text = f"▼ {abs(change_rate):.2f}%"
    else:
        change_text = "0.00%"

    st.markdown(f"### 📌 {ticker}")

    # 첫 번째 줄: 현재가 / 등락률
    metric1, metric2 = st.columns(2)

    with metric1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">현재가</div>
                <div class="metric-value">{current_text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with metric2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">{selected_period_name} 등락률</div>
                <div class="metric-value">{change_text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 두 번째 줄: 최고가 / 최저가 / 평균가
    metric3, metric4, metric5 = st.columns(3)

    with metric3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">최고가</div>
                <div class="metric-value">{highest_text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with metric4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">최저가</div>
                <div class="metric-value">{lowest_text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with metric5:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">평균가</div>
                <div class="metric-value">{average_text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ---------------------------------------------------------
# 입력된 종목 데이터 조회
# ---------------------------------------------------------
stock1 = None
stock2 = None

if ticker1:
    try:
        stock1 = get_stock_data(ticker1, selected_period)
    except Exception:
        stock1 = None

if ticker2:
    try:
        stock2 = get_stock_data(ticker2, selected_period)
    except Exception:
        stock2 = None


# ---------------------------------------------------------
# 데이터를 가져오지 못했을 때 안내
# ---------------------------------------------------------
if ticker1 and stock1 is None:
    st.error(
        f"첫 번째 종목 **{ticker1}**의 데이터를 찾을 수 없습니다. "
        "종목 코드를 확인해주세요."
    )

if ticker2 and stock2 is None:
    st.error(
        f"두 번째 종목 **{ticker2}**의 데이터를 찾을 수 없습니다. "
        "종목 코드를 확인해주세요."
    )


# ---------------------------------------------------------
# 종목별 지표 표시
# ---------------------------------------------------------
if stock1 or stock2:
    st.markdown("---")
    st.subheader("💰 주요 지표")

    if stock1 and stock2:
        col1, col2 = st.columns(2)

        with col1:
            show_stock_metrics(ticker1, stock1[0], stock1[1])

        with col2:
            show_stock_metrics(ticker2, stock2[0], stock2[1])

    elif stock1:
        show_stock_metrics(ticker1, stock1[0], stock1[1])

    elif stock2:
        show_stock_metrics(ticker2, stock2[0], stock2[1])


# ---------------------------------------------------------
# 비교 그래프
# ---------------------------------------------------------
if stock1 or stock2:
    st.markdown("---")
    st.subheader(f"📊 최근 {selected_period_name} 주가 흐름")

    fig = go.Figure()

    # 첫 번째 종목 그래프
    if stock1:
        data1 = stock1[1]

        fig.add_trace(
            go.Scatter(
                x=data1.index,
                y=data1["Close"],
                mode="lines",
                name=ticker1,
                line=dict(width=3),
                hovertemplate=(
                    f"{ticker1}<br>"
                    "날짜: %{x|%Y-%m-%d}<br>"
                    "종가: %{y:,.2f}"
                    "<extra></extra>"
                )
            )
        )

    # 두 번째 종목 그래프
    if stock2:
        data2 = stock2[1]

        fig.add_trace(
            go.Scatter(
                x=data2.index,
                y=data2["Close"],
                mode="lines",
                name=ticker2,
                line=dict(width=3),
                hovertemplate=(
                    f"{ticker2}<br>"
                    "날짜: %{x|%Y-%m-%d}<br>"
                    "종가: %{y:,.2f}"
                    "<extra></extra>"
                )
            )
        )

    # 그래프 모양을 따뜻한 톤으로 설정합니다.
    fig.update_layout(
        height=520,
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="#FFFDF5",
        paper_bgcolor="#FFFDF5",
        hovermode="x unified",
        xaxis=dict(
            title="날짜",
            showgrid=False
        ),
        yaxis=dict(
            title="주가",
            gridcolor="#F0E4C5"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        "※ 주가는 yfinance에서 제공하는 데이터이며 실시간 시세와 "
        "차이가 있을 수 있습니다."
    )
else:
    st.info("위에 종목 코드를 하나 이상 입력해주세요. 😊")
