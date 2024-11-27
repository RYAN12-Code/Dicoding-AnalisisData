# === Import Library ===
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import geopandas as gpd  # versi 0.13.00 with python version 3.9
import folium
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster


# == Atribut dan fungsi ===
# Total Review
def create_total_review_df(df):
    total_review_df = df["review_score"].value_counts()

    return total_review_df


def create_product_counts_df(df):
    filtered_df_r123 = df[df['review_score'].isin([1, 2, 3])]
    product_counts = filtered_df_r123["product_category_name_english"].value_counts(
    )

    return product_counts


def create_geolocation_df(df):
    filtered_df_r123 = df[df['review_score'].isin([1, 2, 3])]
    geolocation_df = filtered_df_r123[["geolocation_lat",
                                       "geolocation_lng",
                                       "review_score",
                                       "geolocation_city"]]

    return geolocation_df


def create_low_rating(df):
    low_rating = df[df['review_score'].isin([1, 2, 3])]

    return low_rating


# == read data ==
main_data = pd.read_csv("main_data.csv")


total_review_df = create_total_review_df(main_data)
product_counts_df = create_product_counts_df(main_data)
geolocation_df = create_geolocation_df(main_data)
low_rating = create_low_rating(main_data)

# === Membuat Komponen Filter ===
min_rating = main_data["review_score"].min()
max_rating = main_data["review_score"].max()


# == Side bar ==
with st.sidebar:
    # Logo
    st.image("rb_2148460710_white.png")
    # st.caption("Made on 19 November 2024")
    st.markdown(
        """
    <style>
    .centered-caption {
        text-align: center;
        font-size: 16px;
        color: gray;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Menampilkan teks menggunakan st.caption
    st.caption(
        '<p class="centered-caption">Made on 19 November 2024.</p>',
        unsafe_allow_html=True)
    st.caption(
        '<p class="centered-caption">by I Putu Ryan Adnyana.</p>',
        unsafe_allow_html=True)

# == Main header ==
st.header('Proyek Analisis Data : E-Commerce Public Dataset')

# === Sub header ===
st.subheader("Percentage Rating Product")

col1, col2 = st.columns(2)

with col1:
    total_review = total_review_df.sum()
    st.metric("Total Review", value=total_review)


# === Piechart ===
st.subheader("Percentage Low Rating Review (Rating 1, 2, and 3)")
# Generate the pie chart
plt.figure(figsize=(8, 8))

# Create the pie chart from the value counts of review_score in low_rating
low_rating['review_score'].value_counts().plot(
    kind='pie',
    autopct='%1.1f%%',
    startangle=140,
    colors=['skyblue', 'orange', 'green']
)
plt.title('Rating Review Distribution')
plt.ylabel('')  # Hide the y-label

# Display the plot in Streamlit
st.pyplot(plt)

# === Sidebar Filter for Rating ===
with st.sidebar:
    # Filter for selecting ratings
    selected_ratings = st.multiselect(
        "Select Ratings to Filter (1, 2, and 3)", 
        options=[1, 2, 3], 
        default=[1, 2, 3]  # Default to all ratings
    )

# === Filter the DataFrame based on selected ratings ===
filtered_low_rating = low_rating[low_rating['review_score'].isin(selected_ratings)]

# === Barplot ===
st.caption('\n')
st.subheader("Product Name Category with Low Rating(Rating 1, 2, and 3)")
# Create a bar plot based on the filtered data
filtered_product_counts_df = create_product_counts_df(filtered_low_rating)

plt.figure(figsize=(10, 6))
filtered_product_counts_df.head(5).sort_values().plot(kind='barh', color='skyblue')
plt.title('Top 5 Product Categories with Low Ratings (1, 2, and 3)')
plt.xlabel('Count')
plt.ylabel(' ')

# Add value labels on the bars
for index, value in enumerate(filtered_product_counts_df.head(5).sort_values()):
    plt.text(value, index, str(value))

# Display the plot in Streamlit
st.pyplot(plt)


# 1. Membuat GeoDataFrame dari DataFrame yang Ada
gdf = gpd.GeoDataFrame(
    geolocation_df,
    geometry=gpd.points_from_xy(
        geolocation_df["geolocation_lng"],
        geolocation_df["geolocation_lat"]
    )
)

# 2. Inisialisasi Peta dengan Titik Tengah
if not gdf.empty:
    center_lat = gdf.geometry.y.mean()
    center_lon = gdf.geometry.x.mean()
else:
    center_lat, center_lon = 0, 0  # Default center if data is missing

m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

# 3. Menambahkan MarkerCluster untuk Distribusi Data Berdasarkan 'review_score'
marker_cluster = MarkerCluster().add_to(m)

# 4. Menambahkan Marker dengan Warna Berdasarkan 'review_score'


def get_marker_color(score):
    if score == 1:
        return 'red'     # Warna merah untuk skor 1
    elif score == 2:
        return 'orange'  # Warna oranye untuk skor 2
    elif score == 3:
        return 'green'  # Warna hijau untuk skor 3
    else:
        return 'blue'    # Default warna biru untuk nilai lainnya


for idx, row in gdf.iterrows():
    folium.Marker(
        location=[
            row.geometry.y,
            row.geometry.x],
        popup=f"City: {row['geolocation_city']}<br>Review Score: {row['review_score']}",
        icon=folium.Icon(
            color=get_marker_color(
                row['review_score']))).add_to(marker_cluster)

# 5. Tampilkan Peta di Streamlit
st.title("Customer Review Distribution Map")

# Render map with Streamlit
st_folium(m, width=800, height=600)
st.caption("Red = rating 1, Yellow = rating 2, Green = rating 3")
