# Import necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Title of the app
st.title("San Jose Police Calls Data Analysis")

# Hardcoded file paths for the 4 main CSV files and the additional CSV file
file_2020 = 'policecalls2020.csv'
file_2021 = 'policecalls2021.csv'
file_2022 = 'policecalls2022.csv'
file_2023 = 'policecalls2023.csv'

# Load the 4 main CSV files and combine them into one DataFrame
data2020 = pd.read_csv(file_2020)
data2021 = pd.read_csv(file_2021)
data2022 = pd.read_csv(file_2022)
data2023 = pd.read_csv(file_2023)

data = pd.concat([data2020, data2021, data2022, data2023], ignore_index=True)

# Display the shape of the dataset before removing columns
st.subheader("Dataset Overview")
st.write("Before Removing Columns:")
st.write(f"Shape: {data.shape}")

# Remove unnecessary columns
cols_to_drop = [
    'CDTS', 'EID', 'START_DATE', 'CALL_NUMBER', 'REPORT_DATE', 
    'CALLTYPE_CODE', 'FINAL_DISPO_CODE', 'CITY', 'STATE', 'ADDRESS'
]
data.drop(columns=cols_to_drop, inplace=True, errors='ignore')

# Display the shape of the dataset after removing columns
st.write("After Removing Columns:")
st.write(f"Shape: {data.shape}")

# Convert OFFENSE_DATE to datetime format
data['OFFENSE_DATE'] = pd.to_datetime(data['OFFENSE_DATE'], format='%m/%d/%Y %I:%M:%S %p')

# --- Visualization 1: Top 20 CALL_TYPE Categories ---
st.subheader("Top 20 CALL_TYPE Categories")
call_type_counts = data['CALL_TYPE'].value_counts().nlargest(20).reset_index()
call_type_counts.columns = ['Category', 'Count']

fig1 = px.bar(
    call_type_counts, x='Count', y='Category', orientation='h',
    text='Count', title='Top 20 CALL_TYPE Categories'
)
fig1.update_yaxes(autorange='reversed')
fig1.update_traces(texttemplate='%{text}', textposition='inside')
st.plotly_chart(fig1)

# --- Visualization 2: FINAL_DISPO Categories ---
st.subheader("FINAL_DISPO Categories")
final_dispo_counts = data['FINAL_DISPO'].value_counts().reset_index()
final_dispo_counts.columns = ['Category', 'Count']

fig2 = px.bar(
    final_dispo_counts, x='Count', y='Category', orientation='h',
    text='Count', title='FINAL_DISPO Categories'
)
fig2.update_yaxes(autorange='reversed')
fig2.update_traces(texttemplate='%{text}', textposition='inside')
st.plotly_chart(fig2)

# --- Visualization 3: Priority Pie Chart ---
st.subheader("PRIORITY Distribution")
priority_counts = data['PRIORITY'].value_counts().reset_index()
priority_counts.columns = ['Category', 'Count']

fig3 = px.pie(
    priority_counts, names='Category', values='Count',
    title="PRIORITY Pie Chart", hole=0.3,
    labels={'Count': 'Count'}
)
fig3.update_traces(textinfo='percent+label')
st.plotly_chart(fig3)

# --- Visualization 4: Month-wise Distribution ---
st.subheader("Month-wise Distribution of Calls")


# Making a dataframe of Months and their respective calls counts.
month = data['OFFENSE_DATE'].groupby([data['OFFENSE_DATE'].dt.month.rename('index')]).agg({'count'})
month['Month'] = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
# Bar chart to show the month wise distribution of the calls counts.
fig4 = px.bar(month, x=month['Month'], y='count', title='Month Wise Distribution of Calls', labels={'count': 'Count'}, text='count', color=month['Month'])

st.plotly_chart(fig4)

# --- Visualization 5: Day-wise Progression Chart ---
st.subheader("Day-wise Progression of Calls (2020-2023)")

date_df = data.groupby("OFFENSE_DATE")['OFFENSE_DATE'].count()

idx = pd.date_range('2020-01-01', '2023-12-31')

date_df.index = pd.DatetimeIndex(date_df.index)

date_df = date_df.reindex(idx, fill_value=0).to_frame(name="Crimes").reset_index()

date_df.rename(columns={'index': 'Date'}, inplace=True)

date_df['7DayMA'] = date_df['Crimes'].rolling(window=7).mean()

fig5 = go.Figure()

fig5.add_trace(go.Scatter(x=date_df.Date, y=date_df.Crimes, mode='lines', name="No of Calls"))

fig5.add_trace(go.Scatter(x=date_df.Date, y=date_df["7DayMA"], mode='lines+markers', name="7-Day Moving Average"))

fig5.update_layout(
    title="San Jose Progression of Calls",
    xaxis_title="Date", yaxis_title="Number of Calls",
    hovermode="x"
)

st.plotly_chart(fig5)

# --- Visualization 6: Hour-wise Distribution ---
st.subheader("Hour-wise Distribution of Calls")

times_data = pd.DatetimeIndex(data['OFFENSE_TIME']).hour.value_counts().reset_index()
times_data.columns = ['Hour', 'Count']

fig6 = px.bar(
    times_data, x='Hour', y='Count',
    title="Hour-wise Distribution", text='Count',
    color=times_data['Hour']
)
st.plotly_chart(fig6)

# For Map Hotspots

import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# Hardcoded file path for the dataset
arrest_data_path = 'updated_sampled_arrestData.csv'
arrest_data = pd.read_csv(arrest_data_path)


# Check if Latitude and Longitude columns exist
if 'Latitude' in arrest_data.columns and 'Longitude' in arrest_data.columns:
    # Create a map centered on San Jose
    map_center = [37.3382, -121.8863]  # San Jose coordinates
    mymap = folium.Map(location=map_center, zoom_start=12)

    # Add markers with clustering
    marker_cluster = MarkerCluster().add_to(mymap)

    for _, row in arrest_data.iterrows():
        if pd.notnull(row['Latitude']) and pd.notnull(row['Longitude']):
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"Call Type: {row['CALL_TYPE']}<br>Date: {row['START_DATE']}",
            ).add_to(marker_cluster)

    # Display the map in Streamlit using streamlit_folium
    st.subheader("Police Calls Map")
    st_folium(mymap, width=800, height=600)
else:
    st.error("The dataset does not contain 'Latitude' and 'Longitude' columns.")