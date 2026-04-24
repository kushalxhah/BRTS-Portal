"""
Routes page component
"""
import streamlit as st
from src.utils.constants import STATIONS, ROUTES


def routes_page():
    """Render routes page"""
    st.markdown('<p class="main-header">🗺️ BRTS Routes</p>', unsafe_allow_html=True)
    
    # Route Overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Route Statistics")
        total_routes = len(ROUTES)
        total_stations = len(STATIONS)
        
        st.metric("Total Routes", total_routes)
        st.metric("Total Stations", total_stations)
    
    with col2:
        st.subheader("🚌 Bus Lines")
        for rid, info in ROUTES.items():
            st.markdown(f"**{info['bus_name']}** - {info['route_name']}")
    
    st.divider()
    
    # Detailed Route Information
    st.subheader("🛣️ Route Details")
    
    for rid, info in ROUTES.items():
        with st.expander(f"📍 {info['route_name']} ({info['bus_name']})", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Forward Direction:**")
                stations = info['stations']
                for i, sid in enumerate(stations):
                    st.write(f"{i+1}. {STATIONS[sid]}")
                    if i < len(stations) - 1:
                        dist = info['distances'].get((sid, stations[i+1]), 0)
                        st.write(f"   ↓ {dist} km")
            
            with col2:
                st.write("**Return Direction:**")
                reverse_stations = list(reversed(stations))
                for i, sid in enumerate(reverse_stations):
                    st.write(f"{i+1}. {STATIONS[sid]}")
                    if i < len(reverse_stations) - 1:
                        next_sid = reverse_stations[i+1]
                        dist = info['distances'].get((next_sid, sid), 0)
                        st.write(f"   ↓ {dist} km")