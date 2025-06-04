import streamlit as st
import plotly.express as px
import pandas as pd
import re
from utils import load_and_preprocess
from konlpy.tag import Okt
import plotly.express as px
from io import BytesIO


st.set_page_config(page_title="네이버 웹툰 브랜드 인식 분석", layout="wide")


@st.cache_data
def get_data(file_bytes):
    return pd.read_excel(BytesIO(file_bytes))

uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx", "xls"])

if uploaded_file:
    content = uploaded_file.read()  # 바이너리 읽기
    df = get_data(content)          # 캐시에 저장 가능
    df = load_and_preprocess(df) # 데이터 전처리 함수 호출


st.title("네이버 웹툰 브랜드 인식 변화 설문 분석")
st.markdown("#### 문항을 선택하면 해당 위치로 이동합니다.")

question_titles = {
    1: "1. 연령대가 어떻게 되시나요?",
    2: "2. 성별을 알려주실 수 있나요?",
    3: "3. 현재 어떤 일을 하고 계신가요?",
    4: "4. 결혼 여부는 어떻게 되시나요?",
    5: "5. 현재 미성년 자녀가 있으신가요?",
    6: "6. '네이버' 하면 가장 먼저 떠오르는 이미지는 어떤 것들이 있나요? (최대 3개까지 선택)",
    7: "7. 전반적으로 네이버 서비스에 얼마나 만족하고 계신가요?",
    8: "8. 평소 자주 사용하는 네이버 서비스는 무엇인가요? (최대 3개까지 선택)",
    9: "9. 최근 1년 안에 웹툰을 본 적이 있으신가요?",
    10: "10. 사용 중인 웹툰 플랫폼이 있다면 모두 선택해주실 수 있나요?",
    11: "11. 네이버 웹툰을 사용하지 않으셨다면, 어떤 이유가 있으신가요?",
    111: "11-1. 추후에 네이버 웹툰을 이용해볼 생각이 있으신가요?",
    12: "12. 네이버 웹툰을 얼마나 오랫동안 사용해오셨나요?",
    13: "13. 네이버 웹툰 하면 떠오르는 이미지를 3개 이내로 골라주실 수 있을까요? (최대 3개까지 선택)",
    14: "14. 네이버 웹툰 서비스를 얼마나 자주 사용하고 계신가요?",
    15: "15. 네이버 웹툰에서 가장 선호하는 웹툰 장르는 어떤 것 인가요?",
    16: "16. 네이버 웹툰 콘텐츠 이용을 위해 유료 결제(예: 쿠키 충전, 유료 회차 구매 등)를 한 경험이 있으십니까?",
    17: "17. (결제 경험이 있으시다면) 지난 1년 동안 월평균 결제 금액은 어느 정도 되시나요?",
    18: "18. 웹툰을 보는 주된 이유는 무엇인가요? (3개 이내로 골라주세요)",
    19: "19. 성인 연령 확인 후 열람 가능한 콘텐츠가 있다는 것을 알고 계셨나요?",
    20: "20. 일반적으로 웹툰 플랫폼이 성인 연령 제한 작품을 제공하는 것에 대해 어떻게 생각하시나요?",
    21: "21. 네이버 웹툰에서 성인 연령 제한 작품을 이용해본 경험이 있으신가요?",
    22: "22. 성인 연령 제한 작품을 이용하신 주된 이유는 무엇인가요?",
    23: "23. 이용하지 않으셨다면, 주된 이유는 무엇인가요?",
    24: "24. 네이버 웹툰이 성인 연령 제한 작품을 포함하여 다양한 연령층을 고려한 콘텐츠를 제공하는 것에 대해 어떻게 생각하시나요?",
    25: "25. 네이버 웹툰이 성인 독자층까지 고려한 다양한 작품을 제공하는 것이 네이버 웹툰 브랜드 이미지에 부정적인 영향을 끼쳤다고 생각하시나요?",
    #251: "25-1. (주관식) 왜 그렇게 느끼셨는지 자유롭게 작성해주실 수 있을까요?", #자연어 배포 안되는 이슈로 주석 처리
    26: "26. 이러한 콘텐츠 구성(예: 다양한 연령층 대상 작품 제공 등)이 '네이버'라는 기업 전체의 브랜드 이미지에 부정적 영향을 준다고 생각하시나요?",
   #261: "26-1. (주관식) 가장 큰 영향을 주었다고 느끼신 측면이나 요인", #자연어 배포 안되는 이슈로 주석 처리
    27: "27. 타 웹툰 플랫폼과 비교했을 때, 네이버 웹툰의 성인 연령 제한 작품 수위는 어떤 편이라고 생각하시나요?",
    28: "28. 네이버 웹툰에서 성인 연령 확인 후 이용 가능한 작품들을 접하시면서 불편하거나 개선되었으면 하는 점이 있었나요?",
    29: "29. (주관식) 구체적으로 어떤 점이 불편했는지 알려주실 수 있나요?",
    30: "30. 현재 네이버 웹툰에서 다양한 연령대의 작품들을 구분하고, 성인 확인이 필요한 작품들에 대한 접근을 관리하는 기능에 대해 얼마나 만족하시나요?",
    31: "31. 네이버 웹툰에서 성인 독자를 위한 작품들을 더 쉽게 발견하거나 관련 추천이 늘어난다면 (성인 연령 제한 작품이 더 눈에 띄게 노출된다면), 해당 작품들을 이전보다 더 자주 보게 될 것 같으신가요?"

}

