import os
import sys
import geopandas as gpd
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, ColorBar, LinearColorMapper, Dropdown, CustomJS, BoxSelectTool, Div, HoverTool
from bokeh.palettes import Viridis256
from bokeh.layouts import column, row
from bokeh.transform import factor_cmap
from bokeh.tile_providers import get_provider, OSM, CARTODBPOSITRON, STAMEN_TERRAIN
from shapely.geometry import Polygon, MultiPolygon

# Function to get the absolute path to the data files
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Function to categorize emissions based on value thresholds
def categorize_emissions(value):
    if value < 100:
        return 'Green Usage'
    elif 100 <= value < 250:
        return 'Red Usage'
    else:
        return 'Black Usage'

def assign_emissions(buildings, column, area_column, floors_column, underground_floors_column, year_column):
    buildings[column] = buildings[column].fillna('기타')
    carbon_vals = {'공동주택' : 0.08, '공장' : 0.065, '관광휴게시설' : 0.114, '교육연구및복지시설' : 0.047, '교육연구시설' : 0.047,
               '교정및군사시설' : 0.059, '근린생활시설' : 0.080, '노유자시설' : 0.047, '단독주택' : 0.080,
               '동.식물 관련시설' : 0.059, '묘지관련시설' : 0.059, '문화및집회시설' : 0.065, '방송통신시설' : 0.065,
               '분뇨.쓰레기처리시설' : 0.095, '수련시설' : 0.059, '숙박시설' : 0.093, '업무시설' : 0.060,
               '운동시설' : 0.059, '운수시설' : 0.059, '위락시설' : 0.114, '위험물저장및처리시설' : 0.095,
               '의료시설' : 0.123, '자동차관련시설' : 0.046, '제1종근린생활시설' : 0.080, '제2종근린생활시설' : 0.080,
               '종교시설' : 0.032, '창고시설' : 0.046, '판매및영업시설' : 0.080, '판매시설' : 0.080, '기타' : 0.080
    }

    buildings[year_column] = pd.to_datetime(buildings[year_column], errors='coerce')
    buildings['year'] = buildings[year_column].dt.year

    # Add floors and multiply by area to get proportional value
    buildings['total_floors'] = buildings[floors_column] + buildings[underground_floors_column]
    buildings['proportional_area'] = buildings[area_column] * buildings['total_floors']

    # Initialize an empty dictionary for emission mapping
    emission_mapping = {}

    # Calculate emissions for each building and create emission mapping
    for building_type, carbon_value in carbon_vals.items():
        emission_mapping[building_type] = carbon_value

    # Calculate emissions for each building
    for idx, row in buildings.iterrows():
        year = row['year']
        
        if pd.isna(year): 
            constant_val = 1 
        elif year < 2000:
            constant_val = 0.015
        elif 2000 <= year < 2010:
            constant_val = 0.01
        else:
            constant_val = 0.005

        emissions = row['proportional_area'] * carbon_vals.get(row[column], 0.080) * (1 + constant_val)
        buildings.at[idx, 'emissions'] = emissions  

    buildings['usage_category'] = buildings['emissions'].apply(categorize_emissions)

    return buildings, emission_mapping


# Convert geometries to x and y lists for Bokeh
def get_coords(geometry):
    if isinstance(geometry, Polygon):
        x, y = geometry.exterior.xy
        return list(x), list(y)
    elif isinstance(geometry, MultiPolygon):
        x, y = [], []
        for poly in geometry:
            px, py = poly.exterior.xy
            x.extend(list(px) + [None])
            y.extend(list(py) + [None])
        return x, y
    
geumjeong_gu_path = resource_path('data/geumjeong_gu.shp')
carbon_emissions = gpd.read_file(geumjeong_gu_path).to_crs(epsg=3857)
carbon_emissions['x'], carbon_emissions['y'] = zip(*carbon_emissions['geometry'].apply(get_coords))
buildings, emission_mapping = assign_emissions(carbon_emissions, 'A9', 'A12', 'A26', 'A27', 'A13')
initial_total_emissions = sum(buildings['emissions'])
total_emissions_div = Div(text=f"Total Carbon Emissions: {initial_total_emissions:.2f} units")

buildings['green_roof'] = False

map_source = ColumnDataSource(data={
    'x': buildings['x'], 'y': buildings['y'],
    'emissions': buildings['emissions'], 'name': buildings['A9'],
    'proportional_area': buildings['proportional_area'],
    'green_roof': buildings['green_roof']
})

