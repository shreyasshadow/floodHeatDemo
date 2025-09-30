import streamlit as st
import numpy as np
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt

st.title("Mumbai Flood & Heat Adaptation Toolkit (Static Demo)")

# --- User Inputs ---
date = st.date_input("Select Date")

# --- Step 1: Create static DEM + Rainfall grids ---
# Simulate a 50x50 grid for Mumbai
rows, cols = 50, 50
np.random.seed(42)

# DEM: elevations in meters (approx range 0-50)
dem = np.random.uniform(0, 50, size=(rows, cols))

# Rainfall: mm/day (simulate moderate-heavy rainfall)
rainfall = np.random.uniform(50, 200, size=(rows, cols))

# --- Step 2: Compute Flood Risk ---
# Simple risk metric: high rainfall + low elevation
flood_risk = (1 - dem / dem.max()) * (rainfall / rainfall.max())  # 0-1
flood_risk_colors = np.empty(flood_risk.shape, dtype=object)
for i in range(rows):
    for j in range(cols):
        if flood_risk[i,j] > 0.7:
            flood_risk_colors[i,j] = "red"
        elif flood_risk[i,j] > 0.4:
            flood_risk_colors[i,j] = "orange"
        else:
            flood_risk_colors[i,j] = "green"

# --- Step 3: Display Flood Map ---
lat_center, lon_center = 19.0760, 72.8777  # Mumbai
flood_map = folium.Map(location=[lat_center, lon_center], zoom_start=12)

# Plot the grid on the map
lat_min, lat_max = 18.90, 19.30
lon_min, lon_max = 72.75, 73.05
lat_grid = np.linspace(lat_min, lat_max, rows)
lon_grid = np.linspace(lon_min, lon_max, cols)

for i in range(rows):
    for j in range(cols):
        folium.CircleMarker(
            location=[lat_grid[i], lon_grid[j]],
            radius=4,
            color=flood_risk_colors[i,j],
            fill=True
        ).add_to(flood_map)

folium_static(flood_map)

# --- Step 4: Heat Index Forecast (mock) ---
temperature = np.random.uniform(30,42,24)  # °C
humidity = np.random.uniform(40,80,24)     # %
HI = -8.784695 + 1.61139411*temperature + 2.338549*humidity - 0.14611605*temperature*humidity \
     - 0.012308094*(temperature**2) - 0.016424828*(humidity**2) \
     + 0.002211732*(temperature**2)*humidity + 0.00072546*temperature*(humidity**2) \
     - 0.000003582*(temperature**2)*(humidity**2)

hours = np.arange(24)
risk = ["Safe" if hi<30 else "Caution" if hi<38 else "Extreme" for hi in HI]
risk_colors = {"Safe":"green", "Caution":"orange", "Extreme":"red"}

fig, ax = plt.subplots(figsize=(10,4))
for h, hi, r in zip(hours, HI, risk):
    ax.bar(h, hi, color=risk_colors[r])
ax.set_xticks(hours)
ax.set_xlabel("Hour")
ax.set_ylabel("Heat Index (°C)")
ax.set_title("Hourly Heat Index")
st.pyplot(fig)

# --- Step 5: Quick Insights ---
st.markdown("### Quick Insights")
st.write(f"Peak Heat Index: {HI.max():.1f}°C → Risk Level: {risk[np.argmax(HI)]}")
st.write("Number of hours in Extreme heat:", sum(r=="Extreme" for r in risk))
st.write("Number of grid points with High flood risk:", np.sum(flood_risk > 0.7))
