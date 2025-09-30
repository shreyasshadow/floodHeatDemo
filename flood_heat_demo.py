# flood_heat_demo.py
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static

st.title("Hyperlocal Flood & Heat Adaptation Toolkit")

# --- Step 1: User Inputs ---
city = st.selectbox("Select City", ["Mumbai", "Delhi", "Chennai"])
date = st.date_input("Select Date")

st.markdown(f"### Flood Risk Map for {city} on {date}")

# --- Step 2: Mock Flood Risk Map ---
# Normally: use DEM + rainfall data, here we simulate
lat_center, lon_center = 19.0760, 72.8777 if city=="Mumbai" else (28.6139, 77.2090)
flood_map = folium.Map(location=[lat_center, lon_center], zoom_start=12)

# Simulate some flooded points
for _ in range(50):
    lat = lat_center + np.random.uniform(-0.05, 0.05)
    lon = lon_center + np.random.uniform(-0.05, 0.05)
    risk_level = np.random.choice(["Low", "Medium", "High"], p=[0.5, 0.3, 0.2])
    color = {"Low":"green","Medium":"orange","High":"red"}[risk_level]
    folium.CircleMarker(location=[lat, lon], radius=5, color=color, fill=True).add_to(flood_map)

folium_static(flood_map)

# --- Step 3: Heat Index Calculation ---
st.markdown(f"### Heat Index Forecast for {city}")

# Mock hourly temperature & humidity
hours = np.arange(0, 24)
temperature = np.random.uniform(30, 42, size=24)  # Celsius
humidity = np.random.uniform(40, 80, size=24)     # %

# Simple heat index formula (Celsius approximation)
HI = -8.784695 + 1.61139411*temperature + 2.338549*humidity - 0.14611605*temperature*humidity \
     - 0.012308094*(temperature**2) - 0.016424828*(humidity**2) \
     + 0.002211732*(temperature**2)*humidity + 0.00072546*temperature*(humidity**2) \
     - 0.000003582*(temperature**2)*(humidity**2)

# Risk levels
risk = ["Safe" if hi<30 else "Caution" if hi<38 else "Extreme" for hi in HI]
risk_colors = {"Safe":"green", "Caution":"orange", "Extreme":"red"}

# Plot
fig, ax = plt.subplots(figsize=(10,4))
for h, hi, r in zip(hours, HI, risk):
    ax.bar(h, hi, color=risk_colors[r])
ax.set_xticks(hours)
ax.set_xlabel("Hour")
ax.set_ylabel("Heat Index (°C)")
ax.set_title("Hourly Heat Index")
st.pyplot(fig)

# --- Step 4: Quick Insight ---
st.markdown("### Quick Insights")
st.write(f"Peak Heat Index: {HI.max():.1f}°C → Risk Level: {risk[np.argmax(HI)]}")
st.write("Number of hours in Extreme heat:", sum(r=="Extreme" for r in risk))
st.write("Number of areas with High flood risk:", sum([1 for marker in flood_map._children.values() 
                                                      if isinstance(marker, folium.vector_layers.CircleMarker) 
                                                      and marker.options['color']=='red']))