# Read and process absorption data
emissions_path = resource_path('data/AL_D194_26410_20240127.shp')
gdf_absorption = gpd.read_file(emissions_path, encoding='euc-kr')
filtered_gdf_absorption = gdf_absorption[gdf_absorption['A14'].isin(['개발제한구역', '자연녹지지역'])]
filtered_gdf_absorption = filtered_gdf_absorption.to_crs(epsg=3857)
filtered_gdf_absorption['area_sqm'] = filtered_gdf_absorption.geometry.area
filtered_gdf_absorption['area_ha'] = filtered_gdf_absorption['area_sqm'] / 10000
filtered_gdf_absorption['carbon_absorption'] = filtered_gdf_absorption['area_ha'] * 6.9
filtered_gdf_absorption['x'], filtered_gdf_absorption['y'] = zip(*filtered_gdf_absorption['geometry'].apply(get_coords))

absorption_source = ColumnDataSource(data={
    'x': filtered_gdf_absorption['x'], 'y': filtered_gdf_absorption['y'],
    'carbon_absorption': filtered_gdf_absorption['carbon_absorption'], 'name': filtered_gdf_absorption['A14']
})

# Create color mappers for emissions and absorption
emission_color_mapper = LinearColorMapper(palette=Viridis256[::-1], low=buildings['emissions'].min(), high=buildings['emissions'].max())
absorption_color_mapper = LinearColorMapper(palette=Viridis256, low=filtered_gdf_absorption['carbon_absorption'].min(), high=filtered_gdf_absorption['carbon_absorption'].max())

p_map = figure(title="Greenhouse gas emission and absorption in Geumjeong-gu, Busan", x_axis_type="mercator", y_axis_type="mercator",
               tools="pan,wheel_zoom,reset,hover", width=1450, height=950)
p_map.add_tile(get_provider(OSM))

# Add emissions and absorption patches
emission_renderer = p_map.patches('x', 'y', source=map_source, fill_color={'field': 'emissions', 'transform': emission_color_mapper}, line_color='black', line_width=0.5)
absorption_renderer = p_map.patches('x', 'y', source=absorption_source, fill_color={'field': 'carbon_absorption', 'transform': absorption_color_mapper}, line_color='black', line_width=0.5, fill_alpha=0.6)

# Add hover tools with the required information
hover_absorption = HoverTool(
    renderers=[absorption_renderer],
    tooltips=[
        ("Type", "Carbon Absorption"),
        ("Location", "@name"),
        ("Absorption (tons)", "@carbon_absorption")
    ]
)

hover_emissions = HoverTool(
    renderers=[emission_renderer],
    tooltips=[
        ("Type", "Carbon Emissions"),
        ("Building type", "@name"),
        ("Emissions (tons)", "@emissions")
    ]
)

p_map.add_tools(hover_absorption, hover_emissions)

# Explicitly add the BoxSelectTool
box_select = BoxSelectTool()
p_map.add_tools(box_select)

# Add color bars for emissions and absorption
emission_color_bar = ColorBar(color_mapper=emission_color_mapper, label_standoff=12, location=(0,0), title='Emissions Level')
absorption_color_bar = ColorBar(color_mapper=absorption_color_mapper, label_standoff=12, location=(0,0), title='Absorption Level')

p_map.add_layout(emission_color_bar, 'right')
p_map.add_layout(absorption_color_bar, 'right')

menu = [(value, value) for value in sorted(buildings['A9'].unique()) if value != 'NULL']
dropdown = Dropdown(label="Select new Building type", button_type="warning", menu=menu)
dropdown.js_on_event('menu_item_click', CustomJS(args={
    'source': map_source, 'total_div': total_emissions_div, 'emission_mapping': emission_mapping
}, code="""
    function categorize_emissions(value) {
        if (value < 100) 
            return 'Green Usage';
        else if (value < 250) 
            return 'Red Usage';
        else 
            return 'Black Usage';
    }

    var data = source.data;
    var f = cb_obj.item;
    var inds = source.selected.indices;
    var new_total = 0;
    var category_updates = {'Green Usage': 0, 'Red Usage': 0, 'Black Usage': 0};

    // Update building types and emissions
    for (var i = 0; i < inds.length; i++) {
        var idx = inds[i];
        var proportional_area = data['proportional_area'][idx];
        var carbon_val = emission_mapping[f];

        // Reset emissions to original value based on proportional_area and building type
        var old_building_type = data['name'][idx];
        data['emissions'][idx] = proportional_area * emission_mapping[old_building_type];

        // Calculate the new emission value based on the new building type
        data['name'][idx] = f;
        data['emissions'][idx] = proportional_area * carbon_val;

        // Check if green rooftop is applied and adjust emissions accordingly
        if (data['green_roof'][idx]) {
            data['emissions'][idx] -= 0.0035 * proportional_area;
        }
    }

    // Recalculate category counts and total emissions
    for (var i = 0; i < data['emissions'].length; i++) {
        var category = categorize_emissions(data['emissions'][i]);
        category_updates[category]++;
        new_total += data['emissions'][i];
    }

    // Update the total emissions display
    total_div.text = "Total Carbon Emissions: " + new_total.toFixed(2) + " units";

    source.change.emit();
    source.selected.indices = []; // Clear selection
"""))

