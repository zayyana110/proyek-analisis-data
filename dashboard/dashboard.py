import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

@st.cache_data
def load_data():
    
    df = pd.read_csv("dashboard/main_data.csv")
    datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
    for column in datetime_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column])
    return df

all_df = load_data()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.title("Zayyana Maulida")
    st.write("Proyek Analisis Data E-Commerce")

st.header('E-Commerce Data Analysis Dashboard 📊')

st.subheader("Best & Worst Performing Product")

sum_order_items_df = all_df.groupby("product_category_name_english").product_id.count().sort_values(ascending=False).reset_index()

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="product_id", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_title("Best Performing Product", loc="center", fontsize=20)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=15)

sns.barplot(x="product_id", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_title("Worst Performing Product", loc="center", fontsize=20)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=15)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()

st.pyplot(fig)

st.subheader("Monthly Revenue Trend (2017-2018)")

monthly_revenue_df = all_df.resample(rule='ME', on='order_purchase_timestamp').agg({"price": "sum"}).reset_index()
monthly_revenue_df.rename(columns={"price": "revenue"}, inplace=True)
monthly_revenue_df['order_purchase_timestamp'] = monthly_revenue_df['order_purchase_timestamp'].dt.strftime('%B %Y')

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_revenue_df["order_purchase_timestamp"],
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

st.subheader("Best Customer Based on RFM Parameters")

rfm_df = all_df.groupby(by="customer_unique_id", as_index=False).agg({
    "order_purchase_timestamp": "max",
    "order_id": "nunique",
    "price": "sum"
})
rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
recent_date = all_df["order_purchase_timestamp"].max()
rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#72BCD4"] * 5

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_title("By Recency (days)", loc="center", fontsize=30)
ax[0].tick_params(axis='x', rotation=45, labelsize=20)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_title("By Frequency", loc="center", fontsize=30)
ax[1].tick_params(axis='x', rotation=45, labelsize=20)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_title("By Monetary", loc="center", fontsize=30)
ax[2].tick_params(axis='x', rotation=45, labelsize=20)

st.pyplot(fig)

st.caption('Copyright (C) Zayyana Maulida 2024')