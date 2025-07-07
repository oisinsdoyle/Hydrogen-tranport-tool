import streamlit as st
import geopandas as gpd
import networkx as nx
import scipy.spatial
from shapely.geometry import LineString, MultiLineString, Point
from geopy.distance import geodesic
import numpy as np
from scipy.spatial import cKDTree
import folium
from geopy.geocoders import Nominatim

st.set_page_config(layout="wide")
st.title("Hydrogen Pipeline Route Planner")

# --- Load pipeline data ---
@st.cache_resource
def load_data():
    file_path = "Hydrogen backbone map Transmission data.json"
    #file_path = r"C:\Users\Oisín\OneDrive - National University of Ireland, Galway\Documents\Desktop\Hydrogen-Costing-Tool-python\Transport\Hydrogen backbone map Transmission data.json"
    pipelines = gpd.read_file(file_path)
    pipelines = pipelines.to_crs("EPSG:4326")
    return pipelines

pipelines = load_data()

# --- Build the graph (snapping) ---
@st.cache_resource
def build_graph(_pipelines, threshold=0.11):
    pipelines = _pipelines
    all_coords = set()
    for _, row in pipelines.iterrows():
        geom = row['geometry']
        if isinstance(geom, LineString):
            coords = [tuple(round(c, 6) for c in pt) for pt in geom.coords]
            all_coords.update(coords)
        elif isinstance(geom, MultiLineString):
            for line in geom.geoms:
                coords = [tuple(round(c, 6) for c in pt) for pt in line.coords]
                all_coords.update(coords)
    all_coords = list(all_coords)
    coord_array = np.array(all_coords)
    tree = cKDTree(coord_array)
    snapped = {}
    for idx, coord in enumerate(all_coords):
        if coord in snapped:
            continue
        idxs = tree.query_ball_point(coord, threshold)
        canonical = all_coords[idx]
        for i in idxs:
            snapped[all_coords[i]] = canonical
    G = nx.Graph()
    for _, row in pipelines.iterrows():
        geom = row['geometry']
        if isinstance(geom, LineString):
            coords = [snapped[tuple(round(c, 6) for c in pt)] for pt in geom.coords]
            for i in range(len(coords) - 1):
                start, end = coords[i], coords[i+1]
                dist = geodesic((start[1], start[0]), (end[1], end[0])).km
                G.add_edge(start, end, weight=dist)
        elif isinstance(geom, MultiLineString):
            for line in geom.geoms:
                coords = [snapped[tuple(round(c, 6) for c in pt)] for pt in line.coords]
                for i in range(len(coords) - 1):
                    start, end = coords[i], coords[i+1]
                    dist = geodesic((start[1], start[0]), (end[1], end[0])).km
                    G.add_edge(start, end, weight=dist)
    # Keep only the largest connected component
    largest_cc = max(nx.connected_components(G), key=len)
    G = G.subgraph(largest_cc).copy()
    return G

G = build_graph(pipelines)

# --- KDTree for snapping user input to graph nodes ---
node_list = list(G.nodes)
node_array = np.array(node_list)
node_tree = cKDTree(node_array)

def snap_to_graph_node(lon, lat, node_list, tree):
    dist, idx = tree.query([lon, lat])
    return tuple(node_list[idx])

# --- User input ---

# ... (your other imports and code) ...

st.sidebar.header("Input Coordinates or Place Name")

# Option to use coordinates or place name


input_mode = st.sidebar.radio("Input mode", ["Coordinates", "Place name"])


if input_mode == "Coordinates":
    start_lat = st.sidebar.number_input("Start Latitude", value=51.9244, format="%.6f")
    start_lon = st.sidebar.number_input("Start Longitude", value=4.4777, format="%.6f")
    end_lat = st.sidebar.number_input("End Latitude", value=49.199370, format="%.6f")
    end_lon = st.sidebar.number_input("End Longitude", value=6.674622, format="%.6f")
