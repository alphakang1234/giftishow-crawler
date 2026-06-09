import streamlit as st
import requests
import pandas as pd
import time
import random

# ==========================================
# 1. 마케터님의 날카로운 디버깅으로 완성된 크롤러 엔진
# ==========================================
def fetch_all_giftishow_products_safely():
    # 마케터님이 검증하신 진짜 목록 API 주소
    url = "https://biz.giftishow.com/fo_api/ggoods/list"
    
    # 브라우저 위장 헤더 환경 세팅
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://biz.giftishow.com/goods/list",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*"
    }
    
    all_products = []
    start_index = 1
    page_size = 200  # 한 번에 200개씩 뭉텅이로 가져오기
    
    # Streamlit 화면에 실시간 진행 상황을 보여주기 위한 알림창
    status_box = st.empty()
    
    while True:
        # start와 size를 반드시 "문자열" 형태로 전송
        payload = {
            "start": str(start_index),
            "size": str(page_size),
            "lineUp": "popular",
            "categoryList": ["1"],      # 커피/음료 카테고리 타겟팅
            "categoryName": ["커피/음료"]
        }
        
        try:
            # 서버에 데이터 요청 (POST 방식)
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                st.error(f"⚠️ 서버 연결 실패 (에러코드: {response.status_code}). 안전을 위해 수집을 중단합니다.")
                break
                
            json_data = response.json()
            
            # 마케터님이 찾아낸 새로운 성공 코드 'SUC0000' 추가 반영
            if json_data.get('code') in ['0000', 'SUC0000']:
                
                # 변경된 주머니 이름 'resultList' 확인
                result_list_data = json_data.get('result', {}).get('resultList', [])
                
                # 빈칸("")이라는 독특한 키(Key) 안에 리스트가 숨어있는 구조 파훼
                if isinstance(result_list_data, dict):
                    items = result_list_data.get("", [])  
                else:
                    items = result_list_data
                
                # ❗ 더 이상 가져올 상품 데이터가 없으면 무한루프 탈출!
                if not items:
                    break
                    
                # 200개 뭉텅이 데이터 가공 및 쇼핑광고 URL 결합
                for p in items:
                    goods_no = p.get('goodsNo')
                    if goods_no:
                        base_url = f"https://biz.giftishow.com/ggoods/detail/?goodsNo={goods_no}"
                        
                        # 네이버 쇼핑 광고 피드용 추적 파라미터 자동 완성
                        naver_url = f"{base_url}&utm_source=naver&utm_medium=cps&utm_campaign=shopping_feed"
                        
                        # 바로 아래 이 부분의 괄호가 지워졌던 것입니다!
                        all_products.append({
                            "상품번호": goods_no,
                            "상품코드": p.get('goodsCode'),
                            "브랜드": p.get('brandName'),
                            "상품명": p.get('goodsName'),
                            "정상가": p.get('realPrice'),
                            "할인가": p.get('discountPrice'),
                            "쇼핑광고용 URL": naver_url
                        })
                
                current_count = len(all_products)
                
                # ⏱️ 마케터님의 리스크 관리: 3초(+알파) 랜덤 텀 두기!
                sleep_time = 3.0 + random.uniform(0, 1.2)
                status_box.info(f"🔄 현재 {current_count}개 상품 수집 완료... IP 차단 방지를 위해 {sleep_time:.1f}초간 대기합니다. ⏳")
                
                # 다음 페이지를 가져오기 위해 인덱스 점프
                start_index += page_size
                time.sleep(sleep_time)
                
            else:
                st.error(f"❌ 서버 에러 메시지: {json_data.get('message')}")
                st.json(json_data)
                break
                
        except Exception as e:
            st.error(f"❌ 수집 중 오류가 발생했습니다: {str(e)}")
            break
            
    # 완료 후 안내창 비우기
    status_box.empty()
    
    return pd.DataFrame(all_products)

# ==========================================
# 2. 마케팅 팀원 누구나 쓰는 직관적인 웹 UI 화면
# ==========================================
st.set_page_config(page_title="기프티쇼비즈 URL 생성기", layout="wide", page_icon="🎁")

st.title("🎁 기프티쇼 비즈 쇼핑광고 URL 대량 자동 생성기")
st.subheader("마케터 전용 대시보드")
st.write("---")
st.write("👉 **[시작]** 버튼을 누르면 기프티쇼 비즈의 커피/음료 상품을 안전하게 수집한 뒤, 네이버 쇼핑 추적 파라미터가 결합된 광고 피드용 엑셀을 생성합니다.")

st.warning("⚠️ 본 도구는 사이트 장애 및 부정 접근 차단 방지를 위해 다음 호출까지 3초 이상의 안전 딜레이를 두고 작동합니다.")

# 실행 버튼
if st.button("🚀 전체 상품 크롤링 및 광고 URL 생성 시작", type="primary"):
    
    df_result = fetch_all_giftishow_products_safely()
    
    if not df_result.empty:
        st.success(f"🎉 성공적으로 상품 수집을 완료했습니다! (총 {len(df_result)}건)")
        
        st.dataframe(df_result, use_container_width=True)
        
        csv = df_result.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 쇼핑광고용 엑셀(CSV) 다운로드",
            data=csv,
            file_name=f"giftishow_advertisement_feed_{time.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.error("데이터를 수집하지 못했습니다. 통신 상태를 확인해 주세요.")
