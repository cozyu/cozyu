import streamlit as st
import feedparser
import google.generativeai as genai
from datetime import datetime, timedelta
import pandas as pd
import time
from github_storage import load_feeds, save_feeds, save_report, load_stats

def collect_recent_news(feed_urls, days=3):
    """
    Collect news items from given RSS feeds that were published in the last `days` days.
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    articles = []

    for url in feed_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                # Try to parse published date
                published_time = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_time = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
                
                if published_time and published_time >= cutoff_date:
                    articles.append({
                        "title": entry.get("title", "No Title"),
                        "summary": entry.get("summary", ""),
                        "link": entry.get("link", url),
                        "published": published_time.strftime("%Y-%m-%d %H:%M:%S")
                    })
        except Exception as e:
            st.error(f"Error parsing feed {url}: {e}")

    return articles

def generate_report(api_key, articles):
    """
    Generate a formatted report using Google Gemini API.
    """
    if not articles:
        return "수집된 기사가 없습니다."

    genai.configure(api_key=api_key)
    # Using gemini-3-flash-preview
    model = genai.GenerativeModel('gemini-3-flash-preview')

    prompt = """
다음은 최근 IT 뉴스 기사들의 제목, 요약, 링크 정보입니다.
이 데이터를 바탕으로 A4 1장 분량의 마크다운 형식으로 '1장짜리 IT 보고서'를 작성해 주세요.
지침은 다음과 같습니다:
1. 전체 기사를 분석하여 주요 토픽별로 그룹화하세요.
2. 각 토픽의 핵심 내용을 간결하게 요약하세요.
3. 관련 기사의 원문 링크를 반드시 포함하세요.
4. 전문적이고 깔끔한 뉴스레터 어조를 유지하세요.

기사 데이터:
"""
    for i, article in enumerate(articles):
        prompt += f"{i+1}. 제목: {article['title']}\n"
        prompt += f"   요약: {article['summary'][:300]}...\n"
        prompt += f"   링크: {article['link']}\n\n"

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"보고서 생성 중 오류가 발생했습니다: {e}"

def show_admin_page():
    st.title("⚙️ 관리자 대시보드")
    
    # Simple Password Authentication
    admin_password = st.secrets.get("ADMIN_PASSWORD", "admin")
    
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        pwd_input = st.text_input("관리자 비밀번호를 입력하세요:", type="password")
        if st.button("로그인"):
            if pwd_input == admin_password:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("비밀번호가 일치하지 않습니다.")
        return

    if st.button("로그아웃"):
        st.session_state.admin_logged_in = False
        st.rerun()

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📡 RSS 피드 관리", "🤖 AI 뉴스 수집 & 분석", "📊 접속 통계"])

    with tab1:
        st.subheader("등록된 RSS 피드")
        feeds = load_feeds()
        
        if feeds:
            for i, feed in enumerate(feeds):
                col1, col2 = st.columns([8, 2])
                with col1:
                    st.write(f"- {feed}")
                with col2:
                    if st.button("삭제", key=f"del_feed_{i}"):
                        feeds.remove(feed)
                        save_feeds(feeds)
                        st.success("피드가 삭제되었습니다.")
                        st.rerun()
        else:
            st.info("등록된 RSS 피드가 없습니다.")

        st.markdown("### 새 피드 추가")
        new_feed = st.text_input("RSS URL을 입력하세요:")
        if st.button("추가"):
            if new_feed and new_feed not in feeds:
                feeds.append(new_feed)
                save_feeds(feeds)
                st.success("피드가 추가되었습니다.")
                st.rerun()
            elif new_feed in feeds:
                st.warning("이미 등록된 피드입니다.")
            else:
                st.warning("URL을 입력해주세요.")

    with tab2:
        st.subheader("뉴스 수집 및 보고서 생성 맞춤 설정")
        if st.button("최근 3일치 뉴스 수집 및 AI 리포트 생성 ✨", type="primary"):
            api_key = st.secrets.get("GEMINI_API_KEY")
            if not api_key:
                st.error("GEMINI_API_KEY가 secrets에 설정되어 있지 않습니다.")
                return

            with st.spinner("RSS 기사 수집 중..."):
                current_feeds = load_feeds()
                articles = collect_recent_news(current_feeds, days=3)
            
            if not articles:
                st.warning("최근 3일간 수집된 새 기사가 없습니다.")
            else:
                st.success(f"총 {len(articles)}개의 기사를 수집했습니다. AI 분석을 시도합니다...")

                with st.spinner("Gemini 3 Flash가 보고서를 작성 중입니다. 잠시만 기다려주세요..."):
                    report = generate_report(api_key, articles)
                    
                today_str = datetime.now().strftime("%Y-%m-%d")
                save_report(today_str, report)
                
                st.success("✅ 보고서 생성 및 저장이 완료되었습니다!")
                with st.expander("생성된 보고서 미리보기"):
                    st.markdown(report)

    with tab3:
        st.subheader("일별 방문자 수 통계")
        stats = load_stats()
        
        st.metric("총 누적 접속수", stats.get("total_visits", 0))
        
        daily_visits = stats.get("daily_visits", {})
        if daily_visits:
            df = pd.DataFrame(list(daily_visits.items()), columns=["날짜", "접속수"])
            # Ensure sorting by date
            df = df.sort_values(by="날짜")
            st.line_chart(df.set_index("날짜"))
        else:
            st.info("아직 수집된 방문자 통계가 없습니다.")
