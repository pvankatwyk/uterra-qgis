
# uterra

**Version 0.1.0**

## Overview

The **uterra** QGIS Plugin is designed to streamline the permitting process for long-haul fiber optic installations by analyzing route intersections with cities, counties, protected areas, and railways. It uses the QGIS environment, several geospatial libraries, and optionally, OpenAI's GPT model to generate comprehensive permitting reports.

## Requirements

This plugin requires several Python packages, which need to be installed within QGIS's Python environment. Key dependencies include:
- `geopandas`
- `fastkml`
- `pygeoif`
- `lxml`
- `openai`
- `requests`
  
Because QGIS uses its own Python environment, packages must be installed within this environment. A `requirements.txt` file has been provided to streamline installation.

## Installing Dependencies in QGIS

### Step 1: Access the QGIS Python Environment
1. Open QGIS.
2. Go to `Plugins > Python Console`.
3. In the console, enter the following command to open the OSGeo shell, which allows you to install packages directly in the QGIS environment:

   ```python
   import os
   os.system('cmd.exe /K "C:\Program Files\QGIS <version>\OSGeo4W.bat"')
   ```
   
   Replace `<version>` with your QGIS version number (e.g., `QGIS 3.10`). For example, I use QGIS 3.26.2.

4. This will open a command prompt with the QGIS environment activated.

### Step 2: Install Required Packages Using `requirements.txt`

1. In the OSGeo4W shell, navigate to the directory where the plugin (and `requirements.txt`) is located.
2. Install the dependencies with the following command:

   ```bash
   pip install -r /path/to/requirements.txt
   ```

This will install all necessary packages in the QGIS Python environment.

### Step 3: Verify Installation in QGIS

After installing the dependencies:
1. Open the QGIS Python Console.
2. Run the following commands to confirm each package was installed correctly:

   ```python
   import geopandas
   import fastkml
   import pygeoif
   import lxml
   import openai
   import requests
   ```

   If there are no errors, the environment is correctly set up.

## Installation of the Plugin

1. Download this repository as a ZIP file.
2. Go to `Plugins > Manage and Install Plugins` in QGIS.
3. Click `Install from ZIP` and select the zipped plugin.
4. On you plugin bar, select the UTerra plugin (blue box). If not visible, restart QGIS to activate the plugin.

## Shapefile Datasets
Data used for this plugin can be downloaded at this link: [uterra-qgis-data](https://drive.google.com/drive/folders/1--1GoFPEK6_jHs1Soylp6cJwgD4IcJEl?usp=drive_link). This includes the US Census Beureau TIGER shapefiles for US cities and counties, the USGS PADUS dataset for protected areas, and US Department of Transportation Rail Line shapefiles. While any well-conditioned shapefile would work, all testing was done on these datasets.

## Usage


1. **Open the Plugin**: Start the UTerra Permitting Tool in QGIS. A dialog window will appear with various fields and options to input your data.

2. **Select Files**:
   - **Route File**: Use the dropdown next to "Select Route File" to choose the line shapefile or KMZ file representing the fiber optic route. This file is critical for determining intersecting locations.
   - **City, County, PADUS, and Railway Shapefiles**: Choose the respective shapefiles for cities, counties, protected areas (PADUS), and railways. These files should be loaded into your active QGIS session to allow the plugin to analyze intersections along the route.
   
3. **Set Output Path**:
   - Use the "Select Output Path" field to specify where the generated permitting report should be saved. You can enter a path directly or use the "Browse" button to select a directory.

4. **Optionally Use LLM for Permitting Summaries**:
   - If you want the permitting report to include an AI-generated summary with links and additional permitting information for each intersected area, enter your OpenAI API key in the "OpenAI API Key" field.
   - Check the "Use LLM?" box to enable this feature. The generated report will include extra contextual information where applicable, leveraging GPT.

5. **Generate the Report**:
   - Once all required fields are filled, click the **Generate Permit Report** button at the bottom of the dialog. The plugin will analyze the route’s intersections with the selected shapefiles and generate a Markdown report. This report will contain:
     - **Cities and Counties**: A list of cities and counties the route intersects, along with contact information and permitting department links (if the LLM option is enabled).
     - **Protected Areas (PADUS)**: Any protected areas crossed by the route, specifying required permissions or special considerations.
     - **Railway Crossings**: Details on railway crossings, including ownership, track rights, and contact information.

6. **View the Output**:
   - Navigate to the specified output path to find the `permit_report.md` file. This report can be opened with any Markdown viewer or text editor.

### Note:
The optional LLM feature uses OpenAI’s GPT to generate detailed permitting summaries. If desired, this can be replaced with other LLMs in the future, but GPT is currently integrated for ease of use and remote hosting advantages.


## Troubleshooting

### Common Issues

- **OSGeo Environment Issues**: If you encounter issues with installing packages, ensure you are using the OSGeo shell provided by QGIS.
- **Dependency Conflicts**: QGIS environments can sometimes have specific versions of libraries. Refer to the `requirements.txt` file to check installed versions and resolve any conflicts.
- **GPT Integration**: If the outputted report does not contain any links or extra information, likely the API key you provided is incorrect. If it is correct, close out the plugin and try again.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Development
This project is under active development. Please refer to the master branch for the most up-to-date releast of the uterra plugin. Feel free to reach out (pvankatwyk@gmail.com) for more information or bug reporting.
