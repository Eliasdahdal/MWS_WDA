import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium  # Import st_folium to render Folium maps in Streamlit
import os

# Set Streamlit page configuration
st.set_page_config(page_title='Sales Dashboard', page_icon=':bar_chart:')

# Load and clean data
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv('sales_data_sample.csv', encoding='ISO-8859-1')
    df.rename(columns={
        'ORDERNUMBER': 'Order ID',
        'PRODUCTLINE': 'Product',
        'QUANTITYORDERED': 'Quantity Ordered',
        'PRICEEACH': 'Price Each',
        'ORDERDATE': 'Order Date',
        'ADDRESSLINE1': 'Purchase Address',
        'CITY': 'CITY'
    }, inplace=True)
    df.dropna(subset=['Order Date', 'Quantity Ordered', 'Price Each'], inplace=True)
    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    df['Quantity Ordered'] = pd.to_numeric(df['Quantity Ordered'], errors='coerce')
    df['Price Each'] = pd.to_numeric(df['Price Each'], errors='coerce')
    df['Total Revenue'] = df['Quantity Ordered'] * df['Price Each']
    df['Year'] = df['Order Date'].dt.year  # Extract the year as an integer column
    return df

# Load data
df = load_and_clean_data()

# Calculate high-level metrics
total_revenue = df['Total Revenue'].sum()
total_units_sold = df['Quantity Ordered'].sum()
average_order_value = total_revenue / len(df['Order ID'].unique()) if len(df['Order ID'].unique()) > 0 else 0

# Global Revenue Trend Chart
def global_revenue_trend(data):
    data['Month'] = data['Order Date'].dt.to_period('M')
    monthly_revenue = data.groupby('Month').agg(total_revenue=('Total Revenue', 'sum')).reset_index()
    monthly_revenue['Month'] = monthly_revenue['Month'].dt.to_timestamp()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly_revenue['Month'], y=monthly_revenue['total_revenue'],
                             mode='lines+markers', name='Total Revenue'))
    fig.update_layout(title="Global Monthly Revenue Trend", xaxis_title="Month", yaxis_title="Total Revenue",
                      template="plotly_white")
    return fig

# Add filters for interactivity
min_year = int(df['Year'].min())
max_year = int(df['Year'].max())

