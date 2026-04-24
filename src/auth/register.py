"""
Registration page component
"""
import streamlit as st
from time import time, sleep
from src.services.database import register_user, validate_email, validate_mobile
from src.services.email import generate_otp, send_otp_email_brevo, verify_otp, get_remaining_time
from src.services.database import validate_email, validate_mobile


def registration_page():
    """Render registration page"""
    st.markdown('<h1 class="main-header"> =========== Ahmedabad BRTS ===========</h1>', unsafe_allow_html=True)
    st.markdown('<h5 class="sub-header">Smart Travel, Seamless Journey</h5>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.session_state.registration_step == 'details':
            _render_registration_form()
        else:
            _render_otp_verification()
        
        st.markdown('</div>', unsafe_allow_html=True)


def _render_registration_form():
    """Render registration details form"""
    st.markdown("###  Create Your Account")
    
    with st.form("registration_form"):
        name = st.text_input("Full Name *", placeholder="Enter your full name")
        email = st.text_input("Email Address *", placeholder="example@email.com")
        phone = st.text_input("Mobile Number *", placeholder="10-digit mobile number")
        password = st.text_input("Password *", type="password", placeholder="Minimum 6 characters")
        confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password")
        
        col_a, col_b = st.columns(2)
        with col_a:
            submit = st.form_submit_button("Continue", use_container_width=True, type="primary")
        with col_b:
            switch_to_login = st.form_submit_button("Back to Login", use_container_width=True)
        
        if submit:
            # Validation
            if not all([name, email, phone, password, confirm_password]):
                st.error("All fields are required!")
            elif not validate_email(email):
                st.error("Invalid email address!")
            else:
                # Validate mobile
                mobile_valid, mobile_result = validate_mobile(phone)
                if not mobile_valid:
                    st.error(mobile_result)
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters!")
                elif password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    # Generate and send OTP directly (register_user will check for duplicates)
                    otp = generate_otp()
                    success, message = send_otp_email_brevo(email, name, otp)
                    
                    if success:
                        # Store registration data
                        st.session_state.registration_data = {
                            'name': name,
                            'email': email,
                            'phone': mobile_result,
                            'password': password
                        }
                        st.session_state.registration_step = 'otp'
                        st.session_state.otp_sent_time = time()
                        # Show OTP on screen if email couldn't be delivered
                        if message.startswith("DEMO_OTP:"):
                            demo_otp = message.split("DEMO_OTP:")[1]
                            st.session_state.demo_otp = demo_otp
                        else:
                            st.session_state.demo_otp = None
                        st.rerun()
                    else:
                        st.error(f"Failed to send OTP: {message}")
        
        if switch_to_login:
            st.session_state.show_registration = False
            st.session_state.registration_step = 'details'
            st.session_state.registration_data = {}
            st.rerun()


def _render_otp_verification():
    """Render OTP verification form"""
    st.markdown("### Email Verification")
    
    # Get remaining time
    remaining_seconds = get_remaining_time(st.session_state.registration_data['email'])
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    
    if remaining_seconds > 0:
        st.markdown(f"""
        <div class="otp-box">
            <h3 style="margin-top: 0;"> Verify Your Email</h3>
            <p style="font-size: 16px; margin: 10px 0;">
                We've sent a 6-digit OTP to<br>
                <strong>{st.session_state.registration_data['email']}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Show OTP on screen if Brevo IP is not whitelisted
        if st.session_state.get('demo_otp'):
            st.warning(f"📧 Email delivery unavailable (IP not whitelisted). Your OTP is: **{st.session_state.demo_otp}**")

        # Live countdown timer
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        timer_placeholder = st.empty()
        timer_placeholder.markdown(f"""
        <div class="timer-box">
             Time Remaining: {minutes:02d}:{seconds:02d}
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("otp_verify_form"):
            otp_input = st.text_input(
                "Enter 6-digit OTP", 
                placeholder="000000", 
                max_chars=6,
                key="otp_field"
            )
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                verify = st.form_submit_button("Verify", use_container_width=True, type="primary")
            with col_b:
                resend = st.form_submit_button("Resend OTP", use_container_width=True)
            with col_c:
                cancel = st.form_submit_button("Cancel", use_container_width=True)
            
            if verify:
                if not otp_input:
                    st.error("Please enter the OTP!")
                elif len(otp_input) != 6:
                    st.error("OTP must be 6 digits!")
                else:
                    success, message = verify_otp(st.session_state.registration_data['email'], otp_input)
                    if success:
                        # Create account
                        reg_success, reg_message = register_user(
                            st.session_state.registration_data['name'],
                            st.session_state.registration_data['email'],
                            st.session_state.registration_data['phone'],
                            st.session_state.registration_data['password']
                        )
                        
                        if reg_success:
                            st.success("Account created successfully! Please login.")
                            # Reset registration state
                            st.session_state.registration_step = 'details'
                            st.session_state.registration_data = {}
                            st.session_state.show_registration = False
                            st.rerun()
                        else:
                            st.error(reg_message)
                    else:
                        st.error(message)
            
            if resend:
                otp = generate_otp()
                success, message = send_otp_email_brevo(
                    st.session_state.registration_data['email'],
                    st.session_state.registration_data['name'],
                    otp
                )
                if success:
                    st.session_state.otp_sent_time = time()
                    if message.startswith("DEMO_OTP:"):
                        st.session_state.demo_otp = message.split("DEMO_OTP:")[1]
                        st.rerun()
                    else:
                        st.session_state.demo_otp = None
                        st.success("New OTP sent to your email!")
                        st.rerun()
                else:
                    st.error(f"Failed to resend OTP: {message}")
            
            if cancel:
                st.session_state.registration_step = 'details'
                st.session_state.registration_data = {}
                st.rerun()

        # Auto-refresh every second to keep timer live
        sleep(1)
        st.rerun()
    else:
        st.error("OTP expired! Please start registration again.")
        if st.button("Start Over", use_container_width=True):
            st.session_state.registration_step = 'details'
            st.session_state.registration_data = {}
            st.rerun()