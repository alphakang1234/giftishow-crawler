import streamlit as st
import requests
import pandas as pd
import time
import random

# ==========================================
# 1. 마케터님의 통찰로 1,000건 이상 전수 수집하는 엔진
# ==========================================
def fetch_all_products_safely():
    url = "https://biz.giftishow.com/fo_api/ggoods/list"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://biz.giftishow.com/goods/list",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*"
    }
    
    all_products = []
    current_page = 1  # 🔥 start 파라미터가 '페이지 번호'이므로 1페이지부터 시작!
    page_size = 200   # 한 번에 가져올 뭉텅이 크기
    
    status_box = st.empty()
    
    while True:
        # payload의 start에 현재 페이지 번호를 문자열로 주입
        payload = {
            "start": str(current_page),
            "size": str(page_size),
            "lineUp": "popular"
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
                
                # ❗ 더 이상 가져올 상품 데이터가 없으면 무한루프 탈출
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
                status_box.info(f"🔄 현재 {current_page}페이지 수집 완료 (총 {current_count}개 상품)... 안전 대기 중 ({sleep_time:.1f}초) ⏳")
                
                # 🔥 [핵심 수정] 200을 더하는 게 아니라, 다음 페이지인 '2페이지', '3페이지'로 1씩 증가!
                current_page += 1
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
# 2. 스마트 필터링 대시보드 UI
# ==========================================
st.set_page_config(page_title="통합 브랜드 URL 생성기", layout="wide", page_icon="🎯")

st.title("🎯 기프티쇼 비즈 통합 브랜드 타겟팅 URL 생성기")
st.write("전체 상품을 한 번 긁어온 후, 원하는 브랜드를 자유롭게 선택해 0.1초 만에 광고 피드를 뽑아냅니다.")
st.write("---")

if 'all_data' not in st.session_state:
    st.session_state['all_data'] = pd.DataFrame()

# ------------------------------------------
# [1단계] 전체 데이터 수집 영역
# ------------------------------------------
if st.session_state['all_data'].empty:
    st.warning("⚠️ 아직 메모리에 수집된 데이터가 없습니다. 먼저 전체 상품을 불러오세요.")
    if st.button("🚀 1단계: 전체 상품 수집 및 브랜드 추출 시작", type="primary"):
        df_result = fetch_all_products_safely()
        
        if not df_result.empty:
            st.session_state['all_data'] = df_result
            st.success(f"🎉 성공적으로 전체 상품 (총 {len(df_result)}건) 수집을 완료했습니다!")
            st.rerun() 
else:
    st.success(f"✅ 현재 메모리에 전체 상품 ({len(st.session_state['all_data'])}건)이 안전하게 저장되어 있습니다.")
    if st.button("🔄 최신 데이터로 다시 수집하기"):
        st.session_state['all_data'] = pd.DataFrame()
        st.rerun()

st.write("---")

# ------------------------------------------
# [2단계] 브랜드 추출 및 필터링 영역
# ------------------------------------------
if not st.session_state['all_data'].empty:
    st.subheader("2단계: 원하는 브랜드 필터링 및 다운로드")
    
    df = st.session_state['all_data']
    brand_list = df['브랜드'].dropna().unique().tolist()
    brand_list.sort() 
    
    selected_brand = st.selectbox("👇 광고를 세팅할 브랜드를 선택하세요", options=brand_list)
    
    filtered_df = df[df['브랜드'] == selected_brand]
    
    st.info(f"✨ 선택된 브랜드: **{selected_brand}** (해당 브랜드 상품 총 {len(filtered_df)}건)")
    
    st.dataframe(filtered_df, use_container_width=True)
    
    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label=f"📥 '{selected_brand}' 전용 쇼핑광고 엑셀 다운로드",
            data=csv,
            file_name=f"giftishow_{selected_brand}_feed_{time.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
