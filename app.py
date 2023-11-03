import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium, folium_static
from pathlib import Path

# features to add:
# add "opening time" column in csv

CONTACT_EMAIL = "lihotim@connect.hku.hk"

# --- PATH SETTINGS ---
THIS_DIR = Path(__file__).parent if "__file__" in locals() else Path.cwd()
ASSETS_DIR = THIS_DIR / "assets"
STYLES_DIR = THIS_DIR / "styles"
CSS_FILE = STYLES_DIR / "main.css"

def load_css_file(css_file_path):
    with open(css_file_path) as f:
        return st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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
    page_title="香港素食餐廳大全 & 素食地圖",
    page_icon="🥗",
    layout="wide",  # You can choose "wide" or "centered"
    initial_sidebar_state="auto"  # You can choose "auto", "expanded", or "collapsed"
)
load_css_file(CSS_FILE)

df_veg = get_csv_data()
# print(df_veg)

# Get lists of districts
# HK_DISTRICTS = df_veg['hk_district'].unique().tolist()
HK_DISTRICTS = ['港島', '九龍', '新界', '離島']
DISTRICTS_HK_ISLAND = df_veg[df_veg['hk_district'] == '港島']['district'].unique().tolist()
DISTRICTS_KOWLOON = df_veg[df_veg['hk_district'] == '九龍']['district'].unique().tolist()
DISTRICTS_NT = df_veg[df_veg['hk_district'] == '新界']['district'].unique().tolist()
DISTRICTS_ISLANDS = df_veg[df_veg['hk_district'] == '離島']['district'].unique().tolist()

# print(HK_DISTRICTS)

NOTICE_TEXT = '''
    更新至2023年11月3日。「素食類型」如果查不到資料一律當「蛋奶素」，請自行向店家查詢。大部分資料來自Google及OpenRice，如有任何錯漏敬請見諒。   
    --- By Tim ---
'''

USER_GUIDE = '''
    使用方法：
    1. 點選【香港地區】。按綠色按鈕內的「X」可以移除該地區；按右邊的灰色「X」可以移除所有地區。按選擇欄任何位置可以選擇個別地區。
    2. 點選【地區】。按綠色按鈕內的「X」可以移除該地區；按右邊的灰色「X」可以移除所有地區。按選擇欄任何位置可以選擇個別地區。
    3. 表格會顯示合乎選擇條件的餐廳名單。
    4. 地圖會顯示所有合乎選擇條件餐廳的座標（綠色氣球）。點擊座標可以顯示該餐廳的詳細資料，以及是Openrice連結。
    5. 由於Google提供的座標未必完全準確，座標跟餐廳的實際位置可能會有幾個舖位的出入，請自行用地址查找餐廳。祝您用餐愉快！
'''

# Mainpage
st.title("🥗 香港素食餐廳大全 & 素食地圖")
st.info(NOTICE_TEXT)
st.divider()
st.markdown(USER_GUIDE)
st.divider()

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
if "離島" in selected_HK_district:
    selected_islands_district = st.multiselect(
        '選擇離島地區：',
        DISTRICTS_ISLANDS,
        default=DISTRICTS_ISLANDS,
    )

st.divider()

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
    
if "離島" in selected_HK_district:
    df_veg_islands = df_veg[df_veg['district'].isin(selected_islands_district)]
    df_veg_map.append(df_veg_islands)


if df_veg_map:
    df_veg_map = pd.concat(df_veg_map)
    # Remove unnecessary columns for the table
    df_veg_map_table = df_veg_map.drop(columns=["openrice_url", "cuisine", "latitude", "longitude"])
    if len(df_veg_map) > 0:
        restaurants_count = len(df_veg_map)
        st.subheader(f"找到{restaurants_count}個結果：")
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
        
        m = folium.Map(location=[df_veg_map.latitude.mean() + 0.08, df_veg_map.longitude.mean() - 0.02], 
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


st.divider()
st.header("有素食餐廳想告訴我們嗎？")
contact_form = f"""
    <form action="https://formsubmit.co/{CONTACT_EMAIL}" method="POST">
        <input type="hidden" name="_captcha" value="false">
        <input type="text" name="name" placeholder="您的名字" required>
        <input type="email" name="email" placeholder="您的電郵" required>
        <textarea name="message" placeholder="請輸入您的訊息"></textarea>
        <button type="submit" class="button">送出 ✉</button>
    </form>
    """
st.markdown(contact_form, unsafe_allow_html=True)