import streamlit as st
from datetime import datetime, timezone, timedelta
from github_storage import increment_stat
import subprocess
import os

KST = timezone(timedelta(hours=9))

def get_latest_git_commit_date_kst():
    try:
        env = os.environ.copy()
        env['TZ'] = 'Asia/Seoul'
        git_date = subprocess.check_output(
            ['git', 'log', '-1', '--date=format-local:%Y-%m-%d %H:%M:%S', '--format=%cd'],
            env=env
        ).decode('utf-8').strip()
        return git_date
    except Exception:
        return None

# Set up page config
st.set_page_config(
    page_title="AI-Powered IT Newsroom",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Only increment visit stats once per session
if "visited" not in st.session_state:
    st.session_state.visited = True
    try:
        today_str = datetime.now(KST).strftime("%Y-%m-%d")
        increment_stat(today_str)
    except Exception as e:
        print(f"Failed to increment stats: {e}")

# Import views
from views.main_page import show_main_page
from views.admin_page import show_admin_page

# Custom CSS for Markdown rendering (dark/light mode compatible)
st.markdown("""
<style>
    /* Better markdown rendering for the reports */
    .stMarkdown p {
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Git update date at the top of sidebar
git_date = get_latest_git_commit_date_kst()
if git_date:
    st.sidebar.markdown(
        f"<div style='font-size: 0.8em; color: gray; margin-bottom: 10px;'>최종 업데이트: {git_date}</div>", 
        unsafe_allow_html=True
    )

# Navigation
st.sidebar.title("🧭 내비게이션")
menu = st.sidebar.radio("이동", ["📰 뉴스룸", "⚙️ 관리자 설정"])

if menu == "📰 뉴스룸":
    show_main_page()
elif menu == "⚙️ 관리자 설정":
    show_admin_page()
