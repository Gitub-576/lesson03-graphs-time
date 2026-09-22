import streamlit as st
import pandas as pd
import plotly.express as px


# ==================================================
# 기본 설정
# ==================================================
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.write("영화의 일별 관객 데이터를 시간의 흐름에 따라 살펴봅니다.")


# ==================================================
# 데이터 불러오기
# ==================================================
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


# 데이터가 없는 경우
if df.empty:
    st.error("데이터를 불러오지 못했습니다.")
    st.stop()


# ==================================================
# 그래프 1
# 영화별 일관객 변화
# ==================================================
st.header("1. 영화별 일관객 변화")

st.write(
    "영화를 선택하면 날짜에 따른 일관객 변화를 확인할 수 있습니다."
)

# 영화 목록 만들기
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

# 선택한 영화 데이터
movie_df = df[
    df["영화코드"] == selected_movie_code
].copy()

movie_df = movie_df.sort_values("날짜")


# 선 그래프
fig1 = px.line(
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

fig1.update_traces(
    hovertemplate=
    "날짜: %{x|%Y-%m-%d}<br>"
    "일관객: %{y:,}명"
)

fig1.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# 그래프 1 해석
st.subheader("📝 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프에서 발견한 내용을 적어보세요.",
    placeholder="예: 날짜에 따라 일관객 수가 어떻게 변화하는지 확인할 수 있다.",
    height=100,
    key="graph1_note"
)


# ==================================================
# 그래프 2
# 일관객 합계 상위 5편의 변화
# ==================================================
st.divider()

st.header("2. 일관객 합계 상위 5편의 변화")

st.write(
    "전체 기간 동안 일관객 합계가 가장 큰 5편의 날짜별 관객 변화를 비교합니다."
)


# 전체 기간 일관객 합계 계산
top5_movies = (
    df.groupby(
        ["영화코드", "영화명"],
        as_index=False
    )["일관객"]
    .sum()
    .sort_values(
        "일관객",
        ascending=False
    )
    .head(5)
)

top5_codes = top5_movies["영화코드"].tolist()

# 상위 5편 데이터
top5_df = df[
    df["영화코드"].isin(top5_codes)
].copy()

top5_df = top5_df.sort_values("날짜")


# 5개 영화를 한 그래프에 표시
fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계가 가장 큰 5편의 날짜별 일관객",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
        "영화명": "영화"
    }
)

fig2.update_traces(
    hovertemplate=
    "영화: %{fullData.name}<br>"
    "날짜: %{x|%Y-%m-%d}<br>"
    "일관객: %{y:,}명"
)

fig2.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)",
    legend_title="영화"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# 상위 5편 표
st.subheader("🏆 일관객 합계 상위 5편")

ranking_df = top5_movies.copy()

ranking_df["순위"] = range(1, 6)

ranking_df = ranking_df[
    ["순위", "영화명", "일관객"]
]

ranking_df = ranking_df.rename(
    columns={
        "영화명": "영화",
        "일관객": "기간 일관객 합계"
    }
)

st.dataframe(
    ranking_df,
    hide_index=True,
    use_container_width=True
)


# 그래프 2 해석
st.subheader("📝 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프에서 발견한 내용을 적어보세요.",
    placeholder="예: 기간 동안 관객을 많이 모은 영화들의 일별 관객 수 변화를 서로 비교할 수 있다.",
    height=100,
    key="graph2_note"
)


# ==================================================
# 그래프 3
# 날짜별 10위권 일관객 합계
# ==================================================
st.divider()

st.header("3. 날짜별 10위권 일관객 합계")

st.write(
    "각 날짜의 10위권 영화가 모은 일관객을 모두 합산하여 전체적인 영화 관람 규모의 변화를 보여 줍니다."
)


# 날짜별 일관객 합계
daily_audience = (
    df.groupby(
        "날짜",
        as_index=False
    )["일관객"]
    .sum()
    .sort_values("날짜")
)

