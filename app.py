import streamlit as st
from config.settings import APP_TITLE, APP_ICON, PAGE_LAYOUT
from src.auth.session import init_session_state, logout
from src.auth.login import login_page
from src.auth.register import registration_page
from src.dashboard.dashboard import dashboard_page
from src.booking.ticket import book_ticket_page
from src.dashboard.tickets import my_tickets_page
from src.booking.routes import routes_page
from src.dashboard.reports import reports_page


st.set_page_config(
    page_title=APP_TITLE,
    layout=PAGE_LAYOUT,
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    """Load custom CSS styles"""
    try:
        with open('static/css/styles.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # CSS file not found, continue without custom styles
        pass

# Initialize session state
init_session_state()

# Load CSS
load_css()


def main():
    """Main application function"""
    
    # Authentication flow
    if not st.session_state.logged_in:
        if st.session_state.get('show_registration', False):
            registration_page()
        else:
            login_page()
        return
    
    # Main application for logged-in users
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.user_name}! 👋")
        st.divider()
        
        # Navigation
        page = st.selectbox(
            "Navigate to:",
            ["Dashboard", "Book Ticket", "My Tickets", "Routes", "Reports"]
        )
        
        st.divider()
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
    
    # Page routing
    if page == "Dashboard":
        dashboard_page()
    elif page == "Book Ticket":
        book_ticket_page()
    elif page == "My Tickets":
        my_tickets_page()
    elif page == "Routes":
        routes_page()
    else:
        reports_page()


if __name__ == "__main__":
    main()