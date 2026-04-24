"""
My Tickets page component
"""
import streamlit as st
from datetime import datetime
from src.services.database import get_user_tickets


def my_tickets_page():
    """Render my tickets page"""
    st.markdown('<p class="main-header">🎫 My Tickets</p>', unsafe_allow_html=True)
    
    # Reload tickets
    st.session_state.tickets = get_user_tickets(st.session_state.user_email)
    
    if not st.session_state.tickets:
        st.info("📌 You haven't booked any tickets yet. Book your first ticket now!")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sort_by = st.selectbox("Sort by", ["Recent First", "Oldest First", "Highest Fare", "Lowest Fare"])
    
    with col2:
        route_filter = st.multiselect("Filter by Route", 
                                      options=list(set(t['route_name'] for t in st.session_state.tickets)))
    
    with col3:
        search = st.text_input("Search", placeholder="Search by ticket ID or bus name")
    
    # Apply filters
    filtered_tickets = st.session_state.tickets.copy()
    
    if route_filter:
        filtered_tickets = [t for t in filtered_tickets if t['route_name'] in route_filter]
    
    if search:
        filtered_tickets = [t for t in filtered_tickets 
                          if search.lower() in str(t['ticket_id']).lower() 
                          or search.lower() in t['bus_name'].lower()]
    
    # Apply sorting
    if sort_by == "Recent First":
        filtered_tickets = sorted(filtered_tickets, key=lambda x: x['booking_time'], reverse=True)
    elif sort_by == "Oldest First":
        filtered_tickets = sorted(filtered_tickets, key=lambda x: x['booking_time'])
    elif sort_by == "Highest Fare":
        filtered_tickets = sorted(filtered_tickets, key=lambda x: x['total_fare'], reverse=True)
    else:
        filtered_tickets = sorted(filtered_tickets, key=lambda x: x['total_fare'])
    
    st.divider()
    
    # Display tickets
    for ticket in filtered_tickets:
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"### 🎫 Ticket #{ticket['ticket_id']}")
                st.write(f"**{ticket['bus_name']}** - {ticket['route_name']}")
                st.write(f"🕐 {datetime.fromisoformat(ticket['booking_time']).strftime('%d %b %Y, %I:%M %p')}")
            
            with col2:
                st.write(f"**Journey:** {ticket['stations']}")
                st.write(f"**Distance:** {ticket['distance']} km")
                st.write(f"**Quantity:** {ticket['qty']} ticket(s)")
            
            with col3:
                st.markdown(f"### ₹{ticket['total_fare']:.2f}")
                st.write(f"💳 {ticket['payment_method']}")
            
            st.divider()