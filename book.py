import streamlit as st
import pandas as pd

# 1. 웹사이트 브라우저 기본 설정
st.set_page_config(page_title="한글 맞춤 도서 추천 시스템 📚", layout="centered")

# ==========================================
# 2. 전처리 완료된 CSV 데이터 로드
# ==========================================
@st.cache_data
def load_data():
    try:
        # 코랩에서 다운로드받은 파일을 읽어옵니다.
        df = pd.read_csv('processed_books.csv')
        return df
    except FileNotFoundError:
        st.error("⚠️ 'processed_books.csv' 파일이 book.py와 같은 폴더에 없습니다! 코랩에서 다운받은 파일을 이 폴더 안으로 꼭 옮겨주세요.")
        st.stop()

df_processed = load_data()

# 한글 베스트셀러 필터링용 리스트
bestseller_korean_titles = ['데미안', '동물농장', '이기적 유전자', '헝거 게임', '해리 포터', '트와일라잇', '앵무새 죽이기', '위대한 개츠비', '잘못은 우리 별에 있어', '호빗', '호밀밭의 파수꾼', '천사와 악마', '오만과 편견', '다빈치 코드', '멋진 신세계', '반지의 제왕', '로미오와 줄리엣', '햄릿', '총, 균, 쇠', '사피엔스', '코스모스']

# ==========================================
# 2-2. 문과/이과 오분류 차단 엔진
# ==========================================
def 정밀_장르_분류(row):
    title_str = str(row['도서명']).lower()
    author_str = str(row['저자']).lower()
    
    # 1) 명백한 문과 베스트셀러는 이과 키워드 검사 전에 무조건 문과로 튕겨냅니다. (오분류 원천 차단)
    humanities_titles = [
        '데미안', '동물농장', '헝거 게임', '해리 포터', '트와일라잇', 
        '앵무새 죽이기', '위대한 개츠비', '잘못은 우리 별에 있어', '호빗', 
        '호밀밭의 파수꾼', '천사와 악마', '오만과 편견', '다빈치 코드', 
        '멋진 신세계', '반지의 제왕', '로미오와 줄리엣', '햄릿'
    ]
    if any(h_title in title_str for h_title in humanities_titles):
        return '문과 책', '인문/사회/문학'
        
    # 2) 이과 책을 결정짓는 과학/기술 전문 키워드
    science_keywords = [
        'science', 'physics', 'biology', 'chemistry', 'calculus', 'computer', 'engineering', 
        'quantum', 'evolution', 'gene', 'dna', 'brain', 'algorithm', 'medical', 'anatomy', 
        'astronomy', 'geometry', '이기적 유전자', '코스모스', '총, 균, 쇠', '사피엔스'
    ]
    
    # 판타지 소설에 자주 쓰이는 단어인 'star', 'earth'를 빼고 우주 전문 문맥으로 대체
    universe_keywords = ['space', 'universe', 'cosmos', 'astrophysics']
    
    # 대표적인 과학 저자 리스트
    science_authors = ['richard dawkins', '리처드 도킨스', 'carl sagan', '칼 세이건', 'stephen hawking', 'albert einstein']
    
    # 3) 이과 조건 검증
    is_science = (
        any(k in title_str for k in science_keywords) or 
        any(u in title_str for u in universe_keywords) or 
        any(a in author_str for a in science_authors)
    )
    
    if is_science:
        return '이과 책', '자연/공학'
    else:
        return '문과 책', '인문/사회/문학'

# 데이터프레임의 장르 체계를 정밀 필터 기준으로 갱신합니다.
df_processed[['책_종류', '세부_분야']] = df_processed.apply(
    lambda r: pd.Series(정밀_장르_분류(r)), axis=1
)

# ==========================================
# 3. 첫 접속 시 보이는 [들어가기] 대문 페이지
# ==========================================
if 'entered' not in st.session_state:
    st.session_state.entered = False

