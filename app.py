import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium, folium_static




@st.cache_data
def get_csv_data():
    df_veg = pd.read_csv("./docs/hk_veg_restaurants_data.csv")
    df_veg.columns = ["hk_district", "district", "restaurant", "cuisine", "veg_type", "address", "latitude", "longitude", "openrice_url", "phone", "remarks"]
    
    # Set the "latitude" and "longitude" columns
    df_veg[['latitude', 'longitude']] = df_veg['latitude'].str.split(', ', expand=True)
    df_veg['latitude'] = pd.to_numeric(df_veg['latitude'])
    df_veg['longitude'] = pd.to_numeric(df_veg['longitude'])

    # Set the "phone" column
    df_veg['phone'] = df_veg['phone'].astype(str)
    df_veg['phone'] = df_veg['phone'].str[:8]
    df_veg['phone'] = df_veg['phone'].apply(lambda x: f"{x[:4]} {x[4:]}" if x else None)

    return df_veg

# Page config
st.set_page_config(
    page_title="香港素食餐廳大全",
    page_icon="🥗",
    layout="wide",  # You can choose "wide" or "centered"
    initial_sidebar_state="auto"  # You can choose "auto", "expanded", or "collapsed"
)

df_veg = get_csv_data()


# Get lists of districts
HK_DISTRICTS = df_veg['hk_district'].unique().tolist()
DISTRICTS_HK_ISLAND = df_veg[df_veg['hk_district'] == '港島']['district'].unique().tolist()
DISTRICTS_KOWLOON = df_veg[df_veg['hk_district'] == '九龍']['district'].unique().tolist()
DISTRICTS_NT = df_veg[df_veg['hk_district'] == '新界']['district'].unique().tolist()


# Mainpage
st.title("🥗 香港素食餐廳大全")

# 4 multiselects
selected_HK_district = st.multiselect(
    '選擇香港地區：',
    HK_DISTRICTS,
    default=HK_DISTRICTS,
)

if "港島" in selected_HK_district:
    selected_HK_island_district = st.multiselect(
        '選擇港島地區：',
        DISTRICTS_HK_ISLAND,
        default=DISTRICTS_HK_ISLAND,
    )
if "九龍" in selected_HK_district:
    selected_kowloon_district = st.multiselect(
        '選擇九龍地區：',
        DISTRICTS_KOWLOON,
        default=DISTRICTS_KOWLOON,
    )
if "新界" in selected_HK_district:
    selected_NT_district = st.multiselect(
        '選擇新界地區：',
        DISTRICTS_NT,
        default=DISTRICTS_NT,
    )


df_veg_map = []
if "港島" in selected_HK_district:
    df_veg_hk_island = df_veg[df_veg['district'].isin(selected_HK_island_district)]
    df_veg_map.append(df_veg_hk_island)

if "九龍" in selected_HK_district:
    df_veg_kowloon = df_veg[df_veg['district'].isin(selected_kowloon_district)]
    df_veg_map.append(df_veg_kowloon)

if "新界" in selected_HK_district:
    df_veg_NT = df_veg[df_veg['district'].isin(selected_NT_district)]
    df_veg_map.append(df_veg_NT)


if df_veg_map:
    df_veg_map = pd.concat(df_veg_map)
    # Remove unnecessary columns for the table
    df_veg_map_table = df_veg_map.drop(columns=["openrice_url", "cuisine", "latitude", "longitude"])
    if len(df_veg_map) > 0:
        restaurants_count = len(df_veg_map)
        st.write(f"（找到{restaurants_count}個結果）")
        st.dataframe(df_veg_map_table,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "hk_district": st.column_config.TextColumn("香港地區"),
                        "district": st.column_config.TextColumn("地區"),
                        "restaurant": st.column_config.TextColumn("餐廳名稱"),
                        "cuisine": st.column_config.TextColumn("菜式"),
                        "veg_type": st.column_config.TextColumn("素食種類"),
                        "address": st.column_config.TextColumn("地址"),
                        "openrice_url": st.column_config.TextColumn("Openrice連結"),
                        "phone": st.column_config.TextColumn("電話"),
                        "remarks": st.column_config.TextColumn("備註", width="large"),
        })

        # Show the map
        st.header(f"📍 香港素食地圖")
        
        m = folium.Map(location=[df_veg_map.latitude.mean(), df_veg_map.longitude.mean()], 
                        zoom_start=11, control_scale=True)

        # Loop through each row in the dataframe
        for i,row in df_veg_map.iterrows():
            # Setup the content of the popup
            remarks = f'<strong>備註: {row["remarks"]} </strong><br/>' if not pd.isna(row["remarks"]) else ''
            iframe = folium.IFrame(f'''
                                <strong>{row["district"]} - {row["restaurant"]} </strong><br/>
                                ------------------------------<br/>
                                菜式: {row["cuisine"]} <br/>
                                素食種類: {row["veg_type"]} <br/>
                                地址: {row["address"]}
                                <a href="https://www.google.com/maps/search/?api=1&query={row['latitude']},{row['longitude']}" target="_blank"> (查看地圖)</a><br/>
                                Openrice連結: <a href="{row["openrice_url"]}" target="_blank">(查看Openrice)</a> <br/>
                                電話: {row["phone"]} <br/>
                                {remarks}
                                ''')

            
            # Initialise the popup using the iframe
            popup = folium.Popup(iframe, min_width=300, max_width=300)
            
            # Add each row to the map
            folium.Marker(location=[row['latitude'], row['longitude']],
                  popup=popup,
                  icon=folium.Icon(color='green', icon="utensils", prefix='fa'),
                  c=row['restaurant']).add_to(m)

        st_data = folium_static(m, width=700)
        
    else:
        st.warning("找不到餐廳！")



# Method 2: streamlit-folium
# st.header("Method 2: streamlit-folium")
# m = folium.Map(location=[df_veg_map.latitude.mean(), df_veg_map.longitude.mean()], 
#                  zoom_start=11, control_scale=True)

# # Loop through each row in the dataframe
# for i,row in df_veg_map.iterrows():
#     # Setup the content of the popup
#     iframe = folium.IFrame(f'''
#                            地區: {row["district"]} <br/>
#                            餐廳名稱: {row["restaurant"]} <br/>
#                            菜式: {row["cuisine"]} <br/>
#                            素食種類: {row["veg_type"]} <br/>
#                            地址: {row["address"]} <br/>
#                            Openrice連結: <a href="{row["openrice_url"]}" target="_blank">Visit Openrice</a> <br/>
#                            電話: {row["phone"]} <br/>
#                            備註: {row["remarks"]} <br/>
#                         ''')

    
#     # Initialise the popup using the iframe
#     popup = folium.Popup(iframe, min_width=300, max_width=300)
    
#     # Add each row to the map
#     folium.Marker(location=[row['latitude'],row['longitude']],
#                   popup = popup, c=row['restaurant']).add_to(m)

# st_data = folium_static(m, width=700)


# Method 3: Plotly
# st.header("Method 3: Plotly")
# fig = px.scatter_mapbox(df_veg, 
#                         lat="latitude", 
#                         lon="longitude", 
#                         hover_name='restaurant', 
#                         zoom=10,
#                         )

# fig.update_layout(mapbox_style="open-street-map")
# fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# st.plotly_chart(fig)