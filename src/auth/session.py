"""
Authentication utilities
"""
import streamlit as st


def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'tickets' not in st.session_state:
        st.session_state.tickets = {}
    if 'registration_step' not in st.session_state:
        st.session_state.registration_step = 'details'  # 'details' or 'otp'
    if 'registration_data' not in st.session_state:
        st.session_state.registration_data = {}
    if 'otp_sent_time' not in st.session_state:
        st.session_state.otp_sent_time = None
    if 'show_registration' not in st.session_state:
        st.session_state.show_registration = False


def logout():
    """Logout user and clear session"""
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.tickets = {}
    st.session_state.registration_step = 'details'
    st.session_state.registration_data = {}
    st.session_state.show_registration = False