import pandas as pd
import streamlit as st
import plotly.express as px
import os

st.set_page_config(page_title="Zayyana E-Commerce Dashboard", layout="wide")

@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "main_data.csv")
    
    if not os.path.exists(file_path):
        # Fallback jika file ada di root saat testing lokal
        file_path = "main_data.csv"
        if not os.path.exists(file_path):
            st.error(f"File tidak ditemukan.")
            return None

    df = pd.read_csv(file_path)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    return df

all_df = load_data()

# --- SIDEBAR FILTER ---
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png", width=100)
    st.title("Navigation")
    page = st.radio("Pilih Halaman:", ["Visualisasi Utama", "Analisis RFM"])
    
    st.divider()
    min_date, max_date = all_df["order_purchase_timestamp"].min().date(), all_df["order_purchase_timestamp"].max().date()
    date_range = st.date_input("Rentang Waktu", [min_date, max_date], min_value=min_date, max_value=max_date)

# Filter Data berdasarkan tanggal
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = all_df[(all_df["order_purchase_timestamp"].dt.date >= start_date) & 
                         (all_df["order_purchase_timestamp"].dt.date <= end_date)]
else:
    start_date, end_date = min_date, max_date
    filtered_df = all_df

# --- HALAMAN VISUALISASI ---
if page == "Visualisasi Utama":
    st.title("Business Intelligence Dashboard 📊")
    
    # 1. Best & Worst Products
    st.subheader("Performa Produk")
    # Menampilkan rentang waktu filter di bawah subheader
    st.markdown(f"**Periode:** {start_date} s/d {end_date}")
    
    prod_perf = filtered_df.groupby("product_category_name_english").order_id.count().sort_values(ascending=False).reset_index()
    
    col1, col2 = st.columns(2)
    with col1:
        fig_best = px.bar(prod_perf.head(5), x="order_id", y="product_category_name_english", 
                          orientation='h', title="Top 5 Kategori", color_discrete_sequence=["#72BCD4"])
        fig_best.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_best, use_container_width=True)
    
    with col2:
        fig_worst = px.bar(prod_perf.tail(5), x="order_id", y="product_category_name_english", 
                           orientation='h', title="Bottom 5 Kategori", color_discrete_sequence=["#E67E22"])
        st.plotly_chart(fig_worst, use_container_width=True)

    # 2. Revenue Trend
    st.subheader("Tren Pendapatan Bulanan")
    trend = filtered_df.resample('ME', on='order_purchase_timestamp').price.sum().reset_index()
    trend['display_month'] = trend['order_purchase_timestamp'].dt.strftime('%b %Y')
    st.plotly_chart(px.line(trend, x='display_month', y='price', markers=True, title="Total Revenue"), use_container_width=True)

# --- HALAMAN RFM ---
else:
    st.title("Customer Segmentation (RFM) 🔍")
    # Menampilkan rentang waktu filter juga di halaman RFM agar konsisten
    st.markdown(f"**Periode Analisis:** {start_date} s/d {end_date}")
    
    recent_date = filtered_df["order_purchase_timestamp"].max()
    rfm_df = filtered_df.groupby("customer_unique_id").agg({
        "order_purchase_timestamp": lambda x: (recent_date - x.max()).days,
        "order_id": "nunique",
        "price": "sum"
    }).reset_index()
    rfm_df.columns = ["customer_id", "recency", "frequency", "monetary"]
    rfm_df["short_id"] = rfm_df["customer_id"].str[:5] + "..."

    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(px.bar(rfm_df.sort_values("recency").head(5), x="short_id", y="recency", title="Recency (Days)"), use_container_width=True)
    with c2:
        st.plotly_chart(px.bar(rfm_df.sort_values("frequency", ascending=False).head(5), x="short_id", y="frequency", title="Frequency"), use_container_width=True)
    with c3:
        st.plotly_chart(px.bar(rfm_df.sort_values("monetary", ascending=False).head(5), x="short_id", y="monetary", title="Monetary"), use_container_width=True)

st.divider()
st.caption("Copyright © 2026 - Zayyana Maulida")