elif input_mode == "Place name":
    geolocator = Nominatim(user_agent="hydrogen_route_planner")
    start_place = st.sidebar.text_input("Start Place Name", value="Rotterdam")
    end_place = st.sidebar.text_input("End Place Name", value="Luxembourg")
    start_location = geolocator.geocode(start_place)
    end_location = geolocator.geocode(end_place)
    if start_location and end_location:
        start_lat, start_lon = start_location.latitude, start_location.longitude
        end_lat, end_lon = end_location.latitude, end_location.longitude
        st.sidebar.success(f"Start: {start_location.address} ({start_lat:.4f}, {start_lon:.4f})")
        st.sidebar.success(f"End: {end_location.address} ({end_lat:.4f}, {end_lon:.4f})")
    else:
        st.sidebar.warning("Could not geocode one or both place names.")
        start_lat = start_lon = end_lat = end_lon = None

if st.sidebar.button("Find Route"):
    # Save original user input locations
    user_start = (start_lat, start_lon)
    user_end = (end_lat, end_lon)
    start = snap_to_graph_node(start_lon, start_lat, node_list, node_tree)
    end = snap_to_graph_node(end_lon, end_lat, node_list, node_tree)

    try:
        path = nx.shortest_path(G, source=start, target=end, weight='weight')
        distance = nx.shortest_path_length(G, source=start, target=end, weight='weight')
        price = round(distance * 0.21 / 1000, 2)
        path_latlon = [(node[1], node[0]) for node in path]

        # Find traversed pipelines and commissioning years
        traversed_pipelines = set()
        commission_years = set()
        for i in range(len(path) - 1):
            segment = LineString([path[i], path[i+1]])
            for _, row in pipelines.iterrows():
                geom = row['geometry']
                if geom and geom.intersects(segment):
                    traversed_pipelines.add(row.get("Project_Na", "Unknown"))
                    try:
                        year = int(row.get("Commission", 0))
                        commission_years.add(year)
                    except (ValueError, TypeError):
                        continue
        if commission_years:
            route_available_year = max(commission_years)
        else:
            route_available_year = "Unknown"

        # --- Folium Map ---
        m = folium.Map(location=[start[1], start[0]], zoom_start=6)
        folium.GeoJson(pipelines, name="Pipelines", style_function=lambda x: {"color": "gray", "weight": 2}).add_to(m)

        # Dotted line from user input to snapped node (start)
        folium.PolyLine(
            locations=[user_start, (start[1], start[0])],
            color="blue",
            weight=3,
            opacity=0.7,
            dash_array="5, 10",
            tooltip="Snap to pipeline (start)"
        ).add_to(m)
        # Dotted line from user input to snapped node (end)
        folium.PolyLine(
            locations=[user_end, (end[1], end[0])],
            color="blue",
            weight=3,
            opacity=0.7,
            dash_array="5, 10",
            tooltip="Snap to pipeline (end)"
        ).add_to(m)

        folium.PolyLine(path_latlon, color="red", weight=5, opacity=0.8, tooltip="Shortest Path").add_to(m)
        folium.Marker([start[1], start[0]], popup="Snapped Start", icon=folium.Icon(icon='play', prefix='fa', color='green')).add_to(m)
        folium.Marker([end[1], end[0]], popup="Snapped End", icon=folium.Icon(icon='flag', prefix='fa', color='red')).add_to(m)
        folium.Marker(user_start, popup="User Start", icon=folium.Icon(icon='user', prefix='fa', color='blue')).add_to(m)
        folium.Marker(user_end, popup="User End", icon=folium.Icon(icon='user', prefix='fa', color='blue')).add_to(m)

        # Info box in corner
        info_html = f"""
        <div style="
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            background: white;
            border: 2px solid red;
            border-radius: 8px;
            padding: 12px 18px;
            font-size: 16pt;
            color: red;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
        ">
            <b>Total distance:</b> {distance:.2f} km<br>
            <b>Estimated transport cost:</b> €{price}/kg (2040 EHB)<br>
            <b>Route available from:</b> {route_available_year}
        </div>
        """
        m.get_root().html.add_child(folium.Element(info_html))

        # Display map
        folium_static = st.components.v1.html(m._repr_html_(), height=600)

        # Display details
        st.subheader("Route Details")
        st.write(f"**Total distance:** {distance:.2f} km")
        st.write(f"**Estimated cost:** €{price}/kg (2040 EHB)")
        st.write(f"**Route available from:** {route_available_year}")
        st.write("**Pipelines traversed:**")
        for name in traversed_pipelines:
            st.write(f"- {name}")

    except nx.NetworkXNoPath:
        st.error("No path found between the selected nodes.")
