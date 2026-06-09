import streamlit as st
import requests
import pandas as pd
import time
import random

# ==========================================
# 1. 특정 브랜드를 타겟팅하는 스마트 크롤러 엔진
# ==========================================
def fetch_brand_products_safely(brand_code, brand_name):
    url = "https://biz.giftishow.com/fo_api/ggoods/list"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://biz.giftishow.com/goods/list",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*"
    }
    
    all_products = []
    start_index = 1
    page_size = 200  
    
    status_box = st.empty()
    
    while True:
        # 🔥 마케터님이 찾아낸 브랜드 타겟팅 규격 적용!
        payload = {
            "start": str(start_index),
            "size": str(page_size),
            "lineUp": "popular",
            "brandCode": [brand_code],
            "brandName": [brand_name]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                st.error(f"⚠️ 서버 연결 실패 (에러코드: {response.status_code})")
                break
                
            json_data = response.json()
            
            if json_data.get('code') in ['0000', 'SUC0000']:
                result_list_data = json_data.get('result', {}).get('resultList', [])
                
                if isinstance(result_list_data, dict):
                    items = result_list_data.get("", [])  
                else:
                    items = result_list_data
                
                if not items:
                    break
                    
                for p in items:
                    goods_no = p.get('goodsNo')
                    if goods_no:
                        base_url = f"https://biz.giftishow.com/ggoods/detail/?goodsNo={goods_no}"
                        naver_url = f"{base_url}&utm_source=naver&utm_medium=cps&utm_campaign=shopping_feed"
                        
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
                sleep_time = 3.0 + random.uniform(0, 1.2)
                status_box.info(f"🔄 '{brand_name}' 상품 {current_count}개 수집 완료... 안전 대기 중 ({sleep_time:.1f}초) ⏳")
                
                start_index += page_size
                time.sleep(sleep_time)
                
            else:
                st.error(f"❌ 서버 에러 메시지: {json_data.get('message')}")
                break
                
        except Exception as e:
            st.error(f"❌ 수집 중 오류가 발생했습니다: {str(e)}")
            break
            
    status_box.empty()
    return pd.DataFrame(all_products)

# ==========================================
# 2. 마케터를 위한 브랜드 필터링 웹 UI
# ==========================================
st.set_page_config(page_title="브랜드별 URL 생성기", layout="wide", page_icon="🎯")

st.title("🎯 기프티쇼 비즈 브랜드별 타겟팅 URL 생성기")
st.write("원하는 브랜드를 선택하면 해당 브랜드의 상품만 수집하여 쇼핑광고 피드를 생성합니다.")
st.write("---")

# 💡 임시로 세팅해 둔 브랜드 사전 (추후 API로 100% 자동화 예정)
# 마케터님이 알고 계신 코드를 여기에 계속 추가하실 수 있습니다.
KNOWN_BRANDS = {
    "스타벅스": "BR00007"
}

# 사용자 UI 창
selected_brand_name = st.selectbox(
    "1. 수집할 브랜드를 선택하세요", 
    options=list(KNOWN_BRANDS.keys())
)
selected_brand_code = KNOWN_BRANDS[selected_brand_name]

st.info(f"선택된 브랜드: **{selected_brand_name}** (코드: {selected_brand_code})")

# 실행 버튼
if st.button(f"🚀 '{selected_brand_name}' 상품 크롤링 시작", type="primary"):
    
    df_result = fetch_brand_products_safely(selected_brand_code, selected_brand_name)
    
    if not df_result.empty:
        st.success(f"🎉 성공적으로 {selected_brand_name} 상품 수집을 완료했습니다! (총 {len(df_result)}건)")
        st.dataframe(df_result, use_container_width=True)
        
        csv = df_result.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 쇼핑광고용 엑셀(CSV) 다운로드",
            data=csv,
            file_name=f"giftishow_{selected_brand_name}_feed_{time.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.error("데이터를 수집하지 못했습니다.")
