import geopandas as gpd
from fastkml import kml
from shapely.geometry import LineString, MultiLineString
import zipfile
import xml.etree.ElementTree as ET
import pygeoif


us_states_territories = {
    "01": "Alabama",
    "02": "Alaska",
    "04": "Arizona",
    "05": "Arkansas",
    "06": "California",
    "08": "Colorado",
    "09": "Connecticut",
    "10": "Delaware",
    "11": "District of Columbia",
    "12": "Florida",
    "13": "Georgia",
    "15": "Hawaii",
    "16": "Idaho",
    "17": "Illinois",
    "18": "Indiana",
    "19": "Iowa",
    "20": "Kansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "23": "Maine",
    "24": "Maryland",
    "25": "Massachusetts",
    "26": "Michigan",
    "27": "Minnesota",
    "28": "Mississippi",
    "29": "Missouri",
    "30": "Montana",
    "31": "Nebraska",
    "32": "Nevada",
    "33": "New Hampshire",
    "34": "New Jersey",
    "35": "New Mexico",
    "36": "New York",
    "37": "North Carolina",
    "38": "North Dakota",
    "39": "Ohio",
    "40": "Oklahoma",
    "41": "Oregon",
    "42": "Pennsylvania",
    "44": "Rhode Island",
    "45": "South Carolina",
    "46": "South Dakota",
    "47": "Tennessee",
    "48": "Texas",
    "49": "Utah",
    "50": "Vermont",
    "51": "Virginia",
    "53": "Washington",
    "54": "West Virginia",
    "55": "Wisconsin",
    "56": "Wyoming",
    "60": "American Samoa",
    "66": "Guam",
    "69": "Northern Mariana Islands",
    "72": "Puerto Rico",
    "74": "U.S. Minor Outlying Islands",
    "78": "Virgin Islands"
}

class Shapefile:
    def __init__(self, shapefile_path, crs="EPSG:4326", convert_crs=True):
        self.shapefile_path = shapefile_path
        self.crs = crs
        self.gdf = gpd.read_file(shapefile_path)
        self.gdf = self.gdf.set_crs(self.crs)
        
        if convert_crs:
            self.convert_crs(convert_crs) if isinstance(convert_crs, str) else self.convert_crs("EPSG:4326")
        
        # self.gdf['geometry'] = self.gdf['geometry'].simplify(tolerance=0.01, preserve_topology=True)
        self.gdf = self.gdf[self.gdf.is_valid]

    def convert_crs(self, crs):
        self.crs = crs
        self.gdf = self.gdf.to_crs(crs)
        
    def get_intersection(self, linefile, cols:list=None):
        linefile_gdf = linefile.gdf if (isinstance(linefile, LineKMZ) or isinstance(linefile, LineShapefile)) else linefile
        try:
            intersection = gpd.sjoin(linefile_gdf, self.gdf, predicate='intersects')
        except:
            self.gdf = self.gdf[self.gdf.is_valid]
            intersection = gpd.sjoin(linefile_gdf, self.gdf, predicate='intersects',)
        return intersection[cols] if cols else intersection

    
    def list_cols(self):
        return self.gdf.columns.tolist()
    

class CitiesShapefile(Shapefile):
    def __init__(self, shapefile_path, crs="EPSG:4326", convert_crs="EPSG:4326"):
        super().__init__(shapefile_path, crs, convert_crs)
        self.cols = None
        self.intersection = None
        
    def get_intersection(self, linefile, cols:list=["NAME", "layer"]):
        self.cols = cols
        self.intersection = super().get_intersection(linefile, cols)
        return self.intersection


class CountiesShapefile(Shapefile):
    def __init__(self, shapefile_path, crs="EPSG:4269", convert_crs="EPSG:4326"):
        super().__init__(shapefile_path, crs, convert_crs)
        self.cols = None
        self.intersection = None
        
    def get_intersection(self, linefile, cols:list=['NAME', 'STATEFP']):
        self.cols = cols
        self.intersection = super().get_intersection(linefile, cols)
        self.intersection['STATEFP'] = self.intersection['STATEFP'].map(us_states_territories)
        return self.intersection
        
      
      
