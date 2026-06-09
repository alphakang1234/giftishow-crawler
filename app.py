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
            
            # 🔥 [핵심 수정 1] 마케터님이 찾아낸 새로운 성공 코드 'SUC0000' 추가 반영!
            if json_data.get('code') in ['0000', 'SUC0000']:
                
                # 🔥 [핵심 수정 2] 변경된 주머니 이름 'resultList' 확인
                result_list_data = json_data.get('result', {}).get('resultList', [])
                
                # 🔥 [핵심 수정 3] 빈칸("")이라는 독특한 키(Key) 안에 리스트가 숨어있는 구조 파훼!
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
                        
                        all_products.append({
                            "상품번호": goods_no,
                            "상품코드": p.get('goodsCode'),
                            "브랜드": p.get('brandName'),
                            "상품명": p.get('goodsName'),
                            "정상가": p.get