green_roof_menu = Dropdown(label="Apply Green Rooftop", button_type="success", menu=[("Yes", "Yes"), ("No", "No")])
green_roof_menu = Dropdown(label="Apply Green Rooftop", button_type="success", menu=[("Yes", "Yes"), ("No", "No")])
green_roof_menu.js_on_event('menu_item_click', CustomJS(args={
    'source': map_source, 'total_div': total_emissions_div, 'emission_mapping': emission_mapping
}, code="""
    function categorize_emissions(value) {
        if (value < 100) 
            return 'Green Usage';
        else if (value < 250) 
            return 'Red Usage';
        else 
            return 'Black Usage';
    }

    var data = source.data;
    var inds = source.selected.indices;
    var new_total = 0;
    var category_updates = {'Green Usage': 0, 'Red Usage': 0, 'Black Usage': 0};
    var apply_green_roof = cb_obj.item === 'Yes';

    // Apply or remove green rooftop reduction
    for (var i = 0; i < inds.length; i++) {
        var idx = inds[i];
        var proportional_area = data['proportional_area'][idx];
        var current_emissions = emission_mapping[data['name'][idx]] * proportional_area;
        if (apply_green_roof) {
            current_emissions -= 0.0035 * proportional_area;
            data['green_roof'][idx] = true;
        } else {
            current_emissions += 0.0035 * proportional_area;
            data['green_roof'][idx] = false;
        }
        data['emissions'][idx] = current_emissions;
    }

    // Recalculate category counts and total emissions
    for (var i = 0; i < data['emissions'].length; i++) {
        var category = categorize_emissions(data['emissions'][i]);
        category_updates[category]++;
        new_total += data['emissions'][i];
    }

    // Update the total emissions display
    total_div.text = "Total Carbon Emissions: " + new_total.toFixed(2) + " units";

    source.change.emit();
    source.selected.indices = []; // Clear selection
"""))

# Load the population ratio data
population_ratio_path = resource_path('data/population_ratio.csv')
population_ratio_df = pd.read_csv(population_ratio_path)

# Create a ColumnDataSource for the new bar graph
population_source = ColumnDataSource(data={
    'dong': population_ratio_df['dong'],
    'popu_ratio': population_ratio_df['popu_ratio'],
    'old_ratio': population_ratio_df['old_ratio']
})

# Create a new combined line graph for popu_ratio and old_ratio
p_population_ratio = figure(title="Population and Old Ratio by Dong", x_axis_label='Dong', y_axis_label='Ratio',
                               x_range=population_ratio_df['dong'].tolist(), height=300, width=375)

p_population_ratio.line(x='dong', y='popu_ratio', source=population_source, line_width=2, color='blue', legend_label='거주 비율')
p_population_ratio.line(x='dong', y='old_ratio', source=population_source, line_width=2, color='green', legend_label='노인 증가율')

p_population_ratio.legend.title = 'Legend'
p_population_ratio.legend.location = 'top_left'
p_population_ratio.legend.click_policy = 'hide'

ssp_245_path = resource_path('data/ssp245.csv')
ssp_585_path = resource_path('data/ssp585.csv')
ssp_245 = pd.read_csv(ssp_245_path)
ssp_585 = pd.read_csv(ssp_585_path)

ssp245_src = ColumnDataSource(data={
    'ssp245_year': ssp_245['year'],
    'ssp245_tas': ssp_245['tas'],
    'ssp245_di': ssp_245['di']
})

ssp585_src = ColumnDataSource(data={
    'ssp585_year': ssp_585['year'],
    'ssp585_tas': ssp_585['tas'],
    'ssp585_di': ssp_585['di']
})

p_line1 = figure(title="SSP245 Data Over Time", x_axis_label='Year', y_axis_label='Temperature', height=300, width=375)
p_line1.line(x='ssp245_year', y='ssp245_tas', source=ssp245_src, color = 'blue', line_width=2,legend_label='tas')
p_line1.line(x='ssp245_year', y='ssp245_di', source=ssp245_src, color = 'green', line_width=2,legend_label='di')

p_line1.legend.title = 'Legend'
p_line1.legend.location = 'top_right'
p_line1.legend.click_policy = 'hide'

p_line2 = figure(title="SSP585 Data Over Time", x_axis_label='Year', y_axis_label='Temperature', height=300, width=375)
p_line2.line(x='ssp585_year', y='ssp585_tas', source=ssp585_src, color = 'blue', line_width=2,legend_label='tas')
p_line2.line(x='ssp585_year', y='ssp585_di', source=ssp585_src, color = 'green', line_width=2,legend_label='di')

p_line2.legend.title = 'Legend'
p_line2.legend.location = 'top_right'
p_line2.legend.click_policy = 'hide'

right_column = column(total_emissions_div, dropdown, green_roof_menu, p_population_ratio, p_line1, p_line2)
layout = row(p_map, right_column)

show(layout)