if not st.session_state.entered:
    st.write("")
    st.write("")
    st.markdown("<h1 style='text-align: center; color: #1e293b; font-family: sans-serif;'>📚 AI 맞춤형 도서 추천 시스템</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 17px;'>나에게 딱 맞는 문과/이과 성향별 베스트셀러를 찾아보세요.</p>", unsafe_allow_html=True)
    st.write("")
    
    # 중앙 정렬을 위한 레이아웃 분할
    _, center_col, _ = st.columns([0.5, 2, 0.5])
    with center_col:
        st.image("https://images.unsplash.com/photo-1507842217343-583bb7270b66?q=80&w=1000", use_container_width=True)
        st.write("")
        
        if st.button("🚀 추천 시스템 들어가기", use_container_width=True, type="primary"):
            st.session_state.entered = True
            st.rerun()
            
    st.stop()

# ==========================================
# 4. 메인 도서 추천 UI (들어가기 성공 후 표시)
# ==========================================
st.title("📚 문/이과 맞춤형 도서 추천 서비스")
st.markdown("사이드바에서 장르를 고르거나, 하단의 베스트셀러 전용 버튼을 눌러보세요.")
st.markdown("---")

# 사이드바 카테고리 구성
st.sidebar.header("🔍 카테고리 필터")
book_categories = {
    '문과 책': ['인문/사회/문학'],  
    '이과 책': ['자연/공학']
}

selected_type = st.sidebar.selectbox("대분류 선택", list(book_categories.keys()))
selected_detail = st.sidebar.selectbox("세부 분야 선택", book_categories[selected_type])

# 화면에 두 개의 버튼을 가로로 배치
col1, col2 = st.columns(2)
with col1:
    btn_general = st.button("🔍 선택 분야 추천받기", use_container_width=True)
with col2:
    btn_bestseller = st.button("🔥 한글 베스트셀러만 보기", use_container_width=True)

# 버튼 작동에 따른 데이터 필터링
filtered_books = pd.DataFrame()
success_msg = ""

if btn_general:
    filtered_books = df_processed[
        (df_processed['책_종류'] == selected_type) & 
        (df_processed['세부_분야'] == selected_detail)
    ]
    # 🔥 [오타 수정] :? 부분이 :, 로 정상 수정되었습니다.
    success_msg = f"✨ '{selected_type} > {selected_detail}' 분야 추천 결과 (총 {len(filtered_books):,}권 중 랜덤 3권)"

elif btn_bestseller:
    filtered_books = df_processed[df_processed['도서명'].isin(bestseller_korean_titles)]
    success_msg = f"🔥 [초인기 베스트셀러] 한글화 패치 완료된 {len(filtered_books)}권 중 랜덤 3권 추천"

# ==========================================
# 5. 책 표지가 포함된 고급 카드형 UI 출력
# ==========================================
if not filtered_books.empty:
    st.success(success_msg)
    
    # 3권 무작위 샘플링
    sample_size = min(3, len(filtered_books))
    top_books = filtered_books.sample(n=sample_size)
    
    for _, row in top_books.iterrows():
        img_url = row['이미지_URL_L'] if pd.notnull(row['이미지_URL_L']) else 'https://via.placeholder.com/100x140?text=No+Image'
        
        # UI 카드 디자인 레이아웃 출력
        st.markdown(f"""
        <div style="display: flex; margin-bottom: 20px; border: 1px solid #e2e8f0; padding: 15px; border-radius: 12px; background-color: #ffffff; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <img src="{img_url}" style="width: 100px; max-height: 140px; margin-right: 20px; object-fit: contain; border-radius: 6px; border: 1px solid #f1f5f9;">
            <div style="display: flex; flex-direction: column; justify-content: center;">
                <h3 style="margin: 0 0 6px 0; color: #0f172a; font-size: 19px; font-family: sans-serif; font-weight: 600;">{row['도서명']}</h3>
                <p style="margin: 3px 0; color: #334155; font-size: 14px; font-family: sans-serif;"><b>저자:</b> {row['저자']}</p>
                <p style="margin: 3px 0; color: #64748b; font-size: 13px; font-family: sans-serif;">출판연도: {int(row['출판연도'])}년 (정규화 지수: {row['출판연도_정규화']:.4f})</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
elif btn_general or btn_bestseller:
    st.warning("❌ 조건에 맞는 도서 데이터를 찾을 수 없습니다.")