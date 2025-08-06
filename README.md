# Hydrogen costing tool (Pipeline Route Planner)

Python-based interactive tool to estimate the transport cost of hydrogen between two locations in Europe using the European Hydrogen Backbone (EHB) pipeline network. The tool uses projected pipeline infrastructure data to calculate distances, estimate transport costs, and visualise the route on a detailed map.

The tool is hosted on streamlit available at this link https://hydrogen-transport-tool.streamlit.app/

---

## 1. Project Overview

This tool focuses on the transportation segment of the hydrogen supply chain. It calculates the shortest pipeline-based transport route between a selected origin and destination, using coordinate data from the European Hydrogen Backbone. The app computes total transport distance, estimates a cost per kilogram of hydrogen transported, and visualises the pipeline route using an interactive map.

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
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
<br />
## 3. Work Completed

- Parsed and processed EHB pipeline data (GeoJSON format)
    - This was completed using the ArcGIS Rest API for the Hydrogen Infrastructure map website, the API directory for the map can be accessed at this link https://services9.arcgis.com/xSsJeibXqRtsnmY7/arcgis/rest/services/Hydrogen_Infrastructure_Map_2024Q4_WFL1/FeatureServer
    - The following guide was used to find this directory https://www.reddit.com/r/ArcGIS/comments/1e3xp14/arcgis_map_scraping/
    - The transmission GeoJSON data was extracted by selecting the transmission layer, selecting "query" at the bottom of the page then submitting a GeoJSON query request.
    - the following values were applied to the query to return all of the transmission geometry: "Where"-"1=1", "Out Fields" - "*", "Return Geometry" - "True", "SQL Format" - "none", "Format" - "GeoJSON"
- Created a graph representation of the pipeline network with nearby coordinates snapped together to solve disconnection issues
    - Converted the network into a graph where each coordinate is defined as a node and the pipeline sections between each coordinate are defined as an edge, allowing for the use of an algorithm to find the optimal path between two points along the network. [A short introduction to graph theory can be found here](https://medium.com/basecs/a-gentle-introduction-to-graph-theory-77969829ead8)
    - To generate the graph, the geometry of each pipeline in the network is looped through, rounded and added to an array, this is completed for both LineString and Multilinestring data.
    - To snap nearby coordinates together to one reference coordinate, a tree is defined using the cKDTree library with this array as an input. A threshold of 0.11 degrees is set which correlates to approximately 12km ,this defines how close coordinates have to be to be snapped together, the coordinate list is looped through with nearby coordinates being snapped together.
    - Edges are then added according to the path between each node, the distance of this path is set as the weight of the edge.
    - The largest connected component is kept to ensure the network is one connected graph.
- Implemented nearest-node snapping for input locations using Kdtree nearest neighbour processing
    - Taking user lon, lat as input and querying for closest coordinate in pipeline graph.
- Built functionality to compute shortest route using NetworkX
    - Used Networkx library shortest_path function which uses Dijsktra's algorithm by default to find the optimal path between two given points along the graph.
- Integrated transport cost estimation based on distance
      - Distance output is multiplied by EHB estimate for cost of transport along pipeline network per kg of hydrogen per 1000km
- Developed interactive map using Folium and Streamlit
      -Tool output is visualised on a map using Folium library and this is integrated into a web app front-end using the streamlit python framework.
- Allowed user input via city/place names or coordinates

---

## 4. Project Structure

- `streamlit_test.py` – Main Streamlit application
- `Hydrogen backbone map Transmission data.json` – EHB pipeline GeoJSON data
- `requirements.txt` – Python dependencies
- `README.md` – This documentation file

---
<br />
<br />
<br />
## 5. How the Tool Works
**Running the tool**
- To run the tool, the streamlit app can be run locally via command line using using "streamlit run "file path""
- The tool can also be hosted through the Streamlit web platform by deploying the app to Streamlit Community Cloud, allowing it to be accessed and used via a public URL.

**Input**  
- Origin and destination: entered as city/place names or decimal latitude/longitude  
- The app geocodes place names (via Nominatim) or uses raw coordinates  

**Processing**  
- Finds nearest point on the pipeline network the given location
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
- `folium` – Interactive map visualisation
- `geopy` – Geocoding and distance utilities
- `scipy.spatial.cKDTree` – nearest-neighbor search

---

## 7. Known Limitations and Assumptions

- Snapping function to overcome gaps in the pipeline data results in accuracies in the routing where the route doesn't exactly follow the pipeline co-ordinates
- Place names must be sufficiently clear to be correctly geocoded.  
- Cost estimates are based on generalized €/kg/km assumption from the EHB estimate of onshore pipelines for 2040 ( highest estimate of the range of €0.22kg/1000km taken, can be adjusted)  
- Commissioning year is assumed accurate based on available metadata in GeoJSON from infrastructure map, could be subsuquent delays announced. 
- Last-mile transport or off-network segments are not currently modelled  

---

## 8. Future Improvements
- Improve pipeline feature overcoming gaps in pipeline data to result in a more accurate routing system, network data could potentially be fixed manually or threshold could be tweaked to have a more accurate connection between points
- Add support for last-mile transport using road and potentially rail network models
- add support for ship transport and expand beyond europe 
- Include more detailed cost parameter settings, account for different pipeline types, cross border fees etc.  
- Improve robustness for ambiguous or poorly geocoded place names / include select on map feature  
- Integrate pipeline construction costs for hypothetical extensions  
- Incorporate modules for hydrogen production and purification costing  
  (potentially as part of a broader end-to-end hydrogen costing tool)  

---

## 9. Data Sources

- European Hydrogen Backbone Pipeline Data:  
  https://www.h2inframap.eu/  
  (GeoJSON extracted via ArcGIS API)

- Geocoding and City Location Data:  
  https://nominatim.openstreetmap.org/
