import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.write("영화의 일별 관객 데이터를 시간의 흐름에 따라 살펴봅니다.")

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜를 진짜 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d"
    )

    # 숫자형 데이터 변환
    numeric_columns = [
        "순위",
        "영화코드",
        "일관객",
        "누적관객",
        "스크린수",
        "상영횟수"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


df = load_data()

# --------------------------------------------------
# 데이터 확인
# --------------------------------------------------
if df.empty:
    st.error("데이터를 불러오지 못했습니다.")
    st.stop()

# --------------------------------------------------
# 그래프 1. 영화별 일관객 변화
# --------------------------------------------------
st.header("1. 영화별 일관객 변화")
st.write("영화를 선택하면 날짜에 따른 일관객 변화를 확인할 수 있습니다.")

# 영화명과 영화코드를 이용해 영화 목록 생성
movie_list = (
    df[["영화코드", "영화명"]]
    .drop_duplicates()
    .sort_values("영화명")
)

movie_options = {
    f"{row['영화명']}": row["영화코드"]
    for _, row in movie_list.iterrows()
}

selected_movie_name = st.selectbox(
    "영화를 선택하세요",
    list(movie_options.keys())
)

selected_movie_code = movie_options[selected_movie_name]

# 선택한 영화의 데이터만 추출
movie_df = df[
    df["영화코드"] == selected_movie_code
].copy()

movie_df = movie_df.sort_values("날짜")

# --------------------------------------------------
# 선 그래프
# --------------------------------------------------
fig = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"{selected_movie_name} - 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수"
    }
)

# 마우스를 올렸을 때 날짜와 관객수가 표시되도록 설정
fig.update_traces(
    hovertemplate=
    "날짜: %{x|%Y-%m-%d}<br>"
    "일관객: %{y:,}명"
)

fig.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# 그래프로 알 수 있는 것
# --------------------------------------------------
st.subheader("📝 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프에서 발견한 내용을 적어보세요.",
    placeholder="예: 주말에 관객 수가 증가하고 평일에는 감소하는 경향을 확인할 수 있다.",
    height=100,
    key="graph1_note"
)

# --------------------------------------------------
# 앞으로 추가할 그래프 영역
# --------------------------------------------------
st.divider()

st.header("2. 추가 그래프")
st.info(
    "앞으로 새로운 그래프를 이 구역에 추가할 수 있습니다."
)

# 예시용 빈 공간
st.subheader("그래프 2")
st.write("여기에 새로운 그래프를 추가할 예정입니다.")

st.subheader("📝 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프 2의 해석을 적어보세요.",
    placeholder="이 그래프에서 알 수 있는 내용을 적어보세요.",
    height=100,
    key="graph2_note"
)

# --------------------------------------------------
# 데이터 정보
# --------------------------------------------------
st.divider()

st.header("📊 데이터 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "전체 기록 수",
        f"{len(df):,}개"
    )

with col2:
    st.metric(
        "영화 수",
        f"{df['영화코드'].nunique():,}편"
    )

with col3:
    st.metric(
        "기록 날짜 수",
        f"{df['날짜'].nunique():,}일"
    )

st.caption(
    "데이터 출처: KOBIS 일별 박스오피스 데이터"
)
