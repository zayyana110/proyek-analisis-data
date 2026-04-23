import pandas as pd
import streamlit as st
import plotly.express as px
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="E-Commerce BI Dashboard", layout="wide")

# Styling CSS untuk tampilan yang lebih profesional
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #e0e0e0;
    }
    div.block-container { padding-top: 2rem; }
    .sidebar-img { display: flex; justify-content: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    # Tentukan path file
    file_path = "dashboard/main_data.csv" if os.path.exists("dashboard/main_data.csv") else "main_data.csv"
    
    if not os.path.exists(file_path):
        st.error(f"File {file_path} tidak ditemukan!")
        return None

    # Gunakan encoding='utf-8' atau 'latin1' untuk menghindari karakter aneh
    df = pd.read_csv(file_path, encoding='utf-8')
    
    # --- LANGKAH KRUSIAL: MEMBERSIHKAN NAMA KOLOM ---
    # Terkadang ada karakter tersembunyi (BOM) di awal file CSV
    df.columns = df.columns.str.strip().str.replace('"', '').str.replace("'", "")
    
    # Konversi ke datetime dengan penanganan error
    if "order_purchase_timestamp" in df.columns:
        df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"], errors='coerce')
    else:
        # Jika masih error, kita tampilkan list kolom yang terbaca agar tahu masalahnya
        st.error("Kolom 'order_purchase_timestamp' tetap tidak ditemukan!")
        st.write("Kolom yang tersedia di file kamu:", df.columns.tolist())
        st.stop()

    if "order_delivered_customer_date" in df.columns:
        df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"], errors='coerce')
            
    return df

# --- INISIALISASI HALAMAN ---
if 'page' not in st.session_state:
    st.session_state.page = "📊 Visualisasi Data"

all_df = load_data()

# Pastikan df tidak None dan kolom tersedia sebelum lanjut ke filter sidebar
if all_df is not None:
    # Filter tanggal hanya jalan jika data tersedia
    try:
        min_date = all_df["order_purchase_timestamp"].min().date()
        max_date = all_df["order_purchase_timestamp"].max().date()
    except Exception as e:
        st.error(f"Gagal mengambil rentang tanggal: {e}")
        st.stop()
# --- MAIN LOGIC ---
all_df = load_data()

if all_df is None:
    st.error("File data tidak ditemukan atau rusak. Pastikan 'main_data.csv' tersedia.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<div class="sidebar-img"><img src="https://github.com/dicodingacademy/assets/raw/main/logo.png" width="150"></div>', unsafe_allow_html=True)
    st.title("Main Menu")
    
    # Navigasi menggunakan Tombol
    if st.button("📊 Visualisasi Data", use_container_width=True):
        st.session_state.page = "📊 Visualisasi Data"
    if st.button("🔍 Analisis Lanjutan (RFM)", use_container_width=True):
        st.session_state.page = "🔍 Analisis Lanjutan (RFM)"

    st.divider()
    st.subheader("Filter Global")
    
    # Filter Rentang Waktu
    min_date = all_df["order_purchase_timestamp"].min().date()
    max_date = all_df["order_purchase_timestamp"].max().date()
    
    date_range = st.date_input("Rentang Waktu", [min_date, max_date], min_value=min_date, max_value=max_date)
    
    # Filter Kategori
    cat_col = "product_category_name_english" if "product_category_name_english" in all_df.columns else "product_category_name"
    all_cats = sorted(all_df[cat_col].dropna().unique())
    selected_cats = st.multiselect("Kategori Produk", all_cats, default=all_cats[:5])

# --- FILTERING DATA ---
# Proteksi jika user hanya memilih satu tanggal atau menghapus filter tanggal
if isinstance(date_range, list) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered_df = all_df[
    (all_df["order_purchase_timestamp"].dt.date >= start_date) &
    (all_df["order_purchase_timestamp"].dt.date <= end_date) &
    (all_df[cat_col].isin(selected_cats))
].copy()

# --- PAGE 1: VISUALISASI DATA ---
if st.session_state.page == "📊 Visualisasi Data":
    st.title("E-Commerce Business Intelligence 📊")
    st.info(f"Menampilkan performa dari **{start_date}** sampai **{end_date}**")

    # Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Revenue", f"R$ {filtered_df['price'].sum():,.0f}")
    with m2:
        st.metric("Total Orders", f"{filtered_df['order_id'].nunique():,}")
    with m3:
        avg_score = filtered_df['review_score'].mean() if 'review_score' in filtered_df.columns else 0
        st.metric("Avg Review Score", f"{avg_score:.2f} ⭐")

    st.divider()

    # Bar Charts
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Top 5 Kategori Produk")
        prod_perf = filtered_df.groupby(cat_col).order_id.count().nlargest(5).reset_index()
        fig_top = px.bar(prod_perf, x='order_id', y=cat_col, orientation='h', 
                         color='order_id', color_continuous_scale='Blues', labels={'order_id':'Orders'})
        fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig_top, use_container_width=True)

    with col2:
        st.markdown("### Bottom 5 Kategori Produk")
        worst_perf = filtered_df.groupby(cat_col).order_id.count().nsmallest(5).reset_index()
        fig_worst = px.bar(worst_perf, x='order_id', y=cat_col, orientation='h', 
                           color='order_id', color_continuous_scale='Reds', labels={'order_id':'Orders'})
        fig_worst.update_layout(yaxis={'categoryorder':'total descending'}, showlegend=False)
        st.plotly_chart(fig_worst, use_container_width=True)

    # Trend Chart
    st.markdown("### Tren Pendapatan Bulanan")
    revenue_trend = filtered_df.set_index("order_purchase_timestamp").resample("ME").agg({"price": "sum"}).reset_index()
    fig_trend = px.line(revenue_trend, x="order_purchase_timestamp", y="price", markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)

# --- PAGE 2: RFM ANALYSIS ---
elif st.session_state.page == "🔍 Analisis Lanjutan (RFM)":
    st.title("Customer Segmentation (RFM Analysis) 🔍")
    
    # Aggregating RFM
    rfm_df = filtered_df.groupby("customer_unique_id").agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "price": "sum"
    }).reset_index()
    
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    recent_date = filtered_df["order_purchase_timestamp"].max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Top Recency (Days)")
        top_rec = rfm_df.nsmallest(5, 'recency')
        st.plotly_chart(px.bar(top_rec, x="recency", y="customer_id", orientation='h', color_discrete_sequence=['#72BCD4']), use_container_width=True)

    with col2:
        st.markdown("#### Top Frequency")
        top_freq = rfm_df.nlargest(5, 'frequency')
        st.plotly_chart(px.bar(top_freq, x="frequency", y="customer_id", orientation='h', color_discrete_sequence=['#2c7be5']), use_container_width=True)

    with col3:
        st.markdown("#### Top Monetary")
        top_mon = rfm_df.nlargest(5, 'monetary')
        st.plotly_chart(px.bar(top_mon, x="monetary", y="customer_id", orientation='h', color_discrete_sequence=['#00d27a']), use_container_width=True)

st.divider()
st.caption(f"Copyright © 2026 Zayyana Maulida | Dashboard Rows: {len(filtered_df):,}")