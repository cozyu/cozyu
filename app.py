import streamlit as st
from datetime import datetime
from github_storage import increment_stat

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
        today_str = datetime.now().strftime("%Y-%m-%d")
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

# Navigation
st.sidebar.title("🧭 내비게이션")
menu = st.sidebar.radio("이동", ["📰 뉴스룸", "⚙️ 관리자 설정"])

if menu == "📰 뉴스룸":
    show_main_page()
elif menu == "⚙️ 관리자 설정":
    show_admin_page()