daily_audience = daily_audience.rename(
    columns={
        "일관객": "10위권 일관객 합계"
    }
)


# 일관객 합계가 가장 큰 3일
top3_days = (
    daily_audience
    .nlargest(
        3,
        "10위권 일관객 합계"
    )
    .sort_values(
        "10위권 일관객 합계",
        ascending=False
    )
)


# 영역 그래프
fig3 = px.area(
    daily_audience,
    x="날짜",
    y="10위권 일관객 합계",
    title="날짜별 10위권 일관객 합계",
    labels={
        "날짜": "날짜",
        "10위권 일관객 합계": "10위권 일관객 합계"
    }
)

fig3.update_traces(
    hovertemplate=
    "날짜: %{x|%Y-%m-%d}<br>"
    "10위권 일관객 합계: %{y:,}명"
)


# 상위 3일 그래프 위에 표시
for _, row in top3_days.iterrows():

    date_text = row["날짜"].strftime("%Y-%m-%d")
    audience = row["10위권 일관객 합계"]

    fig3.add_annotation(
        x=row["날짜"],
        y=audience,
        text=f"{date_text}<br>{audience:,}명",
        showarrow=True,
        arrowhead=2,
        yshift=10
    )


fig3.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="10위권 일관객 합계(명)"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# 상위 3일 표
st.subheader("🏆 10위권 일관객 합계가 가장 컸던 3일")

top3_display = top3_days.copy()

top3_display["순위"] = range(1, 4)

top3_display["날짜"] = (
    top3_display["날짜"]
    .dt.strftime("%Y-%m-%d")
)

top3_display = top3_display[
    [
        "순위",
        "날짜",
        "10위권 일관객 합계"
    ]
]

st.dataframe(
    top3_display,
    hide_index=True,
    use_container_width=True
)


# 그래프 3 해석
st.subheader("📝 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프에서 발견한 내용을 적어보세요.",
    placeholder="예: 날짜별 전체 관객 규모가 어떻게 변했는지 알 수 있으며, 관객이 가장 많았던 날을 확인할 수 있다.",
    height=100,
    key="graph3_note"
)


# ==================================================
# 그래프 4
# 영화별 기간 일관객 TOP 10
# ==================================================
st.divider()

st.header("4. 영화별 기간 일관객 TOP 10")

st.write(
    "전체 기간 동안 영화별 일관객을 합산하여 관객이 가장 많았던 10편을 비교합니다."
)


# 영화별 일관객 합계 + 10위권 등장일수
movie_summary = (
    df.groupby(
        ["영화코드", "영화명"],
        as_index=False
    )
    .agg(
        기간_일관객_합계=("일관객", "sum"),
        **{
            "10위권_등장일수": ("날짜", "nunique")
        }
    )
)


# 일관객 합계 기준 TOP 10
top10_movies = (
    movie_summary
    .sort_values(
        "기간_일관객_합계",
        ascending=False
    )
    .head(10)
    .copy()
)


# 가로 막대 그래프에서 관객이 많은 영화가 위쪽에 오도록
top10_chart = top10_movies.sort_values(
    "기간_일관객_합계",
    ascending=True
)


fig4 = px.bar(
    top10_chart,
    x="기간_일관객_합계",
    y="영화명",
    orientation="h",
    title="영화별 기간 일관객 TOP 10",
    labels={
        "기간_일관객_합계": "기간 일관객 합계",
        "영화명": "영화"
    },
    custom_data=["10위권_등장일수"]
)


# 마우스 오버 정보
fig4.update_traces(
    hovertemplate=
    "영화: %{y}<br>"
    "기간 일관객 합계: %{x:,}명<br>"
    "10위권 등장일수: %{customdata[0]}일"
)

fig4.update_layout(
    xaxis_title="기간 일관객 합계(명)",
    yaxis_title="영화",
    hovermode="closest"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)


