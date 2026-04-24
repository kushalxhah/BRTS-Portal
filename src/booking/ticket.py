"""
Ticket booking page component
"""
import streamlit as st
import random
from datetime import datetime
from src.utils.constants import STATIONS, ROUTES
from src.utils.helpers import find_routes, find_routes_with_transfer, find_routes_from_nearby, calculate_fare
from src.booking.payment import render_payment_section
from src.services.database import get_user_tickets, save_user_ticket


def book_ticket_page():
    """Render ticket booking page"""
    st.markdown('<p class="main-header">🎫 Book Your Ticket</p>', unsafe_allow_html=True)

    # Reset payment confirmation on page load
    if 'payment_confirmed' not in st.session_state:
        st.session_state.payment_confirmed = False
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Select Journey Details")
        
        # Station Selection with default option
        station_options = {0: "🚉 Select your station"}
        station_options.update({sid: f"[{sid}] {name}" for sid, name in STATIONS.items()})
        
        start_station = st.selectbox(
            "Boarding Station",
            options=[0] + list(STATIONS.keys()),
            format_func=lambda x: station_options[x],
            index=0  # Default to "Select your station"
        )
        
        end_station = st.selectbox(
            "Destination Station",
            options=[0] + list(STATIONS.keys()),
            format_func=lambda x: station_options[x],
            index=0  # Default to "Select your station"
        )
        
        # Check if stations are not selected
        if start_station == 0 or end_station == 0:
            return
        
        # Show warning message prominently when stations are same
        if start_station == end_station:
            st.markdown("""
            <div class="no-route-alert">
                <h3>⚠️ Invalid Selection</h3>
                <p><strong>Boarding and Destination stations cannot be the same.</strong></p>
                <p>Please select different stations to continue.</p>
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Find available routes
        available_routes = find_routes(start_station, end_station)
        
        if not available_routes:
            _render_no_direct_routes(start_station, end_station)
            return
        
        # Route selection
        route_options = {rid: f"{ROUTES[rid]['route_name']} ({ROUTES[rid]['bus_name']})" 
                        for rid in available_routes}
        
        selected_route = st.selectbox(
            "Select Route",
            options=available_routes,
            format_func=lambda x: route_options[x]
        )
        
        quantity = st.number_input("Number of Tickets", min_value=1, max_value=10, value=1)
        
        # Calculate fare
        distance, fare_per, total_fare = calculate_fare(selected_route, start_station, end_station, quantity)
    
    with col2:
        _render_booking_summary(selected_route, start_station, end_station, quantity, distance, fare_per, total_fare)


def _render_no_direct_routes(start_station, end_station):
    """Render alternative route options when no direct route is available"""
    st.markdown(f"""
    <div class="no-route-alert">
        <h3>❌ No Direct Bus Available</h3>
        <p><strong>From:</strong> {STATIONS[start_station]}</p>
        <p><strong>To:</strong> {STATIONS[end_station]}</p>
        <p>Please check alternative routes below or select different stations.</p>
    </div>
    """, unsafe_allow_html=True)

    transfer_routes = find_routes_with_transfer(start_station, end_station)
    alternative_routes = find_routes_from_nearby(start_station, end_station, max_distance_km=5.0)

    if transfer_routes:
        st.markdown("---")
        st.markdown("### 🔄 Routes with Bus Change")
        st.success(f"✅ Found {len(transfer_routes)} route(s) with one bus change!")
        st.info("💡 You will need to change buses at a transfer station")

        for idx, tr in enumerate(transfer_routes[:5], 1):
            st.markdown(f"""
            <div class="transfer-route-card">
                <h4>Option {idx}: {tr['bus1_name']} ➜ {tr['bus2_name']}</h4>
                <p><strong>📍 Leg 1:</strong> Take <strong>{tr['bus1_name']}</strong> from <strong>{STATIONS[start_station]}</strong></p>
                <p style="margin-left: 20px;">🛣️ Route: {tr['route1_name']}</p>
                <p style="margin-left: 20px;">📏 Distance: {tr['leg1_distance']} km</p>
                <div class="transfer-station-badge">🔄 Change at: {STATIONS[tr['transfer_station']]}</div>
                <p><strong>📍 Leg 2:</strong> Take <strong>{tr['bus2_name']}</strong> to <strong>{STATIONS[end_station]}</strong></p>
                <p style="margin-left: 20px;">🛣️ Route: {tr['route2_name']}</p>
                <p style="margin-left: 20px;">📏 Distance: {tr['leg2_distance']} km</p>
                <p><strong>💰 Total Distance:</strong> {tr['total_distance']} km (Estimated Fare: ₹{tr['total_distance'] * 5:.2f})</p>
            </div>
            """, unsafe_allow_html=True)
        st.divider()

    if alternative_routes:
        st.markdown("### 📍 Nearby Stations with Direct Routes")
        st.success(f"✅ Found {len(alternative_routes)} alternative route(s) from nearby stations within 5 km!")
        st.info("💡 You can walk to these nearby stations to catch a direct bus")

        for alt in alternative_routes[:5]:
            nearby = alt['nearby_station']
            st.markdown(f"""
            <div class="nearby-station-card">
                <h4>🚶 {nearby['station_name']} (Station {nearby['station_id']})</h4>
                <p><strong>📏 Distance from {STATIONS[start_station]}:</strong> {nearby['distance_km']} km (~{int(nearby['distance_km'] * 12)} min walk)</p>
                <p><strong>🚌 Available Bus:</strong> {alt['bus_name']}</p>
                <p><strong>🛣️ Route:</strong> {alt['route_name']}</p>
            </div>
            """, unsafe_allow_html=True)
        st.divider()

    if not transfer_routes and not alternative_routes:
        st.info("💡 No alternative routes found. Try selecting different stations.")


def _render_booking_summary(selected_route, start_station, end_station, quantity, distance, fare_per, total_fare):
    """Render booking summary and payment section"""
    st.subheader("Booking Summary")
    
    route_info = ROUTES[selected_route]
    stations_on_route = route_info['stations']
    start_idx = stations_on_route.index(start_station)
    end_idx = stations_on_route.index(end_station)
    journey_stations = stations_on_route[start_idx:end_idx+1]
    
    st.info(f"""
    **Route:** {route_info['route_name']}  
    **Bus:** {route_info['bus_name']}  
    **Distance:** {distance} km  
    **Fare per Ticket:** ₹{fare_per:.2f}  
    **Quantity:** {quantity}  
    **Total Fare:** ₹{total_fare:.2f}
    """)
    
    st.write("**Journey Path:**")
    journey_path = " → ".join([f"{STATIONS[sid]}" for sid in journey_stations])
    st.success(journey_path)
    
    st.divider()
    
    # Payment Section
    payment_valid, payment_details, payment_method = render_payment_section(total_fare)
    
    st.divider()
    
    # Confirm Payment Button
    if st.button(f"🔒 Confirm & Pay ₹{total_fare:.2f}", use_container_width=True, type="primary", disabled=not payment_valid):
        _process_payment(route_info, journey_stations, quantity, total_fare, distance, payment_method, payment_details)


def _process_payment(route_info, journey_stations, quantity, total_fare, distance, payment_method, payment_details):
    """Process payment and create ticket"""
    # Create ticket
    user_tickets = get_user_tickets(st.session_state.user_email)
    ticket_id = len(user_tickets) + 1
    
    station_path = " → ".join([f"[{sid}] {STATIONS[sid]}" for sid in journey_stations])
    
    ticket = {
        'ticket_id': ticket_id,
        'route_name': route_info['route_name'],
        'bus_name': route_info['bus_name'],
        'stations': station_path,
        'qty': quantity,
        'total_fare': total_fare,
        'distance': distance,
        'booking_time': datetime.now().isoformat(),
        'payment_method': payment_method,
        'payment_details': payment_details,
        'transaction_id': f"TXN{random.randint(100000, 999999)}"
    }
    
    # Save ticket to database
    save_user_ticket(st.session_state.user_email, ticket)
    
    # Update session state
    st.session_state.tickets = get_user_tickets(st.session_state.user_email)
    st.session_state.payment_confirmed = False

    st.success(f"""
    ✅ **Payment Successful!**  
    Ticket ID: #{ticket_id}  
    Transaction ID: {ticket['transaction_id']}
    """)