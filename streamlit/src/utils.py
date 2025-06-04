import pandas as pd
import re

def load_and_preprocess(df): #file_name(로컬 환경) -> df 변경
    # df = pd.read_excel(file_name) # 엑셀 파일을 읽어올 때 주석 처리(로컬 환경)
    df.columns = df.columns.str.strip()

    # 타임스탬프 컬럼명 및 이용자 동의 컬럼 삭제
    timestamp_col = '타임스탬프'
    if timestamp_col in df.columns:
        df = df.drop(columns=[timestamp_col])
        df.insert(0, 'no', range(1, len(df) + 1))
    df = df.drop(df.columns[1], axis=1)

    # 컬럼명 한글→영문 치환
    rename_dict = {
        '1. 연령대가 어떻게 되시나요?': 'age_group',
        '2. 성별을 알려주실 수 있나요?': 'gender',
        '3. 현재 어떤 일을 하고 계신가요?': 'occupation',
        '4. 결혼 여부는 어떻게 되시나요?': 'marital_status',
        '5. 현재 미성년 자녀가 있으신가요?': 'has_minor_children',
        "6. '네이버' 하면 가장 먼저 떠오르는 이미지는 어떤 것들이 있나요? (최대 3개까지 선택하실 수 있어요)": 'naver_image_association',
        '7. 전반적으로 네이버 서비스에 얼마나 만족하고 계신가요?': 'naver_service_satisfaction',
        '8. 평소 자주 사용하는 네이버 서비스는 무엇인가요? (최대 3개까지 선택하실 수 있어요)': 'frequent_naver_services',
        '9. 최근 1년 안에 웹툰을 본 적이 있으신가요?': 'webtoon_usage_last_year',
        '10. 사용 중인 웹툰 플랫폼이 있다면 모두 선택해주실 수 있나요?': 'webtoon_platforms_used',
        '11. 네이버 웹툰을 사용하지 않으셨다면, 어떤 이유가 있으신가요?': 'reason_not_using_naver_webtoon',
        '11-1. 추후에 네이버 웹툰을 이용해볼 생각이 있으신가요?': 'intent_to_use_naver_webtoon',
        '12. 네이버 웹툰을 얼마나 오랫동안 사용해오셨나요?': 'naver_webtoon_usage_duration',
        '13. 네이버 웹툰 하면 떠오르는 이미지를 3개 이내로 골라주실 수 있을까요? (최대 3개까지 선택하실 수 있어요)': 'naver_webtoon_image_association',
        '14. 네이버 웹툰 서비스를 얼마나 자주 사용하고 계신가요?': 'naver_webtoon_usage_frequency',
        '15. 네이버 웹툰에서 가장 선호하는 웹툰 장르는 어떤 것 인가요?': 'preferred_webtoon_genre',
        '16. 네이버 웹툰 콘텐츠 이용을 위해 유료 결제(예: 쿠키 충전, 유료 회차 구매 등)를 한 경험이 있으십니까?': 'has_paid_for_webtoon',
        '17. (결제 경험이 있으시다면) 지난 1년 동안 월평균 결제 금액은 어느 정도 되시나요?': 'average_monthly_payment',
        '18. 웹툰을 보는 주된 이유는 무엇인가요? (3개 이내로 골라주세요)': 'reasons_for_reading_webtoons',
        '19. 성인 연령 확인 후 열람 가능한 콘텐츠가 있다는 것을 알고 계셨나요?': 'aware_of_age_restricted_content',
        '20. 일반적으로 웹툰 플랫폼이 성인 연령 제한 작품을 제공하는 것에 대해 어떻게 생각하시나요?': 'opinion_on_age_restricted_content',
        '21. 네이버 웹툰에서 성인 연령 제한 작품을 이용해본 경험이 있으신가요?': 'used_age_restricted_content',
        '22. 성인 연령 제한 작품을 이용하신 주된 이유는 무엇인가요?': 'reason_for_using_age_restricted_content',
        '23. 이용하지 않으셨다면, 주된 이유는 무엇인가요?': 'reason_for_not_using_age_restricted_content',
        '24. 네이버 웹툰이 성인 연령 제한 작품을 포함하여 다양한 연령층을 고려한 콘텐츠를 제공하는 것에 대해 어떻게 생각하시나요?': 'opinion_on_content_for_various_ages',
        '25. 네이버 웹툰이 성인 독자층까지 고려한 다양한 작품을 제공하는 것이 네이버 웹툰 브랜드 이미지에 부정적인 영향을 끼쳤다고 생각하시나요?': 'impact_on_brand_image',
        '25-1. (주관식) 왜 그렇게 느끼셨는지 자유롭게 작성해주실 수 있을까요?': 'reason_for_brand_image_opinion',
        "26. 이러한 콘텐츠 구성(예: 다양한 연령층 대상 작품 제공 등)이 '네이버'라는 기업 전체의 브랜드 이미지에 부정적 영향을 준다고 생각하시나요?": 'impact_on_company_brand_image',
        '26-1. (주관식) 가장 큰 영향을 주었다고 느끼신 측면이나 요인은 무엇인가요? 간단히 말씀해 주세요.': 'reason_for_company_brand_image_opinion',
        '27. 타 웹툰 플랫폼(예: 카카오, 레진코믹스, 탑툰 등)과 비교했을 때, 네이버 웹툰의 성인 연령 제한 작품 수위는 어떤 편이라고 생각하시나요?': 'comparison_of_age_restricted_content_level',
        '28. 네이버 웹툰에서 성인 연령 확인 후 이용 가능한 작품들을 접하시면서 불편하거나 개선되었으면 하는 점이 있었나요? (네이버 웹툰 이용자 대상)': 'issues_with_age_restricted_content',
        '29. (주관식) 구체적으로 어떤 점이 불편했는지 알려주실 수 있나요?': 'specific_issues_with_age_restricted_content',
        '30. 현재 네이버 웹툰에서 다양한 연령대의 작품들을 구분하고, 성인 확인이 필요한 작품들에 대한 접근을 관리하는 기능(예: 성인인증, 검색 노출 방식 등)에 대해 얼마나 만족하시나요?': 'satisfaction_with_content_management',
        '31. 네이버 웹툰에서 성인 독자를 위한 작품들을 더 쉽게 발견하거나 관련 추천이 늘어난다면 (성인 연령 제한 작품이 더 눈에 띄게 노출된다면), 해당 작품들을 이전보다 더 자주 보게 될 것 같으신가요?': 'likelihood_of_increased_viewing',
        '32. 네이버 웹툰을 앞으로도 계속 사용하실 의향이 있으신가요? (네이버 웹툰 이용자 대상)': 'intention_to_continue_using_naver_webtoon'
    }
    df = df.rename(columns=rename_dict)

    # 이진 인코딩 (예/아니오 → 1/0)
    binary_cols = [
        'has_minor_children', 'webtoon_usage_last_year', 'has_paid_for_webtoon',
        'aware_of_age_restricted_content', 'used_age_restricted_content',
        'intent_to_use_naver_webtoon', 'issues_with_age_restricted_content'
    ]
    for col in binary_cols:
        if col in df.columns:
            df[col] = df[col].map({'예': 1, '아니오': 0})

    # 다중 선택형(쉼표 구분) 컬럼 원-핫 인코딩
    multi_cols = [
        'frequent_naver_services',
        'webtoon_platforms_used', 'naver_webtoon_image_association',
        'reasons_for_reading_webtoons'
    ]
    for col in multi_cols:
        if col in df.columns:
            dummies = df[col].str.get_dummies(sep=', ')
            dummies = dummies.add_prefix(f'{col}_')
            df = pd.concat([df, dummies], axis=1)

    # naver_image_association 지정 카테고리로 인코딩
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
    if 'naver_image_association' in df.columns:
        def split_multi(x):
            return [i.strip() for i in re.split(r'#', str(x))]
        for cat in category_list:
            df[f'naver_image_association_{cat}'] = df['naver_image_association'].apply(
                lambda x: int(cat in split_multi(x))
            )

    # reason_not_using_naver_webtoon 인코딩
    reason_categories = [
        "다른 플랫폼을 더 선호해서",
        "볼만한 작품이 없어서",
        "유료 콘텐츠 비용이 부담돼서",
        "서비스 이용이 불편해서",
        "19+ 콘텐츠가 있는 것이 싫어서",
        "네이버 웹툰에 대해 잘 몰라서"
    ]
    etc_keywords = [
        "웹툰 내의 문제가 사회적 이슈로 떠올랐는데도 제대로 된 대처를 하지 않아서",
        "기다리는게 귀찮음",
        "다른 플랫폼을 더 선호해서",
        "서비스 이용이 불편해서"
    ]
    def encode_reason(x):
        reasons = [i.strip() for i in str(x).split(',') if i.strip()]
        encoded = {}
        for cat in reason_categories:
            encoded[f'reason_not_using_naver_webtoon_{cat}'] = int(cat in reasons)
        etc_found = any(r in etc_keywords for r in reasons)
        encoded['reason_not_using_naver_webtoon_기타'] = int(etc_found)
        return pd.Series(encoded)
    if 'reason_not_using_naver_webtoon' in df.columns:
        reason_dummies = df['reason_not_using_naver_webtoon'].apply(encode_reason)
        df = pd.concat([df, reason_dummies], axis=1)

    # 선호 장르 다중 선택형 인코딩
    genre_groups = [
        "로맨스 / 로맨스 판타지",
        "액션 / 판타지 / 무협",
        "스릴러 / 추리 / 미스터리",
        "드라마 / 감성",
        "학원 / 성장",
        "코미디 / 일상툰",
        "성인(19+)"
    ]
    col = "preferred_webtoon_genre"
    if col in df.columns:
        def split_multi(x):
            return [i.strip() for i in str(x).split(',') if i.strip()]
        for g in genre_groups:
            df[f'{col}_{g}'] = df[col].apply(lambda x: int(g in split_multi(x)))

    # 순서형 인코딩 (1~5점 척도 등)
    ordinal_cols = [
        'naver_service_satisfaction',
        'opinion_on_content_for_various_ages', 'impact_on_brand_image',
        'impact_on_company_brand_image',
        'satisfaction_with_content_management',
        'intention_to_continue_using_naver_webtoon'
    ]
    for col in ordinal_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 12번 문항: 사용 기간 레이블 인코딩
    duration_label_map = {
        '6개월 미만': 1,
        '6개월 이상 ~ 1년 미만': 2,
        '1년 이상 ~ 3년 미만': 3,
        '3년 이상 ~ 5년 미만': 4,
        '5년 이상': 5
    }
    if 'naver_webtoon_usage_duration' in df.columns:
        df['naver_webtoon_usage_duration'] = df['naver_webtoon_usage_duration'].map(duration_label_map)

    # 14번 문항: 이용 빈도 레이블 인코딩
    frequency_label_map = {
        '거의 매일': 6,
        '주 4~5회': 5,
        '주 2~3회': 4,
        '주 1회': 3,
        '월 2~3회': 2,
        '월 1회 이하': 1
    }
    if 'naver_webtoon_usage_frequency' in df.columns:
        df['naver_webtoon_usage_frequency'] = df['naver_webtoon_usage_frequency'].map(frequency_label_map)

    # 17번 문항: 월평균 결제 금액 레이블 인코딩
    payment_label_map = {
        '1,000원 미만 (쿠키 ~10개)': 1,
        '1,000원 ~ 5,000원 미만 (쿠키 10개 ~ 50개)': 2,
        '5,000원 ~ 10,000원 미만 (쿠키 50개 ~ 100개)': 3,
        '10,000원 ~ 30,000원 미만 (쿠키 100개 ~ 300개)': 4,
        '30,000원 이상 (쿠키 300개 이상 ~)': 5
    }
    col = 'average_monthly_payment'
    if col in df.columns:
        df[col] = df[col].map(payment_label_map)

    # 20번 문항: 성인 연령 제한 작품 제공에 대한 의견
    opinion_label_map = {
        '전혀 필요하지 않다고 생각한다': 1,
        '별로 필요하지 않다고 생각한다': 2,
        '보통이다 (특별한 의견 없음)': 3,
        '어느 정도 필요하다고 생각한다': 4,
        '매우 필요하다고 생각한다': 5
    }
    col = 'opinion_on_age_restricted_content'
    if col in df.columns:
        df[col] = df[col].map(opinion_label_map)

    # 27번 문항: 타 플랫폼과 비교한 성인 연령 제한 작품 수위
    comparison_label_map = {
        '훨씬 낮다': 1,
        '다소 낮다': 2,
        '비슷하다': 3,
        '다소 높다': 4,
        '훨씬 높다': 5,
        '잘 모르겠다/이용 안 해봐서 비교 불가': 0
    }
    col = 'comparison_of_age_restricted_content_level'
    if col in df.columns:
        df[col] = df[col].map(comparison_label_map)

    # 31번 문항: 성인 연령 제한 작품 노출 증가 시 이용 빈도 변화
    likelihood_label_map = {
        '전혀 그렇지 않다': 1,
        '별로 그렇지 않다': 2,
        '보통이다': 3,
        '어느 정도 그렇다': 4,
        '매우 그렇다': 5
    }
    col = 'likelihood_of_increased_viewing'
    if col in df.columns:
        df[col] = df[col].map(likelihood_label_map)

    # 결측치 처리
    df = df.fillna('')

    return df