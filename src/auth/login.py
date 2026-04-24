"""
Login page component
"""
import streamlit as st
from src.services.database import login_user, get_user_tickets


def login_page():
    """Render login page"""
    st.markdown('<h1 class="main-header"> Ahmedabad BRTS</h1>', unsafe_allow_html=True)
    st.markdown('<h5 class="sub-header">Smart Travel, Seamless Journey</h5>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        
        st.markdown("### Login to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="example@email.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                submit = st.form_submit_button("Login", use_container_width=True, type="primary")
            with col_b:
                switch_to_register = st.form_submit_button("Create Account", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.error("Please enter both email and password!")
                else:
                    success, result = login_user(email, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.session_state.user_name = result['name']
                        st.session_state.tickets = get_user_tickets(email)
                        st.rerun()
                    else:
                        st.error(result)
            
            if switch_to_register:
                st.session_state.show_registration = True
                st.session_state.registration_step = 'details'
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)