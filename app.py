import streamlit as st
import requests
import pandas as pd
import time
import random

# ==========================================
# 1. 마케터님의 아이디어로 완성된 안전한 크롤러 엔진
# ==========================================
def fetch_all_giftishow_products_safely():
    # 기프티쇼 비즈의 진짜 목록 API 주소
    url = "https://biz.giftishow.com/fo_api/ggoods/list" 
    
    # 봇 차단 방지를 위한 브라우저 위장 헤더
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "Origin": "https://biz.giftishow.com",
        "Referer": "https://biz.giftishow.com/ggoods/list",
        "Accept": "application/json, text/plain, */*"
    }
    
    all_products = []
    start_index = 1
    page_size = 100  # 서버 부담을 최소화하는 최적의 뭉텅이 크기
    
    # Streamlit 화면에 실시간 진행 상황을 보여주기 위한 앵커
    status_box = st.empty()
    progress_bar = st.progress(0)
    
    while True:
        payload = {
            "start": start_index,
            "size": page_size
        }
        
        try:
            # 서버에 데이터 요청 (POST 방식)
            response = requests.post(url, headers=headers, json=payload)
            
            # 서버 응답 체크 (IP 차단 등 비정상 상황 감지)
            if response.status_code != 200:
                st.error(f"⚠️ 서버 응답 이상 (에러코드: {response.status_code}). 안전을 위해 수집을 중단합니다.")
                break
                
            data = response.json()
            goods_list = data.get("result", {}).get("goodsList", [])
            
            # ❗ 더 이상 가져올 상품 데이터가 없으면 무한루프 탈출!
            if not goods_list:
                break
                
            # 뭉텅이 데이터 가공 및 쇼핑광고 URL 결합
            for p in goods_list:
                base_url = f"https://biz.giftishow.com/ggoods/detail/?goodsNo={p.get('goodsNo')}"
                
                # 🔥 네이버 쇼핑 광고 피드용 추적 파라미터 자동 완성
                naver_url = f"{base_url}&utm_source=naver&utm_medium=cps&utm_campaign=shopping_feed"
                
                all_products.append({
                    "상품번호": p.get("goodsNo"),
                    "상품코드": p.get("goodsCode"),
                    "브랜드": p.get("brandName"),
                    "상품명": p.get("goodsName"),
                    "정상가": p.get("realPrice"),
                    "할인가": p.get("discountPrice"),
                    "카테고리": p.get("categoryName"),
                    "쇼핑광고용 URL": naver_url
                })
                
            current_count = len(all_products)
            
            # 🔥 [핵심 요구사항] 사람처럼 보이기 위한 '3초+알파' 랜덤 딜레이 적용!
            # 기계처럼 정확히 3초면 걸릴 수 있으니 3초~4.5초 사이로 유연하게 쉽니다.
            sleep_time = 3.0 + random.uniform(0, 1.5)
            status_box.info(f"🔄 현재 {current_count}개 상품 수집 완료... 사이트 보호를 위해 잠시 숨 고르는 중 ({sleep_time:.1f}초 대기) ⏳")
            
            # 다음 100개를 가져오기 위해 인덱스 점프
            start_index += page_size
            time.sleep(sleep_time)
            
        except Exception as e:
            st.error(f"❌ 수집 중 오류가 발생했습니다: {str(e)}")
            break
            
    # 완료 후 안내창 비우기
    status_box.empty()
    progress_bar.empty()
    
    return pd.DataFrame(all_products)

# ==========================================
# 2. 마케팅 팀원 누구나 쓰는 직관적인 웹 UI 화면
# ==========================================
st.set_page_config(page_title="기프티쇼비즈 URL 생성기", layout="wide", page_icon="🎁")

st.title("🎁 기프티쇼 비즈 쇼핑광고 URL 대량 자동 생성기")
st.subheader("마케터 전용 대시보드")
st.write("---")
st.write("👉 **[시작]** 버튼을 누르면 기프티쇼 비즈의 전체 상품을 안전하게 수집한 뒤, 네이버 쇼핑 추적 파라미터가 결합된 광고 피드용 엑셀을 생성합니다.")

# 깔끔한 경고 문구 추가 (마케터님의 리스크 관리 마인드 반영)
st.warning("⚠️ 본 도구는 사이트 장애 방지를 위해 100건당 약 3초의 안전 딜레이를 두고 작동하므로, 전체 수집 완료까지 다소 시간이 소요될 수 있습니다.")

# 실행 버튼
if st.button("🚀 전체 상품 크롤링 및 광고 URL 생성 시작", type="primary"):
    
    df_result = fetch_all_giftishow_products_safely()
    
    if not df_result.empty:
        st.success(f"🎉 성공적으로 기프티쇼 비즈의 전체 상품 ({len(df_result)}건) 수집을 완료했습니다!")
        
        # 화면에 엑셀 형태의 데이터프레임 시각화
        st.dataframe(df_result, use_container_width=True)
        
        # 엑셀(CSV) 다운로드 버튼 활성화
        csv = df_result.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 쇼핑광고용 엑셀(CSV) 다운로드",
            data=csv,
            file_name=f"giftishow_advertisement_feed_{time.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.error("데이터를 수집하지 못했습니다. 통신 상태나 API 주소를 다시 확인해 주세요.")