# Year range slider
from_year, to_year = st.slider(
    'Select the year range',
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Filter data based on selected year range
filtered_df = df[(df['Year'] >= from_year) & (df['Year'] <= to_year)]

# Multi-select for products
unique_products = filtered_df['Product'].unique()
selected_products = st.multiselect(
    'Select products to view',
    unique_products,
    default=unique_products[:5]  # Select the first 5 products by default
)

filtered_df = filtered_df[filtered_df['Product'].isin(selected_products)]

# Analysis functions
def get_product_analysis(data):
    product_metrics = data.groupby('Product').agg(
        total_revenue=('Total Revenue', 'sum'),
        total_units_sold=('Quantity Ordered', 'sum'),
        average_price_per_unit=('Price Each', 'mean'),
        total_orders=('Order ID', 'nunique')
    ).reset_index()
    product_metrics['total_revenue'] = product_metrics['total_revenue'].apply(lambda x: f"${x:,.2f}")
    product_metrics['average_price_per_unit'] = product_metrics['average_price_per_unit'].apply(lambda x: f"${x:,.2f}")
    return product_metrics

def get_monthly_analysis(data):
    data['Month'] = data['Order Date'].dt.to_period('M')
    monthly_metrics = data.groupby('Month').agg(
        total_revenue=('Total Revenue', 'sum'),
        total_units_sold=('Quantity Ordered', 'sum'),
        average_price_per_unit=('Price Each', 'mean')
    ).reset_index()
    monthly_metrics['Month'] = monthly_metrics['Month'].dt.to_timestamp()
    return monthly_metrics

def get_city_analysis(data):
    city_metrics = data.groupby('CITY').agg(
        total_revenue=('Total Revenue', 'sum'),
        total_units_sold=('Quantity Ordered', 'sum')
    ).sort_values(by='total_revenue', ascending=False).head(5).reset_index()
    return city_metrics

# Prepare DataFrames for each tab
product_df = get_product_analysis(filtered_df)
monthly_df = get_monthly_analysis(filtered_df)
city_df = get_city_analysis(filtered_df)

# Tabbed layout for navigation
tabs = st.tabs(["Home", "Product Analysis", "Monthly Analysis", "City Analysis"])

# Home Tab with global overview
with tabs[0]:
    st.header("Global Sales Overview")
    
    # Display high-level metrics
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")
    col2.metric(label="Total Units Sold", value=f"{total_units_sold:,}")
    col3.metric(label="Average Order Value", value=f"${average_order_value:,.2f}")
    
    # Display global revenue trend chart
    st.plotly_chart(global_revenue_trend(df), use_container_width=True)

# Product Analysis Tab
with tabs[1]:
    st.header("Product Analysis")
    st.dataframe(product_df, use_container_width=True)

# Monthly Analysis Tab with interactive plot
with tabs[2]:
    st.header("Monthly Analysis")
    
    # Monthly metrics interactive plot
    def monthly_metrics_plot(data):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['Month'], y=data['total_revenue'],
                                 mode='lines+markers', name='Total Revenue'))
        fig.add_trace(go.Scatter(x=data['Month'], y=data['total_units_sold'],
                                 mode='lines+markers', name='Total Units Sold'))
        fig.add_trace(go.Scatter(x=data['Month'], y=data['average_price_per_unit'],
                                 mode='lines+markers', name='Average Price Per Unit'))

        fig.update_layout(title="Monthly Sales Metrics", xaxis_title="Month", yaxis_title="Value",
                          template="plotly_white")
        st.plotly_chart(fig)
    
    # Display chart first, then table
    monthly_metrics_plot(monthly_df)
    st.dataframe(monthly_df, use_container_width=True)

# City Analysis Tab with bar plot and map
with tabs[3]:
    st.header("Top 5 Cities by Revenue")
    
    # Interactive city sales bar chart
    def city_sales_bar_chart(data):
        fig = px.bar(data, x='total_revenue', y='CITY', orientation='h', title="Top 5 Cities by Total Revenue")
        fig.update_layout(template="plotly_white", xaxis_title="Total Revenue", yaxis_title="City")
        st.plotly_chart(fig)

    # Display bar chart first, then table
    city_sales_bar_chart(city_df)
    city_df['formatted_revenue'] = city_df['total_revenue'].apply(lambda x: f"${x:,.2f}")
    st.dataframe(city_df[['CITY', 'formatted_revenue', 'total_units_sold']], use_container_width=True)

    # City map visualization
    def generate_city_map(data):
        city_coordinates = {
            "Madrid": [40.4168, -3.7038],
            "San Rafael": [37.9735, -122.5311],
            "NYC": [40.7128, -74.0060],
            "Singapore": [1.3521, 103.8198],
            "Paris": [48.8566, 2.3522]
        }
        data['LAT'] = data['CITY'].map(lambda x: city_coordinates.get(x, [None, None])[0])
        data['LON'] = data['CITY'].map(lambda x: city_coordinates.get(x, [None, None])[1])
        data = data.dropna(subset=['LAT', 'LON'])

        m = folium.Map(location=[20, 0], zoom_start=2, tiles="cartodb positron")
        for _, row in data.iterrows():
            folium.CircleMarker(
                location=[row['LAT'], row['LON']],
                radius=row['total_revenue'] / 100000,
                color="blue",
                fill=True,
                fill_opacity=0.7,
                tooltip=f"{row['CITY']}: ${row['total_revenue']:,.2f}"
            ).add_to(m)
        st_folium(m, width=700, height=500)

    generate_city_map(city_df)
