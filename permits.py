from classes import CitiesShapefile, CountiesShapefile, PADUSShapefile, RailShapefile, LineKMZ, LineShapefile
import openai
import os

def get_cities_intersection(shapefile_path, linefile, cols:list=["NAME", "layer"]):
    cities = CitiesShapefile(shapefile_path)
    return cities.get_intersection(linefile, cols)

def get_counties_intersection(shapefile_path, linefile, cols:list=['NAME', 'STATEFP']):
    counties = CountiesShapefile(shapefile_path)
    return counties.get_intersection(linefile, cols)

def get_padus_intersection(shapefile_path, linefile, cols=['Unit_Nm']):
    padus = PADUSShapefile(shapefile_path)
    return padus.get_intersection(linefile, cols)

def get_rail_intersection(shapefile_path, linefile, cols:list=["SUBDIV", "STATE", "RROWNER1", "TRKRGHTS1", "FRAARCID"]):
    rail = RailShapefile(shapefile_path)
    return rail.get_intersection(linefile, cols)

def identify_permitting_locations(line_path, cities_shapefile, counties_shapefile, padus_shapefile=None, rail_shapefile=None):
    if line_path.lower().endswith('.kmz'):
        linefile = LineKMZ(line_path)
    elif line_path.lower().endswith('.shp'):
        linefile = LineShapefile(line_path)
    else:
        raise ValueError("Unsupported file type for line layer. Please provide a .kmz or .shp file.")

    cities = get_cities_intersection(cities_shapefile, linefile) if cities_shapefile else None
    counties = get_counties_intersection(counties_shapefile, linefile) if counties_shapefile else None
    padus = get_padus_intersection(padus_shapefile, linefile) if padus_shapefile else None
    rail = get_rail_intersection(rail_shapefile, linefile) if rail_shapefile else None
    return cities, counties, padus, rail

def write_report(report_content, cities, counties, padus, rail, output_path="permit_report.md"):
    
    # Check and retrieve intersecting data
    cities = cities.get_intersection() if isinstance(cities, CitiesShapefile) else cities
    counties = counties.get_intersection() if isinstance(counties, CountiesShapefile) else counties
    padus = padus.get_intersection() if isinstance(padus, PADUSShapefile) else padus
    rail = rail.get_intersection() if isinstance(rail, RailShapefile) else rail
    
    # Convert intersecting data to lists for Markdown bullet points
    cities_list = cities["NAME"].tolist() if cities is not None else None
    counties_list = counties["NAME"].tolist() if counties is not None else None
    padus_list = padus["Unit_Nm"].tolist() if padus is not None else None
    rail_list = [
        f"{x['SUBDIV']}, {x['STATE']}, Owner: {x['RROWNER1']}, Track Rights: {x['TRKRGHTS1']}, FRA ID: {x['FRAARCID']}"
        for _, x in rail.iterrows()
    ] if rail is not None else None
    
    # Write to Markdown file
    with open(output_path, "w") as file:
        # Header
        file.write("# Permit Summary:\n\n")
        
        # Intersecting Locations Section
        file.write("### Intersecting Locations:\n\n")
        
        # Cities
        if cities is not None:
            file.write("**Cities:**\n")
            for city in cities_list:
                file.write(f"- {city}\n")
            file.write("\n")
        
        # Counties
        if counties is not None:
            file.write("**Counties:**\n")
            for county in counties_list:
                file.write(f"- {county}\n")
            file.write("\n")
        
        # PADUS Areas
        if padus is not None:
            file.write("**Protected Areas (PADUS):**\n")
            for area in padus_list:
                file.write(f"- {area}\n")
            file.write("\n")
        
        # Rail Intersections
        if rail is not None:
            file.write("**Rail Intersections:**\n")
            for rail_info in rail_list:
                file.write(f"- {rail_info}\n")
            file.write("\n")
        
        # Separator for the AI-generated content
        file.write("\n\n---\n\n")
        
        # AI-generated permitting report
        file.write(report_content)
    
    print(f"Report saved to {output_path}")


