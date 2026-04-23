import pandas as pd
import streamlit as st
import plotly.express as px
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="E-Commerce BI Dashboard", layout="wide")

@st.cache_data
def load_data():
    file_path = "dashboard/main_data.csv" if os.path.exists("dashboard/main_data.csv") else "main_data.csv"
    if not os.path.exists(file_path):
        return None

    df = pd.read_csv(file_path, encoding='utf-8')
    df.columns = df.columns.str.strip().str.replace('"', '').str.replace("'", "")
    
    datetime_cols = ["order_purchase_timestamp", "order_delivered_customer_date"]
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
    return df

all_df = load_data()

if all_df is None:
    st.error("File data tidak ditemukan.")
    st.stop()

# --- SIDEBAR ---
if 'page' not in st.session_state:
    st.session_state.page = "📊 Visualisasi Data"

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png", width=150)
    st.title("Main Menu")
    if st.button("📊 Visualisasi Data", use_container_width=True):
        st.session_state.page = "📊 Visualisasi Data"
    if st.button("🔍 Analisis Lanjutan (RFM)", use_container_width=True):
        st.session_state.page = "🔍 Analisis Lanjutan (RFM)"

    st.divider()
    st.subheader("Filter Global")
    min_date, max_date = all_df["order_purchase_timestamp"].min().date(), all_df["order_purchase_timestamp"].max().date()
    
    # Perbaikan date_input agar tidak error saat user klik
    date_res = st.date_input("Rentang Waktu", [min_date, max_date], min_value=min_date, max_value=max_date)
    
    # Filter Kategori
    cat_col = "product_category_name_english" if "product_category_name_english" in all_df.columns else "product_category_name"
    all_cats = sorted(all_df[cat_col].dropna().unique())
    selected_cats = st.multiselect("Kategori Produk", all_cats, default=all_cats[:5])

# --- PROSES FILTER DATA ---
if isinstance(date_res, list) and len(date_res) == 2:
    start_date, end_date = date_res
else:
    start_date, end_date = min_date, max_date

filtered_df = all_df[
    (all_df["order_purchase_timestamp"].dt.date >= start_date) &
    (all_df["order_purchase_timestamp"].dt.date <= end_date) &
    (all_df[cat_col].isin(selected_cats))
].copy()

# --- HALAMAN 1: VISUALISASI DATA ---
if st.session_state.page == "📊 Visualisasi Data":
    st.title("E-Commerce Business Intelligence 📊")
    
    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Revenue", f"R$ {filtered_df['price'].sum():,.0f}")
    m2.metric("Total Orders", f"{filtered_df['order_id'].nunique():,}")
    m3.metric("Avg Review Score", f"{filtered_df['review_score'].mean():.2f} ⭐" if 'review_score' in filtered_df.columns else "0 ⭐")

    st.divider()

    # Logika Best & Worst (Sesuai Notebook)
    st.subheader("Best and Worst Performing Product by Number of Sales")
    col1, col2 = st.columns(2)
    
    # Hitung jumlah produk (Sesuai sum_order_items_df di notebook)
    sum_order_items_df = filtered_df.groupby(cat_col).order_id.count().reset_index()
    sum_order_items_df.rename(columns={"order_id": "product_id_count"}, inplace=True)

    with col1:
        top_5 = sum_order_items_df.sort_values(by="product_id_count", ascending=False).head(5)
        fig_best = px.bar(top_5, x="product_id_count", y=cat_col, orientation='h',
                          title="Best Performing Product", color_discrete_sequence=["#72BCD4"])
        fig_best.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_best, use_container_width=True)

    with col2:
        worst_5 = sum_order_items_df.sort_values(by="product_id_count", ascending=True).head(5)
        fig_worst = px.bar(worst_5, x="product_id_count", y=cat_col, orientation='h',
                           title="Worst Performing Product", color_discrete_sequence=["#72BCD4"])
        fig_worst.update_layout(yaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig_worst, use_container_width=True)

    # Tren Pendapatan (Sesuai monthly_revenue_df di notebook)
    st.subheader("Total Revenue per Month")
    revenue_trend = filtered_df.set_index("order_purchase_timestamp").resample("ME").agg({"price": "sum"}).reset_index()
    # Format x-axis agar sama seperti strftime('%B %Y') di notebook
    revenue_trend["display_month"] = revenue_trend["order_purchase_timestamp"].dt.strftime('%B %Y')
    
    fig_trend = px.line(revenue_trend, x="display_month", y="price", markers=True,
                        color_discrete_sequence=["#72BCD4"])
    st.plotly_chart(fig_trend, use_container_width=True)

# --- HALAMAN 2: RFM ANALYSIS ---
elif st.session_state.page == "🔍 Analisis Lanjutan (RFM)":
    st.title("Customer Segmentation (RFM Analysis) 🔍")
    
    rfm_df = filtered_df.groupby("customer_unique_id").agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "price": "sum"
    }).reset_index()
    
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    recent_date = filtered_df["order_purchase_timestamp"].max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

    # Visualisasi RFM (Sesuai Notebook: Bar vertikal dengan Customer ID di sumbu X)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### By Recency (days)")
        top_rec = rfm_df.sort_values("recency", ascending=True).head(5)
        st.plotly_chart(px.bar(top_rec, x="customer_id", y="recency", color_discrete_sequence=["#72BCD4"]), use_container_width=True)

    with col2:
        st.markdown("#### By Frequency")
        top_freq = rfm_df.sort_values("frequency", ascending=False).head(5)
        st.plotly_chart(px.bar(top_freq, x="customer_id", y="frequency", color_discrete_sequence=["#72BCD4"]), use_container_width=True)

    with col3:
        st.markdown("#### By Monetary")
        top_mon = rfm_df.sort_values("monetary", ascending=False).head(5)
        st.plotly_chart(px.bar(top_mon, x="customer_id", y="monetary", color_discrete_sequence=["#72BCD4"]), use_container_width=True)

st.divider()
st.caption(f"Copyright © 2026 Zayyana Maulida | Dashboard Rows: {len(filtered_df):,}")