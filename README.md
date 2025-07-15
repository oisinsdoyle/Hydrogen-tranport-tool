# Hydrogen Pipeline Route Planner

Python-based interactive tool to estimate the transport cost of hydrogen between two locations in Europe using the European Hydrogen Backbone (EHB) pipeline network. The tool uses real pipeline infrastructure data to calculate distances, estimate transport costs, and visualize the route on an interactive map.

---

## 1. Project Overview

This tool focuses on the transportation segment of the hydrogen supply chain. It calculates the shortest pipeline-based transport route between a selected origin and destination, using spatial data from the European Hydrogen Backbone. The app computes total transport distance, estimates a cost per kilogram of hydrogen transported, and visualizes the pipeline route using an interactive map.

---

## 2. Scope and Objectives

- Enable interactive selection of two locations (by coordinates or place names)
- Snap those locations to the nearest hydrogen pipeline node
- Build a connected graph from real pipeline geometry data
- Calculate the shortest available route using Dijkstra’s algorithm
- Estimate total hydrogen transport cost based on distance
- Provide route commissioning year and segment information
- Display results using an embedded Folium map in a Streamlit web app

---

## 3. Work Completed

- Parsed and processed EHB pipeline data (GeoJSON format)
- Created a graph representation of the pipeline network
- Implemented nearest-node snapping for input locations
- Built functionality to compute shortest route using NetworkX
- Integrated transport cost estimation based on distance
- Developed interactive map using Folium and Streamlit
- Allowed user input via city/place names or coordinates

---

## 4. Project Structure

- `app.py` – Main Streamlit application
- `Hydrogen backbone map Transmission data.json` – EHB pipeline GeoJSON data
- `requirements.txt` – Python dependencies
- `README.md` – This documentation file

---

## 5. How the Tool Works

**Input**  
- Origin and destination: entered as city/place names or decimal latitude/longitude  
- The app geocodes place names (via Nominatim) or uses raw coordinates  

**Processing**  
- Snap points to the nearest node on the pipeline network  
- Build shortest path using Dijkstra’s algorithm on the graph  
- Estimate total distance and cost (€/kg)  
- Extract latest commissioning year from route segments  

**Output**  
- Map with overlaid pipeline route and markers for origin/destination  
- Transport distance (in km)  
- Estimated transport cost (€/kg)  
- Route availability year (latest among traversed segments)  
- Names of the pipeline segments used  

---

## 6. Technologies and Libraries Used

- `streamlit` – Web application framework
- `geopandas` – For geospatial data handling
- `shapely` – Geometry operations
- `networkx` – Graph construction and routing
- `folium` – Interactive map visualization
- `geopy` – Geocoding and distance utilities
- `scipy.spatial.cKDTree` – Efficient nearest-neighbor search

---

## 7. Known Limitations and Assumptions

- Only supports locations that can be snapped to the existing EHB pipeline network  
- Place names must be sufficiently clear to be correctly geocoded  
- Cost estimates are based on generalized €/kg/km assumptions (can be adjusted)  
- Commissioning year is assumed accurate based on available metadata in GeoJSON  
- Last-mile transport or off-network segments are not currently modeled  

---

## 8. Future Improvements

- Add support for last-mile transport using road or rail network models  
- Include interactive cost parameter settings (e.g., €/km values)  
- Improve robustness for ambiguous or poorly geocoded place names  
- Integrate pipeline construction costs for hypothetical extensions  
- Incorporate modules for hydrogen production and purification costing  
  (potentially as part of a broader end-to-end hydrogen costing tool)  

---

## 9. Data Sources

- European Hydrogen Backbone Pipeline Data:  
  https://www.h2inframap.eu/  
  (GeoJSON extracted via ArcGIS API)

- Geocoding and City Location Data:  
  https://simplemaps.com/data/world-cities  
  https://nominatim.openstreetmap.org/