# 사이드바 그룹별 구성
sidebar_sections = [
    ("응답자 정보 조사", list(range(1, 6))),
    ("네이버에 대한 인식", list(range(6, 9))),
    ("웹툰 사용 경험", list(range(9, 12))+ [111]),
    ("웹툰 이용 스타일", list(range(12, 19))),
    ("19+콘텐츠 인식", list(range(19, 24))),
    # ("네이버 웹툰 앞으로", list(range(1, 25)) + [25, 251, 26, 261] + list(range(27, 32))), #자연어 배포 안되는 이슈로 주석 처리
    ("네이버 웹툰 앞으로", list(range(24, 32))),
]

with st.sidebar:
    st.markdown("## 문항 바로가기")
    sidebar_options = []
    sidebar_labels = []
    for section, qnums in sidebar_sections:
        st.markdown(f"**{section}**")
        for q in qnums:
            label = question_titles[q]
            sidebar_options.append(q)
            sidebar_labels.append(f"{label}")
            st.markdown(f"- [{label}](#{'q'+str(q)})")

# 스크롤 이동용 앵커 생성 함수
def anchor(num):
    st.markdown(f"<a name='q{num}'></a>", unsafe_allow_html=True)

# 자동 스크롤(앵커 jump) JS 삽입
query_params = st.query_params
if "q" in query_params:
    st.markdown(
        f"""
        <script>
        var q = "{query_params['q']}";
        if (window.location.hash !== "#q" + q) {{
            window.location.hash = "#q" + q;
        }}
        </script>
        """,
        unsafe_allow_html=True,
    )

# 모든 문항 결과를 한 페이지에 순서대로 출력

