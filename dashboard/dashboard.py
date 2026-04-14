import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Set Konfigurasi Halaman
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    # Perbaikan path agar fleksibel (mencari di folder dashboard atau root)
    if os.path.exists("dashboard/main_data.csv"):
        df = pd.read_csv("dashboard/main_data.csv")
    elif os.path.exists("main_data.csv"):
        df = pd.read_csv("main_data.csv")
    else:
        st.error("File main_data.csv tidak ditemukan!")
        return None

    datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
    for column in datetime_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column])
    return df

all_df = load_data()

# Pastikan data berhasil dimuat sebelum lanjut
if all_df is not None:
    # --- SIDEBAR ---
    with st.sidebar:
        st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
        st.title("Zayyana Maulida")
        st.write("Proyek Analisis Data E-Commerce")

    # --- HEADER ---
    st.header('E-Commerce Data Analysis Dashboard 📊')

    # --- BAGIAN 1: PERFORMA PRODUK ---
    st.subheader("Best & Worst Performing Product")

    # Penanganan jika kolom nama inggris tidak ditemukan
    category_col = "product_category_name_english" if "product_category_name_english" in all_df.columns else "product_category_name"
    
    sum_order_items_df = all_df.groupby(category_col).product_id.count().sort_values(ascending=False).reset_index()

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(x="product_id", y=category_col, data=sum_order_items_df.head(5), palette=colors, ax=ax[0], hue=category_col, legend=False)
    ax[0].set_title("Best Performing Product", loc="center", fontsize=20)
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Number of Sales", fontsize=15)

    sns.barplot(x="product_id", y=category_col, data=sum_order_items_df.sort_values(by="product_id", ascending=True).head(5), palette=colors, ax=ax[1], hue=category_col, legend=False)
    ax[1].set_title("Worst Performing Product", loc="center", fontsize=20)
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Number of Sales", fontsize=15)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()

    st.pyplot(fig)

    # --- BAGIAN 2: TREN PENDAPATAN ---
    st.subheader("Monthly Revenue Trend (2017-2018)")

    monthly_revenue_df = all_df.resample(rule='ME', on='order_purchase_timestamp').agg({"price": "sum"}).reset_index()
    monthly_revenue_df.rename(columns={"price": "revenue"}, inplace=True)
    
    # Simpan versi string untuk plotting agar sumbu X rapi
    monthly_revenue_df['month_year'] = monthly_revenue_df['order_purchase_timestamp'].dt.strftime('%B %Y')

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        monthly_revenue_df["month_year"],
        monthly_revenue_df["revenue"],
        marker='o', 
        linewidth=3,
        color="#72BCD4"
    )
    ax.set_title("Total Revenue per Month", fontsize=25)
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)

    st.pyplot(fig)

    # --- BAGIAN 3: ANALISIS RFM ---
    st.subheader("Best Customer Based on RFM Parameters")

    # Pastikan menggunakan ID yang tepat untuk RFM
    customer_col = "customer_unique_id" if "customer_unique_id" in all_df.columns else "customer_id"

    rfm_df = all_df.groupby(by=customer_col, as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    recent_date = all_df["order_purchase_timestamp"].max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
    colors = ["#72BCD4"] * 5

    sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0], hue="customer_id", legend=False)
    ax[0].set_title("By Recency (days)", loc="center", fontsize=30)
    ax[0].tick_params(axis='x', rotation=45, labelsize=20)

    sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1], hue="customer_id", legend=False)
    ax[1].set_title("By Frequency", loc="center", fontsize=30)
    ax[1].tick_params(axis='x', rotation=45, labelsize=20)

    sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2], hue="customer_id", legend=False)
    ax[2].set_title("By Monetary", loc="center", fontsize=30)
    ax[2].tick_params(axis='x', rotation=45, labelsize=20)

    st.pyplot(fig)

    st.caption('Copyright (C) Zayyana Maulida 2024')