# TOP 10 표
st.subheader("🏆 기간 일관객 TOP 10")

top10_table = top10_movies.copy()

top10_table["순위"] = range(1, 11)

top10_table = top10_table[
    [
        "순위",
        "영화명",
        "기간_일관객_합계",
        "10위권_등장일수"
    ]
]

top10_table = top10_table.rename(
    columns={
        "영화명": "영화",
        "기간_일관객_합계": "기간 일관객 합계",
        "10위권_등장일수": "10위권 등장일수"
    }
)

st.dataframe(
    top10_table,
    hide_index=True,
    use_container_width=True
)


# 그래프 4 해석
st.subheader("📝 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프에서 발견한 내용을 적어보세요.",
    placeholder="예: 전체 기간 동안 일관객을 가장 많이 기록한 영화와 각 영화가 10위권에 머문 날수를 비교할 수 있다.",
    height=100,
    key="graph4_note"
)


# ==================================================
# 그래프 5
# 월 × 요일별 일관객 히트맵
# ==================================================
st.divider()

st.header("5. 월 × 요일별 일관객 히트맵")

st.write(
    "월과 요일에 따라 전체 기간 동안 일관객이 어떻게 분포했는지 확인합니다."
)


# 데이터 복사
heatmap_df = df.copy()


# 월 추출
heatmap_df["월"] = heatmap_df["날짜"].dt.month


# 요일 추출
weekday_map = {
    0: "월요일",
    1: "화요일",
    2: "수요일",
    3: "목요일",
    4: "금요일",
    5: "토요일",
    6: "일요일"
}

heatmap_df["요일"] = (
    heatmap_df["날짜"]
    .dt.weekday
    .map(weekday_map)
)


# 요일 순서
weekday_order = [
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일"
]


# 월 × 요일별 일관객 합계
monthly_weekday = (
    heatmap_df
    .groupby(
        ["월", "요일"],
        as_index=False
    )["일관객"]
    .sum()
)


# 요일 순서를 월요일 → 일요일로 고정
monthly_weekday["요일"] = pd.Categorical(
    monthly_weekday["요일"],
    categories=weekday_order,
    ordered=True
)

monthly_weekday = monthly_weekday.sort_values(
    ["월", "요일"]
)


# 히트맵
fig5 = px.density_heatmap(
    monthly_weekday,
    x="요일",
    y="월",
    z="일관객",
    category_orders={
        "요일": weekday_order,
        "월": list(range(1, 13))
    },
    color_continuous_scale="Blues",
    title="월 × 요일별 일관객 합계",
    labels={
        "요일": "요일",
        "월": "월",
        "일관객": "일관객 합계"
    },
    text_auto=".2s"
)


fig5.update_traces(
    hovertemplate=
    "%{y}월 %{x}<br>"
    "일관객 합계: %{z:,}명"
)

fig5.update_layout(
    xaxis_title="요일",
    yaxis_title="월",
    coloraxis_colorbar_title="일관객"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)


# 그래프 5 해석
st.subheader("📝 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프에서 발견한 내용을 적어보세요.",
    placeholder="예: 어떤 월과 요일에 10위권 영화들의 일관객 합계가 높은지 확인할 수 있다.",
    height=100,
    key="graph5_note"
)


# ==================================================
# 추가 그래프 영역
# ==================================================
st.divider()

st.header("6. 추가 그래프")

st.info(
    "앞으로 새로운 그래프를 이 구역에 추가할 수 있습니다."
)

st.subheader("그래프 6")

st.write(
    "여기에 새로운 그래프를 추가할 예정입니다."
)

st.subheader("📝 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프 6의 해석을 적어보세요.",
    placeholder="이 그래프에서 알 수 있는 내용을 적어보세요.",
    height=100,
    key="graph6_note"
)


# ==================================================
# 데이터 정보
# ==================================================
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