# for q_num in list(range(1, 12)) + [111] + list(range(12, 25)) + [25, 251, 26, 261] + list(range(27, 32)):  #자연어 배포 안되는 이슈로 주석 처리
for q_num in list(range(1, 12)) + [111] + list(range(12, 32)):    
    anchor(q_num)
    st.subheader(question_titles[q_num])
    # 아래에 기존 각 문항별 시각화 코드를 if q_num == ...: 대신 for문 안에 넣으세요.

    # 1. 연령대 분포
    if q_num == 1:
        age_order = ['10대', '20대', '30대', '40대', '50대 이상']
        age_df = df['age_group'].value_counts().reindex(age_order).reset_index()
        age_df.columns = ['age_group', 'count']
        fig = px.pie(age_df, names='age_group', values='count')
        st.plotly_chart(fig, use_container_width=True)

    # 2. 성별 분포
    elif q_num == 2:
        gender_df = df['gender'].value_counts().reset_index()
        gender_df.columns = ['gender', 'count']
        fig = px.pie(gender_df, names='gender', values='count')
        st.plotly_chart(fig, use_container_width=True)

    # 3. 직업 분포
    elif q_num == 3:
        occupation_df = df['occupation'].value_counts().reset_index()
        occupation_df.columns = ['occupation', 'count']
        fig = px.pie(occupation_df, names='occupation', values='count')
        st.plotly_chart(fig, use_container_width=True)

    # 4. 결혼 여부
    elif q_num == 4:
        marital_df = df['marital_status'].value_counts().reset_index()
        marital_df.columns = ['marital_status', 'count']
        fig = px.pie(marital_df, names='marital_status', values='count')
        st.plotly_chart(fig, use_container_width=True)

    # 5. 미성년 자녀 유무
    elif q_num == 5:
        child_df = df['has_minor_children'].value_counts().reset_index()
        child_df.columns = ['has_minor_children', 'count']
        child_df['has_minor_children'] = child_df['has_minor_children'].map({1: '예', 0: '아니오'})
        fig = px.pie(child_df, names='has_minor_children', values='count')
        st.plotly_chart(fig, use_container_width=True)

    # 6. 네이버 하면 떠오르는 이미지 (복수응답, 막대그래프)
    elif q_num == 6:
        category_list = [
            "편리함 – 검색부터 뉴스, 쇼핑까지 앱 하나로 가능함",
            "광고가 많음 – 검색 결과 상단에 자주 노출됨",
            "빠른뉴스 – 실시간 이슈 확인에 가장 먼저 떠오름",
            "콘텐츠풍부 – 웹툰, 블로그, 지식인 등 다양한 볼거리",
            "신뢰 어려움 – 상업성 정보가 많아 신뢰가 낮다고 느낌",
            "쇼핑 특화 – 제품 비교 및 결제에 자주 활용",
            "추천반복 – AI 추천이 비슷한 콘텐츠만 보여줌",
            "중장년친화 – 부모님도 쉽게 사용할 수 있는 구성",
            "정보 혼재 – 광고와 실제 정보의 구분이 어려움",
            "기능통합 – 지도·캘린더 등 일상 기능이 한 곳에 있음",
            "상업성 강함 – 광고/협찬 콘텐츠가 많아 보임",
            "국내최적화 – 한국 사용자에게 맞춤화된 정보 구성",
            "깔끔한디자인 – 앱 UI가 정돈되어 사용이 쾌적함",
            "콘텐츠중심 – 검색보다 콘텐츠 소비 용도로 주로 사용함",
            "검색 강자 – 여전히 빠르고 방대한 검색 기능"
        ]
        def split_multi(x):
            return [i.strip() for i in str(x).split('#') if i.strip()]
        image_responses = df['naver_image_association'].dropna().apply(split_multi)
        mapped = []
        for sublist in image_responses:
            for item in sublist:
                if item in category_list:
                    mapped.append(item)
        image_counts = pd.Series(mapped).value_counts().reindex(category_list, fill_value=0)
        respondent_count = df['naver_image_association'].dropna().shape[0]
        image_percents = (image_counts / respondent_count * 100).round(1)
        image_counts = image_counts[::-1]
        image_percents = image_percents[::-1]
        bar_text = [f"{v} ({p}%)" for v, p in zip(image_counts.values, image_percents)]
        fig = px.bar(
            x=image_counts.values,
            y=image_counts.index,
            orientation='h',
            text=bar_text,
            labels={'x': '응답 수', 'y': '이미지'}
        
        )
        fig.update_traces(textposition='outside', marker_color='mediumseagreen')
        st.plotly_chart(fig, use_container_width=True)

    # 7. 네이버 서비스 만족도 (막대그래프)
    elif q_num == 7:
        col = 'naver_service_satisfaction'
        sat_counts = df[col].value_counts().sort_index()
        sat_percents = (sat_counts / sat_counts.sum() * 100).round(1)
        bar_text = [f"{v} ({p}%)" for v, p in zip(sat_counts.values, sat_percents)]
        fig = px.bar(
            x=sat_counts.index.astype(str),
            y=sat_counts.values,
            text=bar_text,
            labels={'x': '만족도(점수)', 'y': '응답 수'}
        )
        fig.update_traces(textposition='outside', marker_color='royalblue')
        st.plotly_chart(fig, use_container_width=True)

    # 8. 평소 자주 사용하는 네이버 서비스 (복수응답, 막대그래프)
    elif q_num == 8:
        service_col = 'frequent_naver_services'
        def split_multi(x):
            return [i.strip() for i in str(x).split(',') if i.strip()]
        service_responses = df[service_col].dropna().apply(split_multi)
        mapped = [item for sublist in service_responses for item in sublist]
        service_counts = pd.Series(mapped).value_counts()
        respondent_count = df[service_col].dropna().shape[0]
        service_percents = (service_counts / respondent_count * 100).round(1)
        service_counts = service_counts[::-1]
        service_percents = service_percents[::-1]
        bar_text = [f"{v} ({p}%)" for v, p in zip(service_counts.values, service_percents)]
        fig = px.bar(
            x=service_counts.values,
            y=service_counts.index,
            orientation='h',
            text=bar_text,
            labels={'x': '응답 수', 'y': '서비스'}
        )
        fig.update_traces(textposition='outside', marker_color='darkcyan')
        st.plotly_chart(fig, use_container_width=True)

    # 9. 최근 1년 안에 웹툰을 본 적이 있으신가요? (파이차트)
    elif q_num == 9:
        col = 'webtoon_usage_last_year'
        usage_df = df[col].map({1: '예', 0: '아니오'}).value_counts().reset_index()
        usage_df.columns = ['webtoon_usage_last_year', 'count']
        fig = px.pie(
            usage_df,
            names='webtoon_usage_last_year',
            values='count'
        )
        st.plotly_chart(fig, use_container_width=True)

    # 10. 사용 중인 웹툰 플랫폼 (복수응답, 막대그래프)
    elif q_num == 10:
        platform_col = 'webtoon_platforms_used'
        full_platform_list = [
            '네이버 웹툰', '리디', '카카오페이지', '레진코믹스', '투믹스', '코미코(comico)', 'Bomtoon (봄툰)', '미스터블루', '탑툰', '없음', '사용하는 웹툰 플랫폼이 없음.'
        ]
        def split_multi(x):
            return [i.strip() for i in str(x).split(',') if i.strip()]
        platform_responses = df[platform_col].dropna().apply(split_multi)
        mapped = [item for sublist in platform_responses for item in sublist]
        platform_counts = pd.Series(mapped).value_counts().reindex(full_platform_list, fill_value=0)
        respondent_count = df[platform_col].dropna().shape[0]
        platform_percents = (platform_counts / respondent_count * 100).round(1)
        platform_counts = platform_counts[::-1]
        platform_percents = platform_percents[::-1]
        bar_text = [f"{v} ({p}%)" for v, p in zip(platform_counts.values, platform_percents)]
        fig = px.bar(
            x=platform_counts.values,
            y=platform_counts.index,
            orientation='h',
            text=bar_text,
            labels={'x': '응답 수', 'y': '플랫폼'}
        )
        fig.update_traces(textposition='outside', marker_color='indigo')
        st.plotly_chart(fig, use_container_width=True)

    # 11. 네이버 웹툰 미이용 사유 (복수응답, 막대그래프)
    elif q_num == 11:
        reason_cols = [
            "reason_not_using_naver_webtoon_다른 플랫폼을 더 선호해서",
            "reason_not_using_naver_webtoon_볼만한 작품이 없어서",
            "reason_not_using_naver_webtoon_유료 콘텐츠 비용이 부담돼서",
            "reason_not_using_naver_webtoon_서비스 이용이 불편해서",
            "reason_not_using_naver_webtoon_19+ 콘텐츠가 있는 것이 싫어서",
            "reason_not_using_naver_webtoon_네이버 웹툰에 대해 잘 몰라서",
            "reason_not_using_naver_webtoon_기타"
        ]
        reason_cols = [col for col in reason_cols if col in df.columns]
        if reason_cols:
            reason_sum = df[reason_cols].sum().sort_values(ascending=True)
            reason_labels = [col.replace("reason_not_using_naver_webtoon_", "") for col in reason_sum.index]
            total_respondents = (df[reason_cols].sum(axis=1) > 0).sum()
            reason_percents = (reason_sum / total_respondents * 100).round(1)
            bar_text = [f"{v} ({p}%)" for v, p in zip(reason_sum.values, reason_percents)]
            fig = px.bar(
                x=reason_sum.values,
                y=reason_labels,
                orientation='h',
                text=bar_text,
                labels={'x': '응답 수', 'y': '미이용 사유'}
            )
            fig.update_traces(textposition='outside', marker_color='tomato')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("미이용 사유 인코딩 컬럼이 없습니다.")

    # 11-1. 추후에 네이버 웹툰을 이용해볼 생각이 있으신가요? (파이차트)
    elif q_num == 111:
        col = 'intent_to_use_naver_webtoon' 
        if col in df.columns:
            intention_df = df[col].map({1: '예', 0: '아니오'}).value_counts().reset_index()
            intention_df.columns = ['intent_to_use_naver_webtoon', 'count']
            fig = px.pie(
                intention_df,
                names='intent_to_use_naver_webtoon',
                values='count'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("intent_to_use_naver_webtoon 컬럼이 없습니다.")


    # 12. 네이버 웹툰 사용 기간 (막대그래프)
    elif q_num == 12:
        col = 'naver_webtoon_usage_duration'
        duration_labels = {
            1: '6개월 미만',
            2: '6개월~1년 미만',
            3: '1년~3년 미만',
            4: '3년~5년 미만',
            5: '5년 이상'
        }
        duration_order = [1, 2, 3, 4, 5]
        duration_names = [duration_labels[i] for i in duration_order]
        duration_counts = df[col].value_counts().reindex(duration_order, fill_value=0)
        duration_percents = (duration_counts / duration_counts.sum() * 100).round(1)
        duration_df = pd.DataFrame({
            'duration': duration_names,
            'count': duration_counts.values,
            'percent': duration_percents.values
        })
        duration_df['bar_text'] = duration_df.apply(lambda x: f"{x['count']} ({x['percent']}%)", axis=1)
        fig = px.bar(
            duration_df,
            x='duration',
            y='count',
            text='bar_text',
            labels={'duration': '이용 기간', 'count': '응답 수'}
        )
        fig.update_traces(textposition='outside', marker_color='goldenrod')
        st.plotly_chart(fig, use_container_width=True)

    # 13. 네이버 웹툰 하면 떠오르는 이미지 (복수응답, 막대그래프)
    elif q_num == 13:
        image_col = 'naver_webtoon_image_association'
        image_category_list = [
            "광고가 자주 노출돼 사용이 불편했다", 
            "다양한 장르의 작품을 쉽게 찾을 수 있었다",
            "특정 작품이 네이버에만 있어 아쉬웠다",
            "그림 퀄리티가 전체적으로 뛰어나다",
            "선정적이거나 폭력적인 내용이 많아졌다",
            "내가 본 작품과 비슷한 추천이 자주 노출된다",
            "매일 기다려지는 연재 작품이 있다",
            "인기작과 일반 작품 간 품질 차이가 크다",
            "앱이나 웹사이트 사용이 불편하지 않다",
            "성인용 콘텐츠가 의도치 않게 노출된 적 있다",
            "무료로 보기 어려워 결제를 자주 하게 된다",
            "자주 보는 작가가 네이버에 많이 있다",
            "이야기 전개가 흥미롭고 집중된다",
            "내용이 반복적이고 참신하지 않다",
            "새로운 작품이나 회차가 자주 올라온다"
        ]
        def split_multi(x):
            return [i.strip() for i in re.split(r'[#,/]', str(x)) if i.strip()]
        image_responses = df[image_col].dropna().apply(split_multi)
        mapped = []
        for sublist in image_responses:
            for item in sublist:
                if item in image_category_list:
                    mapped.append(item)
        image_counts = pd.Series(mapped).value_counts().reindex(image_category_list, fill_value=0)
        respondent_count = df[image_col].dropna().shape[0]
        image_percents = (image_counts / respondent_count * 100).round(1)
        image_counts = image_counts[::-1]
        image_percents = image_percents[::-1]
        bar_text = [f"{v} ({p}%)" for v, p in zip(image_counts.values, image_percents)]
        fig = px.bar(
            x=image_counts.values,
            y=image_counts.index,
            orientation='h',
            text=bar_text,
            labels={'x': '응답 수', 'y': '이미지'}
        )
        fig.update_traces(textposition='outside', marker_color='forestgreen')
        st.plotly_chart(fig, use_container_width=True)

    # 14. 네이버 웹툰 서비스 이용 빈도 (막대그래프)
    elif q_num == 14:
        col = 'naver_webtoon_usage_frequency'
        freq_labels = {
            6: '거의 매일',
            5: '주 4~5회',
            4: '주 2~3회',
            3: '주 1회',
            2: '월 2~3회',
            1: '월 1회 이하'
        }
        freq_order = [1, 2, 3, 4, 5, 6]
        freq_names = [freq_labels[i] for i in freq_order]
        freq_counts = df[col].value_counts().reindex(freq_order, fill_value=0)
        freq_percents = (freq_counts / freq_counts.sum() * 100).round(1)
        freq_df = pd.DataFrame({
            'frequency': freq_names,
            'count': freq_counts.values,
            'percent': freq_percents.values
        })
        freq_df['bar_text'] = freq_df.apply(lambda x: f"{x['count']} ({x['percent']}%)", axis=1)
        fig = px.bar(
            freq_df,
            x='frequency',
            y='count',
            text='bar_text',
            labels={'frequency': '이용 빈도', 'count': '응답 수'}
        )
        fig.update_traces(textposition='outside', marker_color='dodgerblue')
        st.plotly_chart(fig, use_container_width=True)

    # 15. 선호 장르 (복수응답, 막대그래프)
    elif q_num == 15:
        genre_groups = [
            "로맨스 / 로맨스 판타지",
            "액션 / 판타지 / 무협",
            "스릴러 / 추리 / 미스터리",
            "드라마 / 감성",
            "학원 / 성장",
            "코미디 / 일상툰",
            "성인(19+)"
        ]
        onehot_cols = [f'preferred_webtoon_genre_{g}' for g in genre_groups if f'preferred_webtoon_genre_{g}' in df.columns]
        if onehot_cols:
            genre_sum = df[onehot_cols].sum().reindex(onehot_cols)
            genre_sum = genre_sum[::-1]
            genre_labels = [g for g in genre_groups if f'preferred_webtoon_genre_{g}' in genre_sum.index][::-1]
            total = genre_sum.sum()
            genre_percents = (genre_sum / total * 100).round(1)
            bar_text = [f"{v} ({p}%)" for v, p in zip(genre_sum.values, genre_percents)]
            fig = px.bar(
                x=genre_sum.values,
                y=genre_labels,
                orientation='h',
                text=bar_text,
                labels={'x': '응답 수', 'y': '장르'}
            )
            fig.update_traces(textposition='outside', marker_color='mediumpurple')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("원-핫 인코딩된 preferred_webtoon_genre 컬럼이 없습니다.")

    # 16. 유료 결제 경험 (파이차트)
    elif q_num == 16:
        col = 'has_paid_for_webtoon'
        paid_df = df[col].map({1: '예', 0: '아니오'}).value_counts().reset_index()
        paid_df.columns = ['has_paid_for_webtoon', 'count']
        fig = px.pie(
            paid_df,
            names='has_paid_for_webtoon',
            values='count'
        )
        st.plotly_chart(fig, use_container_width=True)

    # 17. 월평균 결제 금액 (막대그래프)
    elif q_num == 17:
        col = 'average_monthly_payment'
        payment_labels = {
            1: '1,000원 미만 (쿠키 ~10개)',
            2: '1,000원 ~ 5,000원 미만 (쿠키 10개 ~ 50개)',
            3: '5,000원 ~ 10,000원 미만 (쿠키 50개 ~ 100개)',
            4: '10,000원 ~ 30,000원 미만 (쿠키 100개 ~ 300개)',
            5: '30,000원 이상 (쿠키 300개 이상 ~)'
        }
        payment_order = [1, 2, 3, 4, 5]
        payment_names = [payment_labels[i] for i in payment_order]
        if 'has_paid_for_webtoon' in df.columns:
            filtered = df[df['has_paid_for_webtoon'] == 1]
        else:
            filtered = df
        payment_counts = filtered[col].value_counts().reindex(payment_order, fill_value=0)
        payment_percents = (payment_counts / payment_counts.sum() * 100).round(1)
        payment_df = pd.DataFrame({
            'payment': payment_names,
            'count': payment_counts.values,
            'percent': payment_percents.values
        })
        payment_df['bar_text'] = payment_df.apply(lambda x: f"{x['count']} ({x['percent']}%)", axis=1)
        fig = px.bar(
            payment_df,
            x='payment',
            y='count',
            text='bar_text',
            labels={'payment': '월평균 결제 금액', 'count': '응답 수'}
        )
        fig.update_traces(textposition='outside', marker_color='orange')
        st.plotly_chart(fig, use_container_width=True)

    # 18. 웹툰을 보는 주된 이유 (복수응답, 막대그래프)
    elif q_num == 18:
        col = 'reasons_for_reading_webtoons'
        def split_multi(x):
            return [i.strip() for i in str(x).split(',') if i.strip()]
        reason_responses = df[col].dropna().apply(split_multi)
        mapped = [item for sublist in reason_responses for item in sublist]
        reason_counts = pd.Series(mapped).value_counts()
        respondent_count = df[col].dropna().shape[0]
        reason_percents = (reason_counts / respondent_count * 100).round(1)
        reason_counts = reason_counts[::-1]
        reason_percents = reason_percents[::-1]
        bar_text = [f"{v} ({p}%)" for v, p in zip(reason_counts.values, reason_percents)]
        fig = px.bar(
            x=reason_counts.values,
            y=reason_counts.index,
            orientation='h',
            text=bar_text,
            labels={'x': '응답 수', 'y': '이유'}
        )
        fig.update_traces(textposition='outside', marker_color='teal')
        st.plotly_chart(fig, use_container_width=True)

    # 19. 성인 연령 확인 후 열람 가능한 콘텐츠 인지 (파이차트)
    elif q_num == 19:
        col = 'aware_of_age_restricted_content'
        aware_df = df[col].map({1: '예', 0: '아니오'}).value_counts().reset_index()
        aware_df.columns = ['aware_of_age_restricted_content', 'count']
        fig = px.pie(
            aware_df,
            names='aware_of_age_restricted_content',
            values='count'
        )
        st.plotly_chart(fig, use_container_width=True)

    # 20. 성인 연령 제한 작품 제공에 대한 의견 (막대그래프)
    elif q_num == 20:
        col = 'opinion_on_age_restricted_content'
        label_map = {
            1: '전혀 필요하지 않다',
            2: '별로 필요하지 않다',
            3: '보통',
            4: '어느 정도 필요하다',
            5: '매우 필요하다'
        }
        order = [1, 2, 3, 4, 5]
        labels = [label_map[i] for i in order]
        counts = df[col].value_counts().reindex(order, fill_value=0)
        percents = (counts / counts.sum() * 100).round(1)
        bar_text = [f"{v} ({p}%)" for v, p in zip(counts.values, percents)]
        fig = px.bar(
            x=labels,
            y=counts.values,
            text=bar_text,
            labels={'x': '의견', 'y': '응답 수'}
        )
        fig.update_traces(textposition='outside', marker_color='salmon')
        st.plotly_chart(fig, use_container_width=True)

    # 21. 성인 연령 제한 작품 이용 경험 (파이차트)
    elif q_num == 21:
        col = 'used_age_restricted_content'
        used_df = df[col].map({1: '예', 0: '아니오'}).value_counts().reset_index()
        used_df.columns = ['used_age_restricted_content', 'count']
        fig = px.pie(
            used_df,
            names='used_age_restricted_content',
            values='count'
        )
        st.plotly_chart(fig, use_container_width=True)

    # 22. 성인 연령 제한 작품 이용 이유 (복수응답, 막대그래프)
    elif q_num == 22:
        col = 'reason_for_using_age_restricted_content'
        def split_multi(x):
            return [i.strip() for i in re.split(r'[,/#]', str(x)) if i.strip()]
        responses = df[col].dropna().apply(split_multi)
        mapped = [item for sublist in responses for item in sublist]
        reason_counts = pd.Series(mapped).value_counts()
        top_n = 10
        reason_counts = reason_counts.head(top_n)[::-1]
        fig = px.bar(
            x=reason_counts.values,
            y=reason_counts.index,
            orientation='h',
            labels={'x': '응답 수', 'y': '이용 이유'}
        )
        fig.update_traces(text=reason_counts.values, textposition='outside', marker_color='crimson')
        st.plotly_chart(fig, use_container_width=True)

    # 23. 성인 연령 제한 작품 미이용 이유 (복수응답, 막대그래프)
    elif q_num == 23:
        col = 'reason_for_not_using_age_restricted_content'
        def split_multi(x):
            return [i.strip() for i in re.split(r'[,/#]', str(x)) if i.strip()]
        responses = df[col].dropna().apply(split_multi)
        mapped = [item for sublist in responses for item in sublist]
        reason_counts = pd.Series(mapped).value_counts()
        top_n = 10
        reason_counts = reason_counts.head(top_n)[::-1]
        fig = px.bar(
            x=reason_counts.values,
            y=reason_counts.index,
            orientation='h',
            labels={'x': '응답 수', 'y': '미이용 이유'}
        )
        fig.update_traces(text=reason_counts.values, textposition='outside', marker_color='slateblue')
        st.plotly_chart(fig, use_container_width=True)

    # 24. 다양한 연령층 콘텐츠 제공에 대한 의견 (막대그래프)
    elif q_num == 24:
        col = 'opinion_on_content_for_various_ages'
        label_map = {
            1: '매우 불만족',
            2: '불만족',
            3: '보통',
            4: '만족',
            5: '매우 만족'
        }
        order = [1, 2, 3, 4, 5]
        labels = [label_map[i] for i in order]
        counts = df[col].value_counts().reindex(order, fill_value=0)
        percents = (counts / counts.sum() * 100).round(1)
        bar_text = [f"{v} ({p}%)" for v, p in zip(counts.values, percents)]

        # 명시적으로 제시 
        bar_df = pd.DataFrame({
        '의견': labels,
        '응답 수': counts.values,
        'text': bar_text
        })
        fig = px.bar(
            bar_df,
            x='의견',
            y='응답 수',
            text='text'
        )

        fig.update_traces(textposition='outside', marker_color='seagreen')
        st.plotly_chart(fig, use_container_width=True)

    # 25. 브랜드 이미지 영향 (막대그래프)
    elif q_num == 25:
        col = 'impact_on_brand_image'
        label_map = {
            1: '매우 그렇지 않다',
            2: '그렇지 않다',
            3: '보통이다',
            4: '그렇다',
            5: '매우 그렇다'
        }
        order = [1, 2, 3, 4, 5]
        labels = [label_map[i] for i in order]
        counts = df[col].value_counts().reindex(order, fill_value=0)
        percents = (counts / counts.sum() * 100).round(1)
        bar_text = [f"{v} ({p}%)" for v, p in zip(counts.values, percents)]

        # 명시적으로 제시
        bar_df = pd.DataFrame({
        '영향': labels,
        '응답 수': counts.values,
        'text': bar_text
         })
        
        fig = px.bar(
            bar_df,
            x='영향',
            y='응답 수',
            text='text'
        )
        fig.update_traces(textposition='outside', marker_color='darkorange')
        st.plotly_chart(fig, use_container_width=True)

    # # 25-1. (주관식) 왜 그렇게 느끼셨는지 자유롭게 작성해주실 수 있을까요? (감정 유형별 단어 빈도)
    # elif q_num == 251:
    #     col = 'reason_for_brand_image_opinion'
    #     stopwords = {'오히려', '것', '더', '웹툰', '작품이', '네이버', "때문", '영화화', '영화계', '만화가', '만화', '문화생활', '영화', '이', '에','생각','.','을','적','의',',','와'}
    #     emotion_words = {
    #         '긍정': ['좋다', '행복', '괜찮', '완벽', '긍정', '필요', '재밌', '즐기', '공감', '존중', '개방', '만족', '고급', '완성도', '쾌적', '흥미', '집중', '변화', '트랜드', '다양성', '맞춤형', '필요하다'],
    #         '부정': ['아쉽', '문제', '별로', '타격', '부정', '싫', '불편', '과하다', '덜하다', 'B급', '노출', '선정적', '지나치', '독', '불만', '불쾌', '아니다', '없다'],
    #         '중립': ['없다', '모르', '모름', '없음', '별다르', '없을', '없다고', '없음']
    #     }
    #     emotion_type_map = {}
    #     for t, words in emotion_words.items():
    #         for w in words:
    #             emotion_type_map[w] = t
    #     if col in df.columns:
    #         text = ' '.join(df[col].dropna().astype(str))
    #         if text.strip():
    #             okt = Okt()
    #             words = [word for word in okt.morphs(text) if word not in stopwords]
    #             emotion_filtered = [w for w in words if w in emotion_type_map]
    #             freq = pd.Series(emotion_filtered).value_counts()
    #             table = []
    #             for word, count in freq.items():
    #                 table.append([emotion_type_map[word], word, count])
    #             df_table = pd.DataFrame(table, columns=['유형', '감정단어', '빈도'])
    #             df_table = df_table.sort_values(['유형', '빈도'], ascending=[True, False])
    #             st.dataframe(df_table)
    #             category_sum = df_table.groupby('유형')['빈도'].sum().reindex(['긍정', '부정', '중립'])
    #             fig = px.bar(
    #                 x=category_sum.index,
    #                 y=category_sum.values,
    #                 labels={'x': '감정 유형', 'y': '단어 빈도 합계'},
    #                 text=category_sum.values,
    #                 color=category_sum.index,
    #                 color_discrete_map={'긍정': 'royalblue', '부정': 'tomato', '중립': 'gray'},
    #                 title='감정 유형별 단어 빈도'
    #             )
    #             fig.update_traces(textposition='outside')
    #             fig.update_layout(
    #                 xaxis=dict(tickfont=dict(size=13)),
    #                 yaxis=dict(tickfont=dict(size=13)),
    #                 title_font_size=20,
    #                 showlegend=False
    #             )
    #             st.plotly_chart(fig, use_container_width=True)
    #         else:
    #             st.info("주관식 응답이 없습니다.")
    #     else:
    #         st.warning("reason_for_brand_image_opinion 컬럼이 없습니다.")

   
    # 26. 기업 브랜드 이미지 영향 (막대그래프)
    elif q_num == 26:
        col = 'impact_on_company_brand_image'
        label_map = {
            1: '전혀 없음',
            2: '낮음',
            3: '보통',
            4: '높음',
            5: '매우 높음'
        }
        order = [1, 2, 3, 4, 5]
        labels = [label_map[i] for i in order]
        counts = df[col].value_counts().reindex(order, fill_value=0)
        percents = (counts / counts.sum() * 100).round(1)
        bar_text = [f"{v} ({p}%)" for v, p in zip(counts.values, percents)]

       # 데이터프레임으로 명시적으로 구성 
        bar_df = pd.DataFrame({
            '영향': labels,
            '응답 수': counts.values,
            'text': bar_text
        })

        fig = px.bar(
            bar_df,
            x='영향',
            y='응답 수',
            text='text',
        )
        fig.update_traces(textposition='outside', marker_color='darkgreen')
        st.plotly_chart(fig, use_container_width=True)

#  # 26-1. (주관식) 가장 큰 영향을 주었다고 느끼신 측면이나 요인 (감정 유형별 단어 빈도)
#     elif q_num == 261:
#         col = 'reason_for_company_brand_image_opinion'
#         stopwords = {'오히려', '것', '더', '웹툰', '작품이', '네이버', "때문", '영화화', '영화계', '만화가', '만화', '문화생활', '영화', '이', '에','생각','.','을','적','의',',','와'}
#         emotion_words = {
#             '긍정': ['좋다', '행복', '괜찮', '완벽', '긍정', '필요', '재밌', '즐기', '공감', '존중', '개방', '만족', '고급', '완성도', '쾌적', '흥미', '집중', '변화', '트랜드', '다양성', '맞춤형', '필요하다'],
#             '부정': ['아쉽', '문제', '별로', '타격', '부정', '싫', '불편', '과하다', '덜하다', 'B급', '노출', '선정적', '지나치', '독', '불만', '불쾌', '아니다', '없다'],
#             '중립': ['없다', '모르', '모름', '없음', '별다르', '없을', '없다고', '없음']
#         }
#         emotion_type_map = {}
#         for t, words in emotion_words.items():
#             for w in words:
#                 emotion_type_map[w] = t
#         if col in df.columns:
#             text = ' '.join(df[col].dropna().astype(str))
#             if text.strip():
#                 okt = Okt()
#                 words = [word for word in okt.morphs(text) if word not in stopwords]
#                 emotion_filtered = [w for w in words if w in emotion_type_map]
#                 freq = pd.Series(emotion_filtered).value_counts()
#                 table = []
#                 for word, count in freq.items():
#                     table.append([emotion_type_map[word], word, count])
#                 df_table = pd.DataFrame(table, columns=['유형', '감정단어', '빈도'])
#                 df_table = df_table.sort_values(['유형', '빈도'], ascending=[True, False])
#                 st.dataframe(df_table)
#                 category_sum = df_table.groupby('유형')['빈도'].sum().reindex(['긍정', '부정', '중립'])
#                 fig = px.bar(
#                     x=category_sum.index,
#                     y=category_sum.values,
#                     labels={'x': '감정 유형', 'y': '단어 빈도 합계'},
#                     text=category_sum.values,
#                     color=category_sum.index,
#                     color_discrete_map={'긍정': 'royalblue', '부정': 'tomato', '중립': 'gray'},
#                     title='감정 유형별 단어 빈도'
#                 )
#                 fig.update_traces(textposition='outside')
#                 fig.update_layout(
#                     xaxis=dict(tickfont=dict(size=13)),
#                     yaxis=dict(tickfont=dict(size=13)),
#                     title_font_size=20,
#                     showlegend=False
#                 )
#                 st.plotly_chart(fig, use_container_width=True)
#             else:
#                 st.info("주관식 응답이 없습니다.")
#         else:
#             st.warning("reason_for_company_brand_image_opinion 컬럼이 없습니다.")
    # 27. 타 플랫폼과 비교한 성인 연령 제한 작품 수위 (막대그래프)
    elif q_num == 27:
        col = 'comparison_of_age_restricted_content_level'
        label_map = {
            1: '매우 낮은 편',
            2: '다소 낮은 편',
            3: '비슷함',
            4: '다소 높은 편',
            5: '매우 높은 편'
        }
        order = [1, 2, 3, 4, 5]
        labels = [label_map[i] for i in order]
        counts = df[col].value_counts().reindex(order, fill_value=0)
        percents = (counts / counts.sum() * 100).round(1)
        bar_text = [f"{v} ({p}%)" for v, p in zip(counts.values, percents)]
        fig = px.bar(
            x=labels,
            y=counts.values,
            text=bar_text,
            labels={'x': '수위 평가', 'y': '응답 수'}
        )
        fig.update_traces(textposition='outside', marker_color='slategray')
        st.plotly_chart(fig, use_container_width=True)

    # 28. 성인 연령 확인 후 불편/개선점 경험 (파이차트)
    elif q_num == 28:
        col = 'issues_with_age_restricted_content'
        issue_df = df[col].map({1: '예', 0: '아니오'}).value_counts().reset_index()
        issue_df.columns = ['issues_with_age_restricted_content', 'count']
        fig = px.pie(
            issue_df,
            names='issues_with_age_restricted_content',
            values='count'
        )
        st.plotly_chart(fig, use_container_width=True)

    # 29. 구체적 불편사항(주관식, 표)
    elif q_num == 29:
        col = 'specific_issues_with_age_restricted_content'
        result_df = df[[col]].loc[df[col] != ''].reset_index(drop=True)
        result_df.index = result_df.index + 1
        result_df.columns = ['구체적 불편사항(원문 응답)']
        st.dataframe(result_df)

    # 30. 다양한 연령대 작품 구분 및 성인 확인 관리 기능 만족도 (막대그래프)
    elif q_num == 30:
        col = 'satisfaction_with_content_management'
        label_map = {
            1: '매우 불만족',
            2: '다소 불만족',
            3: '보통',
            4: '다소 만족',
            5: '매우 만족'
        }
        order = [1, 2, 3, 4, 5]
        labels = [label_map[i] for i in order]
        counts = df[col].value_counts().reindex(order, fill_value=0)
        percents = (counts / counts.sum() * 100).round(1)
        bar_text = [f"{v} ({p}%)" for v, p in zip(counts.values, percents)]
        fig = px.bar(
            x=labels,
            y=counts.values,
            text=bar_text,
            labels={'x': '만족도', 'y': '응답 수'}
        )
        fig.update_traces(textposition='outside', marker_color='seagreen')
        st.plotly_chart(fig, use_container_width=True)

        
    # 31. 성인 연령 제한 작품 노출 증가 시 이용 빈도 변화 예상 (막대그래프)
    elif q_num == 31:
        col = 'likelihood_of_increased_viewing'
        label_map = {
            1: '전혀 그렇지 않다',
            2: '별로 그렇지 않다',
            3: '보통이다',
            4: '어느 정도 그렇다',
            5: '매우 그렇다'
        }
        order = [1, 2, 3, 4, 5]
        # 값이 문자열로 저장된 경우 숫자로 변환
        counts = pd.to_numeric(df[col], errors='coerce').value_counts().reindex(order, fill_value=0)
        percents = (counts / counts.sum() * 100).round(1)
        labels = [label_map[i] for i in order]
        bar_text = [f"{v} ({p}%)" for v, p in zip(counts.values, percents)]
        fig = px.bar(
            x=labels,
            y=counts.values,
            text=bar_text,
            labels={'x': '이용 증가 예상', 'y': '응답 수'}
        )
        fig.update_traces(textposition='outside', marker_color='royalblue')
        fig.update_layout(title_text="")  # 그래프 제목 제거
        st.plotly_chart(fig, use_container_width=True)