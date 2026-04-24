"""
Payment processing component
"""
import streamlit as st
from src.services.database import validate_upi_id, validate_card_number, validate_expiry_date, validate_cvv


def render_payment_section(total_fare):
    """Render payment section and return payment validation status and details"""
    st.subheader("💳 Payment")
    payment_method = st.radio("Select Payment Method", ["UPI", "Debit/Credit Card"])

    payment_valid = False
    payment_details = {}

    if payment_method == "UPI":
        payment_valid, payment_details = _render_upi_payment()
    elif payment_method == "Debit/Credit Card":
        payment_valid, payment_details = _render_card_payment()

    return payment_valid, payment_details, payment_method


def _render_upi_payment():
    """Render UPI payment form"""
    st.write("**📱 Enter UPI Details**")

    upi_id = st.text_input("UPI ID *", placeholder="example@upi", key="upi_input")

    if upi_id:
        if validate_upi_id(upi_id):
            st.success("✅ Valid UPI ID")
            return True, {'upi_id': upi_id}
        else:
            st.error("❌ Invalid UPI ID format. Must contain '@upi'")

    st.caption("💡 Example: yourname@upi, 9876543210@upi")
    return False, {}


def _render_card_payment():
    """Render card payment form"""
    st.write("**💳 Enter Card Details**")

    card_number = st.text_input("Card Number *", placeholder="XXXX XXXX XXXX XXXX", max_chars=19, key="card_input")

    col_a, col_b = st.columns(2)
    with col_a:
        expiry_date = st.text_input("Expiry Date *", placeholder="MM/YY", max_chars=5, key="exp_input")
    with col_b:
        cvv = st.text_input("CVV *", placeholder="XXX", max_chars=4, type="password", key="cvv_input")

    card_valid = exp_valid = cvv_valid = False

    if card_number:
        if validate_card_number(card_number):
            card_valid = True
        else:
            st.error("❌ Invalid card number")

    if expiry_date:
        if validate_expiry_date(expiry_date):
            exp_valid = True
        else:
            st.error("❌ Invalid or expired date")

    if cvv:
        if validate_cvv(cvv):
            cvv_valid = True
        else:
            st.error("❌ Invalid CVV")

    if card_valid and exp_valid and cvv_valid:
        st.success("✅ Card details validated")
        masked_card = "**** **** **** " + card_number.replace(" ", "")[-4:]
        return True, {'card_number': masked_card, 'expiry_date': expiry_date}

    st.caption("🔒 Your card details are secure and encrypted")
    return False, {}
