"""
Reports page component
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


def reports_page():
    """Render reports page"""
    st.markdown('<p class="main-header">📊 Travel Reports</p>', unsafe_allow_html=True)

    st.session_state.tickets = get_user_tickets(st.session_state.user_email)

    if not st.session_state.tickets:
        st.info("📌 No data available for reports")
        return

    period = st.selectbox("Select Period", ["This Month", "Last 3 Months", "Last 6 Months", "All Time"])
    filtered_tickets = _filter_tickets_by_period(st.session_state.tickets, period)

    if not filtered_tickets:
        st.info("No bookings in selected period")
        return

    _render_summary_stats(filtered_tickets)
    st.divider()
    _render_charts(filtered_tickets)
    st.divider()
    _render_detailed_table(filtered_tickets, period)


def _filter_tickets_by_period(tickets, period):
    now = datetime.now()
    result = []
    for t in tickets:
        d = datetime.fromisoformat(t['booking_time'])
        if period == "This Month" and d.month == now.month and d.year == now.year:
            result.append(t)
        elif period == "Last 3 Months" and (now - d).days <= 90:
            result.append(t)
        elif period == "Last 6 Months" and (now - d).days <= 180:
            result.append(t)
        elif period == "All Time":
            result.append(t)
    return result


def _render_summary_stats(filtered_tickets):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Bookings", len(filtered_tickets))
    with col2:
        st.metric("Total Tickets", sum(t['qty'] for t in filtered_tickets))
    with col3:
        st.metric("Total Spent", f"₹{sum(t['total_fare'] for t in filtered_tickets):.2f}")
    with col4:
        st.metric("Avg Fare", f"₹{np.mean([t['total_fare'] for t in filtered_tickets]):.2f}")


def _render_charts(filtered_tickets):
    col1, col2 = st.columns(2)

    # --- Donut chart: Spending by Route ---
    with col1:
        st.subheader("💰 Spending Distribution")
        route_spending = {}
        for t in filtered_tickets:
            route_spending[t['route_name']] = route_spending.get(t['route_name'], 0) + t['total_fare']

        fig, ax = plt.subplots(figsize=(7, 7))
        fig.patch.set_facecolor("#1E1E2E")
        ax.set_facecolor("#1E1E2E")
        wedges, texts, autotexts = ax.pie(
            route_spending.values(),
            labels=None,
            autopct='%1.1f%%',
            startangle=90,
            colors=PALETTE[:len(route_spending)],
            pctdistance=0.78,
            wedgeprops=dict(width=0.55, edgecolor="#1E1E2E", linewidth=2)
        )
        for at in autotexts:
            at.set_color("#FFFFFF")
            at.set_fontsize(9)
            at.set_fontweight('bold')
        # Legend
        legend_patches = [mpatches.Patch(color=PALETTE[i], label=k) for i, k in enumerate(route_spending.keys())]
        ax.legend(handles=legend_patches, loc="lower center", bbox_to_anchor=(0.5, -0.12),
                  ncol=2, frameon=False, labelcolor="#CCCCDD", fontsize=9)
        ax.set_title('Spending by Route', color="#FFFFFF", pad=16, fontsize=13, fontweight='bold')
        # Centre label
        total = sum(route_spending.values())
        ax.text(0, 0, f"₹{total:.0f}\nTotal", ha='center', va='center',
                color="#FFFFFF", fontsize=11, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # --- Horizontal bar: Bus Usage ---
    with col2:
        st.subheader("🚌 Bus Usage")
        bus_usage = {}
        for t in filtered_tickets:
            bus_usage[t['bus_name']] = bus_usage.get(t['bus_name'], 0) + t['qty']

        fig, ax = plt.subplots(figsize=(7, 7))
        _style_fig(fig, ax)
        buses = list(bus_usage.keys())
        counts = list(bus_usage.values())
        colors = PALETTE[:len(buses)]
        bars = ax.barh(buses, counts, color=colors, height=0.5, zorder=3)
        ax.xaxis.grid(True, color="#444466", linestyle="--", alpha=0.6, zorder=0)
        ax.set_axisbelow(True)
        for bar, val in zip(bars, counts):
            ax.text(bar.get_width() + max(counts) * 0.02, bar.get_y() + bar.get_height() / 2,
                    str(val), va='center', color="#FFFFFF", fontsize=9, fontweight='bold')
        ax.set_xlabel('Tickets Sold', labelpad=8)
        ax.set_title('Tickets by Bus Line', pad=14, fontsize=13, fontweight='bold')
        ax.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # --- Full-width line chart: Fare over time ---
    st.subheader("📈 Fare Trend Over Time")
    dates = [datetime.fromisoformat(t['booking_time']).date() for t in filtered_tickets]
    fares = [t['total_fare'] for t in filtered_tickets]
    df_trend = pd.DataFrame({'date': dates, 'fare': fares}).groupby('date')['fare'].sum().reset_index()

    fig, ax = plt.subplots(figsize=(12, 4))
    _style_fig(fig, ax)
    ax.fill_between(df_trend['date'], df_trend['fare'], alpha=0.2, color="#43E97B")
    ax.plot(df_trend['date'], df_trend['fare'], marker='o', linewidth=2.5,
            color="#43E97B", markersize=7, markerfacecolor="#FFFFFF", markeredgewidth=2)
    ax.yaxis.grid(True, color="#444466", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    ax.set_xlabel('Date', labelpad=8)
    ax.set_ylabel('Total Fare (₹)', labelpad=8)
    ax.set_title('Daily Fare Trend', pad=14, fontsize=13, fontweight='bold')
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def _render_detailed_table(filtered_tickets, period):
    st.subheader("📋 Detailed Ticket Report")
    df = pd.DataFrame(filtered_tickets)
    df['booking_time'] = pd.to_datetime(df['booking_time']).dt.strftime('%d %b %Y, %I:%M %p')
    display_df = df[['ticket_id', 'bus_name', 'route_name', 'qty', 'total_fare', 'distance', 'booking_time']]
    display_df.columns = ['Ticket ID', 'Bus', 'Route', 'Qty', 'Fare (₹)', 'Distance (km)', 'Date & Time']
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.divider()
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Report as CSV",
        data=csv,
        file_name=f"brts_report_{period.lower().replace(' ', '_')}.csv",
        mime="text/csv"
    )