def ai_summary(api_key, cities, counties, padus, rail, to_md=True):
    # Ensure data compatibility
    cities = cities.get_intersection() if isinstance(cities, CitiesShapefile) else cities
    counties = counties.get_intersection() if isinstance(counties, CountiesShapefile) else counties
    padus = padus.get_intersection() if isinstance(padus, PADUSShapefile) else padus
    rail = rail.get_intersection() if isinstance(rail, RailShapefile) else rail
    
    # Generate report using OpenAI API
    try:
        client = openai.OpenAI(api_key=api_key)
    except Exception as e:
        raise ValueError(f"Error initializing OpenAI client: {e}")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a permitting specialist for long-haul fiber optic installations, responsible for ensuring only verified and working websites are referenced for permitting and regulatory information."},
            {"role": "user", "content": f"""I am conducting a long-haul fiber optic installation across multiple states and jurisdictions. Please create a highly detailed and well-organized permitting report that is divided into clear sections for **Cities**, **Counties**, **PADUS (Protected Areas)**, and **Railway Crossings**. If any of the information is not provided, a string will be given that says that it was not provided. In this case, state that the data was not probided and you can come up with an answer yourself. For each section:
            
- **Cities**: List each city that the installation route intersects, detailing the specific permitting departments or agencies to contact, along with relevant URLs for each department's main or permitting page. Provide essential contact information, including emails or phone numbers where available.

- **Counties**: List each intersecting county along the route, noting any specific considerations such as local regulations, environmental restrictions, or zoning requirements. Include relevant county permitting agencies with URLs and contact details. Provide links to official directories or permitting portals when direct URLs are unavailable. Prioritize verified links to main pages or high-level directories of official government and regulatory websites. Avoid creating specific URLs that may not exist; if a specific permit page isnt known, provide the main website link. 

- **Protected Areas (PADUS)**: Identify each protected area crossed, specifying the name and type (e.g., national forest, wildlife refuge, recreation area). Provide guidance on necessary permits or special permissions required for these lands, along with contacts and URLs for the respective federal, state, or local agencies that manage these areas.

- **Railway Crossings**: For each railway segment that the route intersects, detail the rail company (e.g., 'Owner: X') and provide essential contacts for obtaining crossing permits. Include any additional details like track rights, subdivision information, and any FRA-related identifiers, where available. If known, specify any unique procedural steps or fees related to the crossing permits.

Make sure each section is separated and clearly labeled. Provide details as bullet points or structured lists for easy reading, and prioritize clarity and accessibility of contact information and URLs. If information is unavailable, indicate 'information not found.' 

**Intersecting Locations**:
- **Cities**: {cities if cities is not None else "Cities information was not provided."}
- **Counties**: {counties if counties is not None else "Counties information was not provided."}
- **PADUS Areas**: {padus if padus is not None else "PADUS information was not provided."}
- **Rail Intersections**: {rail if rail is not None else "Rail information was not provided."}

Additionally, emphasize any considerations for environmental impact, protected species, or cultural sites that may require special permissions along the fiber optic route, especially within sensitive or restricted areas. Be sure to provide working links where you can."""
            }
        ]
    )
    
    response_content = response.choices[0].message.content
    if to_md:
        write_report(response_content, cities, counties, padus, rail)
    
    return response_content


def get_permit_summary(line_path, cities_path: str=None, counties_path: str=None, padus_path: str=None, rail_path: str=None, output_path: str=None, use_llm: bool=False, api_key: str=None):
    cities, counties, padus, rail = identify_permitting_locations(line_path, cities_path, counties_path, padus_path, rail_path)
    
    if use_llm and api_key is not None:
        report_content = ai_summary(api_key, cities, counties, padus, rail, to_md=False)
    else:
        report_content = ""
    
    if output_path:
        write_report(report_content, cities, counties, padus, rail, output_path)
        
    return report_content
