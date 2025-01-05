import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_all_df(df):
    daily_orders_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum"
    }).reset_index()
    daily_orders_df.rename(columns={
        "cnt": "Total Penyewaan",
    }, inplace=True)
    
    return daily_orders_df

def create_daily_vs_df(df):
    daily_orders_df = df.resample(rule='D', on='dteday').agg({
        "casual": "sum",
        "registered": "sum"
    }).reset_index()
    daily_orders_df.rename(columns={
        "casual": "Kasual",
        "registered": "Terdaftar"
    }, inplace=True)
    
    return daily_orders_df

def create_byworkingday_df(df):
    byworkingday_df = df.groupby(['dteday', 'workingday']).agg({
        "cnt": "sum"
    }).reset_index()
    byworkingday_df.rename(columns={
        "cnt": "Total Penyewaan",
    }, inplace=True)
    return byworkingday_df

def create_byweathersit_df(df):
    byweathersit_df = df.groupby(['dteday', 'weathersit']).agg({
        "cnt": "sum"
    }).reset_index()
    byweathersit_df.rename(columns={
        "cnt": "Total Penyewaan",
    }, inplace=True)
    return byweathersit_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="instant", as_index=False).agg({
        "dteday": "max", # mengambil tanggal order terakhir
        "cnt": "sum", # menghitung jumlah order
    })
    rfm_df.columns = ["instant", "max_order_timestamp", "frequency"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["dteday"].dt.date.max()  # Menggunakan df yang benar
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

# Membaca data dari CSV
all_df = pd.read_csv("dashboard/day_master.csv")

# Mengonversi kolom tanggal
datetime_columns = ["dteday"]
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(drop=True, inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://miro.medium.com/v2/resize:fit:1400/1*tFONSoZiVSpQGP_s1BvfJg.jpeg")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Memfilter data berdasarkan rentang tanggal
main_df = all_df[(all_df["dteday"] >= pd.to_datetime(start_date)) & 
                  (all_df["dteday"] <= pd.to_datetime(end_date))]

# Membuat DataFrame yang diperlukan
daily_all_df = create_daily_all_df(main_df)
daily_vs_df = create_daily_vs_df(main_df)
byworkingday_df = create_byworkingday_df(main_df)
byweathersit_df = create_byweathersit_df(main_df)
rfm_df = create_rfm_df(main_df)

# Menampilkan dashboard
st.header('Bike Sharing Dashboard :sparkles:')

st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_all_df["Total Penyewaan"].sum() 
    st.metric("Total orders", value=total_orders)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_all_df["dteday"],
    daily_all_df["Total Penyewaan"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.set_xlabel('Tanggal', fontsize=20)
ax.set_ylabel('Jumlah Penyewaan', fontsize=20)

st.pyplot(fig)


# Menampilkan Daily vs Orders
st.subheader('Kasual vs Terdaftar')

fig_vs, ax_vs = plt.subplots(figsize=(16, 8))

# Plot untuk Kasual
ax_vs.plot(
    daily_vs_df["dteday"],
    daily_vs_df["Kasual"],
    marker='o', 
    linewidth=2,
    color="#FFAB40",
    label='Kasual'
)

# Plot untuk Terdaftar
ax_vs.plot(
    daily_vs_df["dteday"],
    daily_vs_df["Terdaftar"],
    marker='o', 
    linewidth=2,
    color="#64B5F6",
    label='Terdaftar'
)

# Menambahkan label dan judul
ax_vs.set_title('Jumlah Penyewaan Harian: Kasual vs Terdaftar', fontsize=24)
ax_vs.set_xlabel('Tanggal', fontsize=20)
ax_vs.set_ylabel('Jumlah Penyewaan', fontsize=20)
ax_vs.tick_params(axis='y', labelsize=20)
ax_vs.tick_params(axis='x', labelsize=15)
ax_vs.legend(fontsize=16)

# Menampilkan plot
st.pyplot(fig_vs)


# Menyiapkan data untuk plot
st.subheader('Perbandingan Jumlah Penyewa Sepeda')
byweathersit_df['weathersit'] = byweathersit_df['weathersit'].map({
    1: 'Cerah',
    2: 'Berawan',
    3: 'Hujan Ringan',
    4: 'Hujan Berat'
})

# Menggunakan DataFrame yang sudah ada untuk plot
workingday_counts = byworkingday_df.groupby('workingday')['Total Penyewaan'].sum().reset_index()
weathersit_counts = byweathersit_df.groupby('weathersit')['Total Penyewaan'].sum().reset_index()

# Menampilkan plot
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    
    sns.barplot(
        y="Total Penyewaan", 
        x="workingday",
        data=workingday_counts.sort_values(by="Total Penyewaan", ascending=False),
        palette=["#90CAF9", "#FFAB40"],
        ax=ax
    )
    ax.set_title("Jumlah Penyewaan Berdasarkan Hari Kerja", loc="center", fontsize=50)
    ax.set_ylabel("Jumlah Penyewaan")
    ax.set_xlabel("Hari Kerja")
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    
    sns.barplot(
        y="Total Penyewaan", 
        x="weathersit",
        data=weathersit_counts.sort_values(by="Total Penyewaan", ascending=False),
        palette=["#90CAF9", "#FFAB40", "#D3D3D3", "#D3D3D3"],
        ax=ax
    )
    ax.set_title("Jumlah Penyewaan Berdasarkan Kondisi Cuaca", loc="center", fontsize=50)
    ax.set_ylabel("Jumlah Penyewaan")
    ax.set_xlabel("Kondisi Cuaca")
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

# Menampilkan RFM Metrics
st.subheader("Best Customer Based on RFM Parameters")

col1, col2 = st.columns(2)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(30, 15))
colors = ["#90CAF9", "#90CAF9"]

sns.barplot(y="recency", x="instant", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Customer ID", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(y="frequency", x="instant", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Customer ID", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

st.pyplot(fig)

st.caption('Copyright (c) Fika 2025')