class PADUSShapefile(Shapefile):
    def __init__(self, shapefile_path, crs="EPSG:3857", convert_crs="EPSG:4326"):
        super().__init__(shapefile_path, crs, convert_crs)
        self.cols = None
        self.intersection = None
        
    def get_intersection(self, linefile, cols:list=['Unit_Nm']):
        self.cols = cols
        self.intersection = super().get_intersection(linefile, cols)
        return self.intersection
    
class RailShapefile(Shapefile):
    def __init__(self, shapefile_path, crs="EPSG:3857", convert_crs="EPSG:4326"):
        super().__init__(shapefile_path, crs, convert_crs)
        self.cols = None
        self.intersection = None
        
    def get_intersection(self, linefile, cols:list=["SUBDIV", "STATE", "RROWNER1", "TRKRGHTS1", "FRAARCID"]):
        self.cols = cols
        self.intersection = super().get_intersection(linefile, cols)
        return self.intersection
        
class KMZ:
  def __init__(self, kmz_path):
    self.kmz_path = kmz_path
    
class LineKMZ(KMZ):
    def __init__(self, kmz_path, convert_crs="EPSG:4326"):
        super().__init__(kmz_path)
        
        self.gdf = gpd.GeoDataFrame(geometry=self.extract_lines_from_kmz())
        
        if self.gdf.crs is None:
            self.gdf.set_crs("EPSG:4326", inplace=True)
        
        self.gdf = self.gdf.to_crs(convert_crs) if isinstance(convert_crs, str) else self.convert_crs("EPSG:4326")
        
    def extract_lines_from_kmz(self, kmz_path=None):
        
        kmz_path = kmz_path if kmz_path else self.kmz_path
        line_geometries = []
        
        with zipfile.ZipFile(kmz_path, 'r') as kmz:
            with kmz.open('doc.kml', 'r') as kml_file:
                k = kml.KML()
                try:
                    k.from_string(kml_file.read())
                    
                    # Recursively search for LineString or MultiLineString geometries in Placemarks
                    def find_lines(feature):
                        for subfeature in feature.features():
                            if hasattr(subfeature, 'features'):
                                find_lines(subfeature)
                            elif subfeature.__class__.__name__ == "Placemark":
                                geometry = subfeature.geometry
                                if isinstance(geometry, pygeoif.geometry.LineString):
                                    line_geometries.append(LineString(geometry.coords))
                                elif isinstance(geometry, pygeoif.geometry.MultiLineString):
                                    for line in geometry.geoms:
                                        line_geometries.append(LineString(line.coords))

                    for feature in k.features():
                        find_lines(feature)

                except ET.ParseError as e:
                    print("Error parsing KML file:", e)
                    return []

        return line_geometries
    
import geopandas as gpd
from shapely.ops import unary_union
from shapely.errors import TopologicalError

class LineShapefile:
    def __init__(self, shapefile_path):
        # Load the shapefile directly using GeoPandas
        self.gdf = self.load_shapefile(shapefile_path)
        self.clean_geometries()  # Clean invalid geometries upon loading

    def load_shapefile(self, shapefile_path):
        """Load a shapefile and return a GeoDataFrame with its geometries."""
        try:
            gdf = gpd.read_file(shapefile_path)
            return gdf
        except Exception as e:
            raise ValueError(f"Error loading shapefile: {e}")
        
    def clean_geometries(self):
        """Attempt to fix invalid geometries in the GeoDataFrame."""
        self.gdf["geometry"] = self.gdf["geometry"].apply(lambda geom: geom if geom.is_valid else geom.buffer(0))
        # Drop geometries that are still invalid
        self.gdf = self.gdf[self.gdf.is_valid]

    @property
    def unary_union(self):
        """Return the union of all geometries in the shapefile's GeoDataFrame."""
        return self.gdf.geometry.unary_union
