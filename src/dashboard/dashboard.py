"""
Dashboard page component
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime
from src.services.database import get_user_tickets

PALETTE = ["#6C63FF", "#FF6584", "#43E97B", "#F7971E", "#4FACFE", "#FA709A", "#A18CD1", "#FBC2EB"]


def _style_fig(fig, ax):
    fig.patch.set_facecolor("#1E1E2E")
    ax.set_facecolor("#2A2A3E")
    ax.tick_params(colors="#CCCCDD", labelsize=9)
    ax.xaxis.label.set_color("#AAAACC")
    ax.yaxis.label.set_color("#AAAACC")
    ax.title.set_color("#FFFFFF")
    for spine in ax.spines.values():
        spine.set_edgecolor("#444466")


def dashboard_page():
    """Render dashboard page"""
    st.markdown(f'<p class="main-header">Welcome, {st.session_state.user_name}! 🎉</p>', unsafe_allow_html=True)

    st.session_state.tickets = get_user_tickets(st.session_state.user_email)

    total_tickets = len(st.session_state.tickets)
    total_spent = sum(t['total_fare'] for t in st.session_state.tickets)
    total_trips = sum(t['qty'] for t in st.session_state.tickets)
    avg_fare = total_spent / total_trips if total_trips > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-card"><h3>📊 Total Bookings</h3><h1>{total_tickets}</h1></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><h3>🎫 Total Tickets</h3><h1>{total_trips}</h1></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><h3>💰 Total Spent</h3><h1>₹{total_spent:.0f}</h1></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-card"><h3>📈 Avg Fare</h3><h1>₹{avg_fare:.0f}</h1></div>', unsafe_allow_html=True)

    st.divider()

    if st.session_state.tickets:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Spending by Route")
            route_spending = {}
            for t in st.session_state.tickets:
                route_spending[t['route_name']] = route_spending.get(t['route_name'], 0) + t['total_fare']

            fig, ax = plt.subplots(figsize=(8, 5))
            _style_fig(fig, ax)
            routes = list(route_spending.keys())
            amounts = list(route_spending.values())
            colors = PALETTE[:len(routes)]
            bars = ax.bar(routes, amounts, color=colors, width=0.55, zorder=3)
            ax.yaxis.grid(True, color="#444466", linestyle="--", alpha=0.6, zorder=0)
            ax.set_axisbelow(True)
            # Value labels on bars
            for bar, val in zip(bars, amounts):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(amounts) * 0.02,
                        f"₹{val:.0f}", ha='center', va='bottom', color="#FFFFFF", fontsize=8, fontweight='bold')
            ax.set_xlabel('Route', labelpad=8)
            ax.set_ylabel('Amount (₹)', labelpad=8)
            ax.set_title('Spending by Route', pad=14, fontsize=13, fontweight='bold')
            plt.xticks(rotation=30, ha='right')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        with col2:
            st.subheader("📈 Booking Trend")
            dates = [datetime.fromisoformat(t['booking_time']).date() for t in st.session_state.tickets]
            date_counts = pd.Series(dates).value_counts().sort_index()

            fig, ax = plt.subplots(figsize=(8, 5))
            _style_fig(fig, ax)
            ax.fill_between(date_counts.index, date_counts.values, alpha=0.25, color="#6C63FF")
            ax.plot(date_counts.index, date_counts.values, marker='o', linewidth=2.5,
                    markersize=8, color="#6C63FF", markerfacecolor="#FFFFFF", markeredgewidth=2)
            ax.yaxis.grid(True, color="#444466", linestyle="--", alpha=0.6)
            ax.set_axisbelow(True)
            ax.set_xlabel('Date', labelpad=8)
            ax.set_ylabel('Bookings', labelpad=8)
            ax.set_title('Booking Trend Over Time', pad=14, fontsize=13, fontweight='bold')
            plt.xticks(rotation=30, ha='right')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        st.divider()
        st.subheader("🎫 Recent Bookings")
        recent = sorted(st.session_state.tickets, key=lambda x: x['booking_time'], reverse=True)[:5]
        for ticket in recent:
            with st.expander(f"Ticket #{ticket['ticket_id']} — {ticket['bus_name']} — ₹{ticket['total_fare']}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Route:** {ticket['route_name']}")
                    st.write(f"**Quantity:** {ticket['qty']} tickets")
                    st.write(f"**Date:** {ticket['booking_time']}")
                with c2:
                    st.write(f"**Stations:** {ticket['stations']}")
                    st.write(f"**Distance:** {ticket['distance']} km")
    else:
        st.info("📌 No bookings yet. Book your first ticket!")
