import pandas as pd
import plotly.express as px
import streamlit as st
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="E-Commerce Insights", layout="wide")

# --- CUSTOM CSS UNTUK TAMPILAN MODERN ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div.block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    file_path = "dashboard/main_data.csv" if os.path.exists("dashboard/main_data.csv") else "main_data.csv"
    if not os.path.exists(file_path):
        st.error("File data tidak ditemukan!")
        return None
    
    df = pd.read_csv(file_path)
    datetime_cols = ["order_purchase_timestamp", "order_delivered_customer_date"]
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df

all_df = load_data()

if all_df is not None:
    # --- SIDEBAR - FILTER INTERAKTIF (KRITERIA 4) ---
    with st.sidebar:
        st.title("📊 Filter Dashboard")
        
        # 1. Filter Rentang Tanggal
        min_date = all_df["order_purchase_timestamp"].min().date()
        max_date = all_df["order_purchase_timestamp"].max().date()
        start_date, end_date = st.date_input("Rentang Waktu", [min_date, max_date])

        # 2. Filter Kategori (Interactiveness)
        cat_col = "product_category_name_english" if "product_category_name_english" in all_df.columns else "product_category_name"
        all_cats = sorted(all_df[cat_col].dropna().unique())
        selected_cats = st.multiselect("Pilih Kategori Produk", all_cats, default=all_cats[:5])

        # 3. Filter Negara Bagian/State
        all_states = sorted(all_df["customer_state"].unique())
        selected_states = st.multiselect("Pilih Wilayah (State)", all_states, default=all_states)

    # --- APPLY FILTERS (KRITERIA 4 - Mempengaruhi data mentah) ---
    filtered_df = all_df[
        (all_df["order_purchase_timestamp"].dt.date >= start_date) &
        (all_df["order_purchase_timestamp"].dt.date <= end_date) &
        (all_df[cat_col].isin(selected_cats)) &
        (all_df["customer_state"].isin(selected_states))
    ].copy()

    # --- HEADER ---
    st.title("E-Commerce Business Intelligence")
    st.markdown(f"Menganalisis performa dari **{start_date}** sampai **{end_date}**")

    # --- RINGKASAN METRIK ---
    col1, col2, col3 = st.columns(3)
    with col1:
        total_rev = filtered_df["price"].sum()
        st.metric("Total Revenue", f"R$ {total_rev:,.0f}")
    with col2:
        total_orders = filtered_df["order_id"].nunique()
        st.metric("Total Orders", f"{total_orders:,}")
    with col3:
        avg_price = filtered_df["price"].mean()
        st.metric("Avg Order Value", f"R$ {avg_price:.2f}")

    st.divider()

    # --- VISUALISASI 1: PERFORMA PRODUK (Menjawab Pertanyaan Bisnis 1) ---
    st.subheader("Produk Kategori Paling Banyak & Sedikit Terjual")
    
    prod_perf = filtered_df.groupby(cat_col).order_id.count().sort_values(ascending=False).reset_index()
    prod_perf.columns = ['Category', 'Sales']

    tab1, tab2 = st.tabs(["Top 5", "Bottom 5"])
    with tab1:
        fig_top = px.bar(prod_perf.head(5), x='Sales', y='Category', orientation='h',
                         color='Sales', color_continuous_scale='Blues',
                         template='minimal')
        fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig_top, use_container_width=True)
    with tab2:
        fig_low = px.bar(prod_perf.tail(5), x='Sales', y='Category', orientation='h',
                         color='Sales', color_continuous_scale='Reds',
                         template='minimal')
        fig_low.update_layout(yaxis={'categoryorder':'total descending'}, showlegend=False)
        st.plotly_chart(fig_low, use_container_width=True)

    # --- VISUALISASI 2: TREN REVENUE (Menjawab Pertanyaan Bisnis 2) ---
    st.subheader("Tren Pendapatan Bulanan")
    
    # Resample bulanan dari filtered_df
    revenue_trend = filtered_df.set_index("order_purchase_timestamp").resample("ME").agg({"price": "sum"}).reset_index()
    revenue_trend.rename(columns={"price": "Revenue"}, inplace=True)

    fig_trend = px.line(revenue_trend, x="order_purchase_timestamp", y="Revenue",
                        markers=True, line_shape="spline",
                        template='minimal', labels={'order_purchase_timestamp': 'Bulan'})
    fig_trend.update_traces(line_color='#2c7be5', line_width=3)
    st.plotly_chart(fig_trend, use_container_width=True)

    # --- FOOTER ---
    st.caption(f"© 2024 Zayyana Maulida | Dicoding Data Analysis Project. Data rows filtered: {len(filtered_df):,}")