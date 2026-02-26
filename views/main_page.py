import streamlit as st
from github_storage import load_reports

def show_main_page():
    st.title("📰 1장짜리 IT 보고서")
    
    reports = load_reports()
    
    if not reports:
        st.info("아직 생성된 보고서가 없습니다. 관리자 대시보드에서 리포트를 생성해보세요.")
        return

    # Sort dates descending
    sorted_dates = sorted(reports.keys(), reverse=True)
    
    st.sidebar.markdown("### 🕒 지난 보고서 보기 (생성 시각 기준)")
    selected_date = st.sidebar.radio("생성 시각 선택", sorted_dates)
    
    if selected_date:
        st.subheader(f"🕒 {selected_date} 보고서")
        st.markdown(reports[selected_date])
