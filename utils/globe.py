import geopandas as gpd
import numpy as np
import plotly.graph_objects as go
import matplotlib.tri as mtri
from matplotlib.path import Path

class Globe:
    """
    A class to create a minimal 3D Plotly globe with solid continents (Mesh3d)
    and provide a method to update the scatter data points.
    """
    def __init__(self, shapefile_path='ui/assets/ne_50m_land.shp', globe_radius=1.0, land_color='rgb(100, 180, 100)'):
        """
        Initializes the globe, loading the land data and setting up the base figure.

        Args:
            shapefile_path (str): Path to the Natural Earth land shapefile (e.g., ne_50m_land.shp).
            globe_radius (float): Radius of the sphere in Plotly units.
            land_color (str): Solid color for the continents (e.g., 'rgb(R, G, B)').
        """
        self.R_globe = globe_radius
        self.R_land = self.R_globe * 1.001
        self.land_color = land_color
        self.shapefile_path = shapefile_path
        self.fig = None
        self.data_trace_id = 'custom_data_points'

        try:
            self.world_land = gpd.read_file(self.shapefile_path)
        except Exception as e:
            print(f"Error loading shapefile at {shapefile_path}: {e}")
            raise

    def _geographic_to_cartesian(self, lon_deg, lat_deg, R):
        """Converts degrees (lat, lon) to Cartesian (x, y, z) for a sphere of radius R."""
        lat_rad = np.deg2rad(lat_deg)
        lon_rad = np.deg2rad(lon_deg)
        
        x = R * np.cos(lat_rad) * np.cos(lon_rad)
        y = R * np.cos(lat_rad) * np.sin(lon_rad)
        z = R * np.sin(lat_rad)
        return x, y, z

    def _create_mesh3d_data(self):
        """
        Processes GeoDataFrame polygons, projects them to 3D, and triangulates 
        using stable local centering and triangle filtering.
        """
        total_x, total_y, total_z = [], [], []
        total_i, total_j, total_k = [], [], []
        vertex_offset = 0 
        
        for geom in self.world_land['geometry']:
            
            # Geometry extraction (simplified)
            if geom.geom_type == 'Polygon':
                coords = np.array(geom.exterior.coords)
            elif geom.geom_type == 'MultiPolygon' and geom.geoms:
                coords = np.array(geom.geoms[0].exterior.coords)
            else:
                continue
                
            lon_deg = coords[:, 0]
            lat_deg = coords[:, 1]

            # 1. Convert to 3D
            x, y, z = self._geographic_to_cartesian(lon_deg, lat_deg, self.R_land)

            # 2. Create stable local 2D coordinates for triangulation (CRITICAL FIX)
            lon_center = np.median(lon_deg)
            lat_center = np.median(lat_deg)
            lon_local = lon_deg - lon_center
            lat_local = lat_deg - lat_center

            try:
                # Triangulate
                tri_finder = mtri.Triangulation(lon_local, lat_local)
                
                # Filter (using Path to remove triangles outside the polygon)
                polygon_path = Path(np.column_stack([lon_local, lat_local]))
                tri_centers_lon = np.mean(lon_local[tri_finder.triangles], axis=1)
                tri_centers_lat = np.mean(lat_local[tri_finder.triangles], axis=1)
                is_inside = polygon_path.contains_points(np.column_stack([tri_centers_lon, tri_centers_lat]))
                faces = tri_finder.triangles[is_inside]
                
                if faces.size == 0:
                    continue

                # 3. Collect Data and Adjust Indices
                total_x.extend(x); total_y.extend(y); total_z.extend(z)
                i, j, k = faces[:, 0], faces[:, 1], faces[:, 2]
                
                total_i.extend(i + vertex_offset)
                total_j.extend(j + vertex_offset)
                total_k.extend(k + vertex_offset)
                
                vertex_offset += len(x)

            except Exception:
                continue

        return total_x, total_y, total_z, total_i, total_j, total_k

    def create_figure(self):
        """
        Creates and returns the initial Plotly figure object with continents and globe outline.
        """
        # --- Prepare Continent Mesh Data ---
        land_x, land_y, land_z, land_i, land_j, land_k = self._create_mesh3d_data()

        # --- Prepare Globe Surface Grid ---
        lats = np.linspace(-90, 90, 50)
        lons = np.linspace(-180, 180, 50)
        lon_grid, lat_grid = np.meshgrid(np.deg2rad(lons), np.deg2rad(lats))
        x_sphere, y_sphere, z_sphere = self._geographic_to_cartesian(
            np.rad2deg(lon_grid), np.rad2deg(lat_grid), self.R_globe
        )
        
        # Initialize Figure
        self.fig = go.Figure()

        # Add the continents using go.Mesh3d
        self.fig.add_trace(go.Mesh3d(
            x=land_x, y=land_y, z=land_z, 
            i=land_i, j=land_j, k=land_k,
            color=self.land_color, 
            opacity=1.0, 
            flatshading=True,
            name='Continents',
            showlegend=False,
            # Assigning an ID to prevent accidental removal
            uid='globe_continents_mesh' 
        ))

        # Add the minimalistic globe background (Ocean / Transparent Sphere)
        self.fig.add_trace(go.Surface(
            x=x_sphere, y=y_sphere, z=z_sphere,
            surfacecolor=np.zeros(z_sphere.shape),
            colorscale=[[0, 'rgb(220, 220, 255)'], [1, 'rgb(220, 220, 255)']],
            showscale=False,
            opacity=0.1,
            contours=dict(x=dict(show=False), y=dict(show=False), z=dict(show=False)),
            name='Ocean Background',
            uid='globe_ocean_surface'
        ))
        
        # Add a placeholder scatter trace for custom data (will be updated later)
        self.fig.add_trace(go.Scatter3d(
            x=[0], y=[0], z=[0], # Single point placeholder
            mode='markers',
            marker=dict(size=5, color='red', opacity=0.9),
            name='Data Points',
            uid=self.data_trace_id, 
        ))

        # Layout Customization (Minimalistic style)
        self.fig.update_layout(
            scene=dict(
                xaxis=dict(showgrid=False, zeroline=False, visible=False),
                yaxis=dict(showgrid=False, zeroline=False, visible=False),
                zaxis=dict(showgrid=False, zeroline=False, visible=False),
                aspectmode='cube',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            margin=dict(l=0, r=0, b=0, t=30),
            plot_bgcolor='rgb(28, 32, 40)',
            paper_bgcolor='rgb(28, 32, 40)',
        )
        
        return self.fig

    def update_scatter_data(self, lon_deg, lat_deg, marker_size=5, marker_color='rgb(69, 82, 75)', opacity=0.9):
        """
        Updates the scatter data points on the globe.

        Args:
            lon_deg (list/array): List of longitudes (degrees).
            lat_deg (list/array): List of latitudes (degrees).
            marker_size (int): Size of the scatter markers.
            marker_color (str): Color of the scatter markers.
            opacity (float): Opacity of the scatter markers.
        """
        if self.fig is None:
            raise RuntimeError("Figure must be created first. Call create_figure().")

        # Convert the new geographic data to Cartesian coordinates
        x_scatter, y_scatter, z_scatter = self._geographic_to_cartesian(
            lon_deg, lat_deg, self.R_land
        )
        
        # Find the index of the scatter data trace using its UID
        trace_index = next((i for i, trace in enumerate(self.fig.data) if trace.uid == self.data_trace_id), None)

        if trace_index is not None:
            # Use the data dictionary to update the existing trace
            self.fig.data[trace_index].update(
                x=x_scatter,
                y=y_scatter,
                z=z_scatter,
                marker=dict(
                    size=marker_size,
                    color=marker_color,
                    opacity=opacity
                )
            )
        else:
             print("Error: Scatter data placeholder trace not found.")