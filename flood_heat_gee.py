# flood_heat_gee.py
import streamlit as st
import geemap.foliumap as geemap
import ee
import numpy as np
import matplotlib.pyplot as plt

# --- Authenticate GEE ---
ee.Initialize()

st.title("Mumbai Hyperlocal Flood & Heat Adaptation Toolkit (Live Data)")

# --- Inputs ---
date = st.date_input("Select Date")

# Mumbai bounding box
mumbai_roi = ee.Geometry.Rectangle([72.75, 18.90, 73.05, 19.30])

# --- Step 1: Load DEM (SRTM) ---
dem = ee.Image("USGS/SRTMGL1_003").clip(mumbai_roi)

# --- Step 2: Load Rainfall Data (GPM IMERG Daily) ---
# For demonstration, pick the day of input
year, month, day = date.year, date.month, date.day
rainfall = ee.ImageCollection("NASA/GPM_L3/IMERG_V06")
rainfall = rainfall.filterDate(f"{year}-{month:02d}-{day:02d}", f"{year}-{month:02d}-{day:02d}")
rainfall = rainfall.select("precipitationCal").mean().clip(mumbai_roi)

# --- Step 3: Simple Flood Risk Calculation ---
# Normalize DEM and Rainfall
dem_norm = dem.unitScale(ee.Number(dem.reduceRegion(
    reducer=ee.Reducer.minMax(), geometry=mumbai_roi, scale=30
).get('elevation'))[0], ee.Number(dem.reduceRegion(
    reducer=ee.Reducer.minMax(), geometry=mumbai_roi, scale=30
).get('elevation'))[1])

rain_norm = rainfall.unitScale(ee.Number(rainfall.reduceRegion(
    reducer=ee.Reducer.minMax(), geometry=mumbai_roi, scale=1000
).get('precipitationCal'))[0], ee.Number(rainfall.reduceRegion(
    reducer=ee.Reducer.minMax(), geometry=mumbai_roi, scale=1000
).get('precipitationCal'))[1])

# Flood risk = high rainfall + low elevation
flood_risk = rain_norm.multiply(1 - dem_norm)

# --- Step 4: Display Map ---
Map = geemap.Map(center=[19.0760, 72.8777], zoom=11)
Map.addLayer(flood_risk, {'min':0, 'max':1, 'palette':['green','yellow','red']}, 'Flood Risk')
Map.addLayerControl()
Map.to_streamlit(height=500)

# --- Step 5: Heat Index (mock for now) ---
temperature = np.random.uniform(30,42,24)
humidity = np.random.uniform(40,80,24)
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
