import os
import streamlit as st
import pandas as pd
import numpy as np
import folium
import plotly.express as px
from pymongo import MongoClient
from dotenv import load_dotenv

# Set page configuration
st.set_page_config(
    page_title="Global Earthquake Clustering Dashboard",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium White Mode Theme & text visibility overrides
st.markdown("""
    <style>
    /* Global Background and text color overrides */
    .stApp {
        background-color: #fcfcfc !important;
        color: #2D3748 !important;
    }
    
    /* Ensure all headers, paragraphs, and standard text elements are dark gray */
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #2D3748 !important;
    }
    
    /* Sidebar text color overrides */
    section[data-testid="stSidebar"] {
        background-color: #f7fafc !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] .st-ae, 
    section[data-testid="stSidebar"] .st-af, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span {
        color: #2D3748 !important;
        font-weight: 500;
    }

    /* Target widget labels specifically */
    div[data-testid="stWidgetLabel"] p {
        color: #2D3748 !important;
        font-weight: 600 !important;
    }

    /* KPI card styles */
    .kpi-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        text-align: center;
        margin-bottom: 15px;
    }
    .kpi-title {
        font-size: 0.9rem;
        color: #718096 !important;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 2.2rem;
        color: #2B6CB0 !important;
        font-weight: 800;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

# MongoDB connection configuration with fallback
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://dbEarthquake:kenzoiscute@earthquake.474hrso.mongodb.net/")
if "dbEarthquake" not in MONGO_URI and "kenzoiscute" not in MONGO_URI:
    MONGO_URI = "mongodb+srv://dbEarthquake:kenzoiscute@earthquake.474hrso.mongodb.net/"

MONGO_DB = "earthquake_db"

@st.cache_resource
def get_mongo_client():
    return MongoClient(MONGO_URI)

# Helper function to load data from MongoDB
@st.cache_data(ttl=600) # Cache for 10 minutes to save bandwidth
def load_collection_data(collection_name):
    try:
        client = get_mongo_client()
        db = client[MONGO_DB]
        collection = db[collection_name]
        
        cursor = collection.find({}, {
            "_id": 0, "time": 1, "place": 1, "country": 1, 
            "latitude": 1, "longitude": 1, "depth": 1, "mag": 1, 
            "kmeans_cluster": 1, "bisect_cluster": 1, "quake_count": 1,
            "avg_depth": 1, "avg_mag": 1, "max_mag": 1
        })
        df = pd.DataFrame(list(cursor))
        if not df.empty and 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Gagal menghubungkan ke database: {e}")
        return pd.DataFrame()

# Load datasets
spatial_df = load_collection_data("kmeans_results_emsc")
hazard_df = load_collection_data("kmeans_hazard_results_emsc")
country_risk_df = load_collection_data("kmeans_country_risk_results_emsc")

# Navigation Sidebar (No Emojis, Clean UI)
st.sidebar.title("Navigasi Analisis")
menu = st.sidebar.radio(
    "Pilih Halaman Visualisasi:",
    [
        "Ringkasan & Tren Seismik", 
        "Peta Zona Rawan Spasial (Ring of Fire)", 
        "Peta & Profil Bahaya Gempa (Hazard)",
        "Peta & Profil Risiko Negara (Country Risk)"
    ]
)

# Shared Filters in Sidebar (only for map pages)
if menu != "Ringkasan & Tren Seismik":
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filter Dinamis Peta")
    
    # Check if we have data to set filter range
    min_mag, max_mag = 2.5, 9.5
    min_depth, max_depth = 0.0, 700.0
    
    ref_df = spatial_df
    if not ref_df.empty:
        min_mag = float(ref_df['mag'].min())
        max_mag = float(ref_df['mag'].max())
        min_depth = float(ref_df['depth'].min())
        max_depth = float(ref_df['depth'].max())
        
    mag_filter = st.sidebar.slider("Rentang Magnitudo (Mag):", min_value=min_mag, max_value=max_mag, value=(min_mag, max_mag), step=0.1)
    depth_filter = st.sidebar.slider("Rentang Kedalaman (Depth km):", min_value=min_depth, max_value=max_depth, value=(min_depth, max_depth), step=5.0)

# Colors for mapping clusters
SPATIAL_COLORS = ['#e53e3e', '#3182ce', '#38a169', '#dd6b20', '#805ad5', '#d69e2e', '#319795', '#b7791f']
HAZARD_INFO = {
    0: {"label": "Dangkal & Lemah (Shallow & Weak)", "color": "#3182ce", "desc": "Kedalaman < 70 km, kekuatan < 4.0. Gempa kecil harian, risiko rendah."},
    1: {"label": "Dangkal & Kuat (Shallow & Strong)", "color": "#e53e3e", "desc": "Kedalaman < 70 km, kekuatan > 5.5. Gempa merusak permukaan, potensi tsunami jika di laut."},
    2: {"label": "Menengah & Sedang (Intermediate & Moderate)", "color": "#dd6b20", "desc": "Kedalaman 70-300 km, kekuatan 4.0-5.5. Terasa getaran sedang di darat."},
    3: {"label": "Dalam & Kuat (Deep & Strong)", "color": "#d69e2e", "desc": "Kedalaman > 300 km, kekuatan > 5.5. Getaran meluas ke wilayah jauh, tetapi aman untuk permukaan."}
}

COUNTRY_RISK_INFO = {
    0: {"label": "Risiko Ekstrem (Extreme Risk)", "color": "#e53e3e", "desc": "Frekuensi gempa sangat tinggi dan kekuatan rata-rata besar (contoh: Indonesia, Chile)."},
    1: {"label": "Risiko Sedang (Moderate Risk)", "color": "#dd6b20", "desc": "Frekuensi gempa sedang dengan kekuatan menengah (contoh: Turkey, Greece)."},
    2: {"label": "Subduksi Dalam (Deep Tectonic Risk)", "color": "#805ad5", "desc": "Aktivitas gempa berkedalaman tinggi, jarang berdampak fatal ke permukaan."},
    3: {"label": "Risiko Rendah (Low Risk)", "color": "#38a169", "desc": "Sangat jarang mengalami gempa dan kekuatannya relatif sangat kecil."}
}

# --- PAGE 1: GENERAL METRICS & TRENDS ---
if menu == "Ringkasan & Tren Seismik":
    st.title("Ringkasan & Tren Seismik (EMSC)")
    st.write("Visualisasi analisis data awal (EDA) kejadian gempa bumi global untuk tahun 2025.")
    
    if spatial_df.empty:
        st.warning("Data kosong di MongoDB. Pastikan pipeline Spark Anda sudah dijalankan.")
    else:
        # KPI Cards Layout
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        with kpi1:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Total Kejadian Gempa</div>
                    <div class="kpi-value">{len(spatial_df):,}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with kpi2:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Magnitudo Terbesar</div>
                    <div class="kpi-value">{spatial_df['mag'].max():.1f}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with kpi3:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Negara Terdampak</div>
                    <div class="kpi-value">{spatial_df['country'].nunique()}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with kpi4:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Rata-rata Kedalaman</div>
                    <div class="kpi-value">{spatial_df['depth'].mean():.1f} km</div>
                </div>
            """, unsafe_allow_html=True)
            
        # Top Countries and Trends Plotly Layout
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("10 Negara Paling Aktif Seismik")
            top_countries = spatial_df['country'].value_counts().head(10).reset_index()
            top_countries.columns = ['Negara', 'Jumlah Gempa']
            fig_country = px.bar(
                top_countries, x='Jumlah Gempa', y='Negara', orientation='h',
                color='Jumlah Gempa', color_continuous_scale='Reds',
                labels={'Jumlah Gempa': 'Jumlah Kejadian Gempa', 'Negara': 'Wilayah/Negara'}
            )
            fig_country.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                font=dict(color='#2D3748'),
                xaxis=dict(gridcolor='#e2e8f0', title_font=dict(color='#2D3748'), tickfont=dict(color='#2D3748')),
                yaxis_title_font=dict(color='#2D3748'),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            st.plotly_chart(fig_country, use_container_width=True)
            
        with chart_col2:
            st.subheader("Tren Kejadian Gempa Bulanan (2025)")
            spatial_df['month'] = spatial_df['time'].dt.to_period('M')
            monthly_counts = spatial_df.groupby('month').size().reset_index(name='Jumlah Gempa')
            monthly_counts['Bulan'] = monthly_counts['month'].dt.strftime('%b %Y')
            
            fig_trend = px.line(
                monthly_counts, x='Bulan', y='Jumlah Gempa', markers=True,
                labels={'Jumlah Gempa': 'Frekuensi Gempa'}
            )
            fig_trend.update_traces(line_color='#2B6CB0', marker_color='#2B6CB0', line_width=3)
            fig_trend.update_layout(
                font=dict(color='#2D3748'),
                xaxis=dict(gridcolor='#e2e8f0', title_font=dict(color='#2D3748'), tickfont=dict(color='#2D3748')),
                yaxis=dict(gridcolor='#e2e8f0', title_font=dict(color='#2D3748'), tickfont=dict(color='#2D3748')),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            st.plotly_chart(fig_trend, use_container_width=True)

# --- PAGE 2: SPATIAL RING OF FIRE MAP ---
elif menu == "Peta Zona Rawan Spasial (Ring of Fire)":
    st.title("Peta Zona Rawan Spasial (Ring of Fire)")
    st.write("Mengelompokkan gempa berdasarkan lokasi geografis 3D (x, y, z) untuk memetakan batas lempeng sabuk gempa bumi global.")
    
    if spatial_df.empty:
        st.warning("Data spasial kosong. Silakan jalankan notebook `03_data_analysis.ipynb`.")
    else:
        # Apply filters
        filtered_df = spatial_df[
            (spatial_df['mag'] >= mag_filter[0]) & (spatial_df['mag'] <= mag_filter[1]) &
            (spatial_df['depth'] >= depth_filter[0]) & (spatial_df['depth'] <= depth_filter[1])
        ]
        
        st.write(f"Menampilkan **{len(filtered_df):,}** gempa sesuai filter.")
        
        # Sampling mapping points to avoid crashing the browser
        sample_size = min(3000, len(filtered_df))
        if sample_size > 0:
            map_data = filtered_df.sample(n=sample_size, random_state=42)
            
            # Map Initialization
            m = folium.Map(location=[0, 115], zoom_start=3, tiles="CartoDB positron")
            
            for _, row in map_data.iterrows():
                cluster = int(row['kmeans_cluster'])
                color = SPATIAL_COLORS[cluster % len(SPATIAL_COLORS)]
                
                popup_text = f"""
                <b>Lokasi:</b> {row['place']}<br>
                <b>Negara:</b> {row['country']}<br>
                <b>Magnitudo:</b> {row['mag']:.2f}<br>
                <b>Kedalaman:</b> {row['depth']:.1f} km<br>
                <b>Klaster:</b> {cluster}
                """
                
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=max(3, row['mag'] * 1.5),
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.6,
                    popup=folium.Popup(popup_text, max_width=300)
                ).add_to(m)
                
            st.components.v1.html(m._repr_html_(), height=600)
            
            # Legend mapping
            st.markdown("### Keterangan Klaster Lokasi (Spasial)")
            cols = st.columns(4)
            for idx in range(8):
                with cols[idx % 4]:
                    color = SPATIAL_COLORS[idx]
                    st.markdown(f"<span style='color:{color}; font-size:1.5rem;'>■</span> **Klaster {idx}**", unsafe_allow_html=True)
        else:
            st.info("Tidak ada data gempa bumi pada rentang filter ini.")

# --- PAGE 3: HAZARD PROFILING MAP ---
elif menu == "Peta & Profil Bahaya Gempa (Hazard)":
    st.title("Peta & Profil Bahaya Gempa (Hazard)")
    st.write("Mengklasifikasikan gempa bumi berdasarkan karakteristik parameter fisik patahan (kedalaman & magnitudo) secara global.")
    
    if hazard_df.empty:
        st.warning("Data hazard kosong. Silakan jalankan notebook `03_data_analysis_hazard.ipynb`.")
    else:
        # Apply filters
        filtered_df = hazard_df[
            (hazard_df['mag'] >= mag_filter[0]) & (hazard_df['mag'] <= mag_filter[1]) &
            (hazard_df['depth'] >= depth_filter[0]) & (hazard_df['depth'] <= depth_filter[1])
        ]
        
        st.write(f"Menampilkan **{len(filtered_df):,}** gempa sesuai filter.")
        
        # Left map, right scatter plot layout
        map_col, chart_col = st.columns([3, 2])
        
        with map_col:
            st.subheader("Sebaran Wilayah Gempa per Profil Bahaya")
            sample_size = min(3000, len(filtered_df))
            if sample_size > 0:
                map_data = filtered_df.sample(n=sample_size, random_state=42)
                m = folium.Map(location=[0, 115], zoom_start=3, tiles="CartoDB positron")
                
                for _, row in map_data.iterrows():
                    cluster = int(row['kmeans_cluster'])
                    info = HAZARD_INFO.get(cluster, {"color": "gray", "label": "Unknown"})
                    color = info["color"]
                    
                    popup_text = f"""
                    <b>Lokasi:</b> {row['place']}<br>
                    <b>Negara:</b> {row['country']}<br>
                    <b>Magnitudo:</b> {row['mag']:.2f}<br>
                    <b>Kedalaman:</b> {row['depth']:.1f} km<br>
                    <b>Kategori Bahaya:</b> {info['label']}
                    """
                    
                    folium.CircleMarker(
                        location=[row['latitude'], row['longitude']],
                        radius=max(3, row['mag'] * 1.5),
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.6,
                        popup=folium.Popup(popup_text, max_width=300)
                    ).add_to(m)
                    
                st.components.v1.html(m._repr_html_(), height=550)
            else:
                st.info("Tidak ada data gempa bumi pada rentang filter ini.")
                
        with chart_col:
            st.subheader("Hubungan Magnitudo vs Kedalaman")
            if not filtered_df.empty:
                plot_data = filtered_df.copy()
                plot_data['Kategori Bahaya'] = plot_data['kmeans_cluster'].map(lambda x: HAZARD_INFO.get(int(x), {"label": "Unknown"})["label"])
                
                fig_scatter = px.scatter(
                    plot_data.sample(n=min(5000, len(plot_data)), random_state=42),
                    x='mag', y='depth', color='Kategori Bahaya',
                    color_discrete_map={v['label']: v['color'] for k, v in HAZARD_INFO.items()},
                    labels={'mag': 'Magnitudo', 'depth': 'Kedalaman (km)'},
                    opacity=0.7
                )
                fig_scatter.update_layout(
                    yaxis_autorange="reverse", # Reverse Y-axis (depth points downward)
                    font=dict(color='#2D3748'),
                    xaxis=dict(gridcolor='#e2e8f0', title_font=dict(color='#2D3748'), tickfont=dict(color='#2D3748')),
                    yaxis=dict(gridcolor='#e2e8f0', title_font=dict(color='#2D3748'), tickfont=dict(color='#2D3748')),
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("Tidak ada data untuk mem-plot grafik.")
                
        # Hazard Description Box Table
        st.markdown("### Deskripsi & Karakteristik Profil Bahaya Seismik")
        kpi_desc_cols = st.columns(4)
        for cluster_id, info in HAZARD_INFO.items():
            with kpi_desc_cols[cluster_id]:
                st.markdown(f"""
                <div style="background-color:#ffffff; padding:15px; border-radius:10px; border-left: 6px solid {info['color']}; box-shadow: 0 2px 4px rgba(0,0,0,0.05); height: 100%;">
                    <strong style="color:#2D3748; font-size:1.05rem;">{info['label']}</strong><br>
                    <span style="color:#718096; font-size:0.85rem; font-style:italic;">{info['desc']}</span>
                </div>
                """, unsafe_allow_html=True)

# --- PAGE 4: COUNTRY RISK MAP & PROFILING ---
elif menu == "Peta & Profil Risiko Negara (Country Risk)":
    st.title("Peta & Profil Risiko Negara (Country Risk)")
    st.write("Mengelompokkan negara-negara di dunia berdasarkan total frekuensi kejadian, rata-rata kedalaman, rata-rata magnitudo, dan magnitudo maksimum gempa bumi.")
    
    if country_risk_df.empty:
        st.warning("Data Country Risk kosong. Pastikan Anda sudah menjalankan notebook `03_data_analysis_country_risk.ipynb`.")
    else:
        events_df = spatial_df.copy()
        
        merged_events = pd.merge(
            events_df, 
            country_risk_df[['country', 'kmeans_cluster']], 
            on='country', 
            how='inner', 
            suffixes=('', '_country')
        )
        
        # Apply filters
        filtered_df = merged_events[
            (merged_events['mag'] >= mag_filter[0]) & (merged_events['mag'] <= mag_filter[1]) &
            (merged_events['depth'] >= depth_filter[0]) & (merged_events['depth'] <= depth_filter[1])
        ]
        
        st.write(f"Menampilkan **{len(filtered_df):,}** kejadian gempa yang terjadi di negara-negara terklaster.")
        
        # Map and scatter plot layout
        map_col, chart_col = st.columns([3, 2])
        
        with map_col:
            st.subheader("Sebaran Gempa Berdasarkan Tingkat Risiko Negara")
            sample_size = min(3000, len(filtered_df))
            if sample_size > 0:
                map_data = filtered_df.sample(n=sample_size, random_state=42)
                m = folium.Map(location=[0, 115], zoom_start=3, tiles="CartoDB positron")
                
                for _, row in map_data.iterrows():
                    cluster = int(row['kmeans_cluster_country'])
                    info = COUNTRY_RISK_INFO.get(cluster, {"color": "gray", "label": "Unknown"})
                    color = info["color"]
                    
                    popup_text = f"""
                    <b>Lokasi:</b> {row['place']}<br>
                    <b>Negara:</b> {row['country']}<br>
                    <b>Kategori Risiko Negara:</b> {info['label']}<br>
                    <b>Magnitudo Gempa:</b> {row['mag']:.2f}<br>
                    <b>Kedalaman:</b> {row['depth']:.1f} km
                    """
                    
                    folium.CircleMarker(
                        location=[row['latitude'], row['longitude']],
                        radius=max(3, row['mag'] * 1.5),
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.6,
                        popup=folium.Popup(popup_text, max_width=300)
                    ).add_to(m)
                    
                st.components.v1.html(m._repr_html_(), height=550)
            else:
                st.info("Tidak ada data gempa pada rentang filter ini.")
                
        with chart_col:
            st.subheader("Klasterisasi Negara (Frekuensi vs Rata-rata Magnitudo)")
            if not country_risk_df.empty:
                plot_data = country_risk_df.copy()
                plot_data['Kategori Risiko'] = plot_data['kmeans_cluster'].map(lambda x: COUNTRY_RISK_INFO.get(int(x), {"label": "Unknown"})["label"])
                
                fig_scatter = px.scatter(
                    plot_data,
                    x='quake_count', y='avg_mag', color='Kategori Risiko',
                    hover_name='country',
                    color_discrete_map={v['label']: v['color'] for k, v in COUNTRY_RISK_INFO.items()},
                    labels={'quake_count': 'Jumlah Gempa Setahun', 'avg_mag': 'Rata-rata Magnitudo'},
                    size='max_mag',
                    size_max=30,
                    opacity=0.8
                )
                fig_scatter.update_layout(
                    font=dict(color='#2D3748'),
                    xaxis=dict(gridcolor='#e2e8f0', title_font=dict(color='#2D3748'), tickfont=dict(color='#2D3748')),
                    yaxis=dict(gridcolor='#e2e8f0', title_font=dict(color='#2D3748'), tickfont=dict(color='#2D3748')),
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("Tidak ada data untuk mem-plot grafik.")
                
        # Country Risk Description Box Layout
        st.markdown("### Karakteristik Tingkat Risiko Gempa Negara")
        risk_cols = st.columns(4)
        for cluster_id, info in COUNTRY_RISK_INFO.items():
            with risk_cols[cluster_id]:
                st.markdown(f"""
                <div style="background-color:#ffffff; padding:15px; border-radius:10px; border-left: 6px solid {info['color']}; box-shadow: 0 2px 4px rgba(0,0,0,0.05); height: 100%;">
                    <strong style="color:#2D3748; font-size:1.05rem;">{info['label']}</strong><br>
                    <span style="color:#718096; font-size:0.85rem; font-style:italic;">{info['desc']}</span>
                </div>
                """, unsafe_allow_html=True)
