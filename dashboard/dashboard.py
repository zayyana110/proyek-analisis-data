import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st
import os

st.set_page_config(page_title="E-Commerce Business Intelligence", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div.block-container { padding-top: 2rem; }
    .sidebar-img { display: flex; justify-content: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_path = "dashboard/main_data.csv" if os.path.exists("dashboard/main_data.csv") else "main_data.csv"
    
    df = pd.read_csv(file_path, sep=None, engine='python', skipinitialspace=True)
    
    df.columns = df.columns.str.strip()
    
    datetime_cols = [
        "order_purchase_timestamp", 
        "order_delivered_customer_date"
    ]
    
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
    return df

all_df = load_data()

if 'page' not in st.session_state:
    st.session_state.page = "📊 Visualisasi Data"

if all_df is not None:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-img">
                <img src="https://github.com/dicodingacademy/assets/raw/main/logo.png" width="150">
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.title("Main Menu")
        
        if st.button("📊 Visualisasi Data", use_container_width=True, 
                     type="primary" if st.session_state.page == "📊 Visualisasi Data" else "secondary"):
            st.session_state.page = "📊 Visualisasi Data"
            st.rerun()
        
        if st.button("🔍 Analisis Lanjutan (RFM)", use_container_width=True,
                     type="primary" if st.session_state.page == "🔍 Analisis Lanjutan (RFM)" else "secondary"):
            st.session_state.page = "🔍 Analisis Lanjutan (RFM)"
            st.rerun()

        st.markdown("---")
        
        st.subheader("Filter Global")
        min_date = all_df["order_purchase_timestamp"].min().date()
        max_date = all_df["order_purchase_timestamp"].max().date()
        
        start_date, end_date = st.date_input("Rentang Waktu", [min_date, max_date])
        
        cat_col = "product_category_name_english" if "product_category_name_english" in all_df.columns else "product_category_name"
        all_cats = sorted(all_df[cat_col].dropna().unique())
        selected_cats = st.multiselect("Kategori Produk", all_cats, default=all_cats[:5])

    filtered_df = all_df[
        (all_df["order_purchase_timestamp"].dt.date >= start_date) &
        (all_df["order_purchase_timestamp"].dt.date <= end_date) &
        (all_df[cat_col].isin(selected_cats))
    ].copy()


    if st.session_state.page == "📊 Visualisasi Data":
        st.title("E-Commerce Business Intelligence 📊")
        st.markdown(f"Menampilkan performa data dari **{start_date}** hingga **{end_date}**")

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Total Revenue", f"R$ {filtered_df['price'].sum():,.0f}")
        with m2:
            st.metric("Total Orders", f"{filtered_df['order_id'].nunique():,}")
        with m3:
            st.metric("Avg Review Score", f"{filtered_df['review_score'].mean():.2f} ⭐" if 'review_score' in filtered_df.columns else "N/A")

        st.divider()

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Best Performing Product")
            prod_perf = filtered_df.groupby(cat_col).order_id.count().sort_values(ascending=False).reset_index().head(5)
            fig_top = px.bar(prod_perf, x='order_id', y=cat_col, orientation='h',
                             labels={'order_id': 'Sales', cat_col: 'Category'},
                             color='order_id', color_continuous_scale='Blues')
            fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
            st.plotly_chart(fig_top, use_container_width=True)

        with col2:
            st.markdown("### Worst Performing Product")
            worst_perf = filtered_df.groupby(cat_col).order_id.count().sort_values(ascending=True).reset_index().head(5)
            fig_worst = px.bar(worst_perf, x='order_id', y=cat_col, orientation='h',
                               labels={'order_id': 'Sales', cat_col: 'Category'},
                               color='order_id', color_continuous_scale='Reds')
            fig_worst.update_layout(yaxis={'categoryorder':'total descending'}, showlegend=False)
            st.plotly_chart(fig_worst, use_container_width=True)

        st.markdown("### Tren Pendapatan Bulanan")
        revenue_trend = filtered_df.set_index("order_purchase_timestamp").resample("ME").agg({"price": "sum"}).reset_index()
        fig_trend = px.line(revenue_trend, x="order_purchase_timestamp", y="price",
                            markers=True, line_shape="spline", template='minimal')
        fig_trend.update_traces(line_color='#2c7be5', line_width=3)
        st.plotly_chart(fig_trend, use_container_width=True)

    elif st.session_state.page == "🔍 Analisis Lanjutan (RFM)":
        st.title("Customer Segmentation (RFM Analysis) 🔍")
        
        rfm_df = filtered_df.groupby(by="customer_unique_id", as_index=False).agg({
            "order_purchase_timestamp": "max",
            "order_id": "nunique",
            "price": "sum"
        })
        rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
        recent_date = filtered_df["order_purchase_timestamp"].max()
        rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Top Customers by Recency")
            top_recency = rfm_df.sort_values(by="recency", ascending=True).head(5)
            fig_rec = px.bar(top_recency, x="recency", y="customer_id", orientation='h', color_discrete_sequence=['#72BCD4'])
            st.plotly_chart(fig_rec, use_container_width=True)

        with col2:
            st.markdown("#### Top Customers by Frequency")
            top_freq = rfm_df.sort_values(by="frequency", ascending=False).head(5)
            fig_freq = px.bar(top_freq, x="frequency", y="customer_id", orientation='h', color_discrete_sequence=['#72BCD4'])
            st.plotly_chart(fig_freq, use_container_width=True)

        with col3:
            st.markdown("#### Top Customers by Monetary")
            top_mon = rfm_df.sort_values(by="monetary", ascending=False).head(5)
            fig_mon = px.bar(top_mon, x="monetary", y="customer_id", orientation='h', color_discrete_sequence=['#72BCD4'])
            st.plotly_chart(fig_mon, use_container_width=True)

    st.caption(f"Copyright © 2026 Zayyana Maulida | Dashboard Rows: {len(filtered_df):,}")