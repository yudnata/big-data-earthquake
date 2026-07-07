import os
import json
import streamlit as st
import pandas as pd
import numpy as np
import folium
import requests
import plotly.express as px
from pymongo import MongoClient
from dotenv import load_dotenv

# ── Tectonic Plates GeoJSON (cached globally) ──────────────────────────
_TECTONIC_GEOJSON_URL = "https://raw.githubusercontent.com/fraxen/tectonicplates/master/GeoJSON/PB2002_boundaries.json"

@st.cache_data(ttl=86400)
def _load_tectonic_plates():
    """Download and cache tectonic plate boundaries GeoJSON."""
    try:
        resp = requests.get(_TECTONIC_GEOJSON_URL, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None

def create_world_map(center=(10, 20), zoom=2):
    """Create a bounded Folium world map with tectonic plate boundary overlay."""
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="CartoDB positron",
        max_bounds=True,
        min_zoom=2,
        max_zoom=12,
    )
    # Restrict panning to world bounds so the map cannot be scrolled infinitely
    m.fit_bounds([[-60, -180], [75, 180]])

    # Add tectonic plate boundary lines
    plates_geojson = _load_tectonic_plates()
    if plates_geojson:
        folium.GeoJson(
            plates_geojson,
            name="Lempeng Tektonik",
            style_function=lambda _: {
                "color": "#dc2626",
                "weight": 1.8,
                "opacity": 0.7,
                "dashArray": "5 3",
            },
        ).add_to(m)
    return m

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
            "avg_depth": 1, "avg_mag": 1, "max_mag": 1,
            "hazard_cluster": 1, "cluster_name": 1
        })
        df = pd.DataFrame(list(cursor))
        if not df.empty and 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Gagal menghubungkan ke database: {e}")
        return pd.DataFrame()

# Load datasets from custom hazard collection (3 clusters: Risiko Rendah, Sedang, Tinggi)
spatial_df = load_collection_data("custom_hazard_results_emsc")
if not spatial_df.empty:
    if 'hazard_cluster' in spatial_df.columns:
        spatial_df['kmeans_cluster'] = spatial_df['hazard_cluster']
hazard_df = spatial_df.copy()
country_risk_df = load_collection_data("kmeans_country_risk_results_emsc")

# Navigation Sidebar (No Emojis, Clean UI)
st.sidebar.title("Navigasi Analisis")
menu = st.sidebar.radio(
    "Pilih Halaman Visualisasi:",
    [
        "Ringkasan & Tren Seismik", 
        "Peta Zona Rawan Spasial (Ring of Fire)", 
        "Klasifikasi Risiko Negara (Top 10)"
    ]
)



# Colors for mapping clusters
SPATIAL_COLORS = ['#e53e3e', '#3182ce', '#38a169', '#dd6b20', '#805ad5', '#d69e2e', '#319795', '#b7791f']

# Warna dan deskripsi per kategori bahaya (3 tingkat bahaya)
_HAZARD_PALETTE = [
    {"key": "rendah",  "color": "#3b82f6", "label": "Risiko Rendah",
     "desc": "Gempa minor (magnitudo < 4.0) di semua kedalaman, atau gempa dalam (> 300 km) dengan magnitudo sedang. Sangat aman dan hampir tidak menimbulkan dampak permukaan."},
    {"key": "sedang",  "color": "#f97316", "label": "Risiko Sedang",
     "desc": "Gempa kekuatan sedang (4.0 - 5.5 SR) di kedalaman dangkal/menengah (depth <= 300 km), atau gempa berkekuatan tinggi (>= 5.5 SR) di kedalaman menengah/dalam (>= 70 km). Getaran terasa jelas, namun risiko kerusakan struktural masif relatif rendah."},
    {"key": "tinggi",  "color": "#ef4444", "label": "Risiko Tinggi",
     "desc": "Gempa berkekuatan tinggi (>= 5.5 SR) pada kedalaman dangkal (< 70 km). Merupakan gempa paling merusak karena pusat energi berada sangat dekat dengan permukaan bumi dan berpotensi tsunami."},
]

def build_hazard_info(df: pd.DataFrame) -> dict:
    """
    Mengembalikan label bahaya kustom yang konsisten dengan hasil notebook clustering aturan (rule-based).
    """
    return {
        0: {"label": "Risiko Rendah", "color": _HAZARD_PALETTE[0]["color"], "desc": _HAZARD_PALETTE[0]["desc"]},
        1: {"label": "Risiko Sedang", "color": _HAZARD_PALETTE[1]["color"], "desc": _HAZARD_PALETTE[1]["desc"]},
        2: {"label": "Risiko Tinggi", "color": _HAZARD_PALETTE[2]["color"], "desc": _HAZARD_PALETTE[2]["desc"]}
    }

HAZARD_INFO = build_hazard_info(pd.DataFrame())  # placeholder; rebuilt on page load

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
        # KPI Cards Layout (3 columns: Total Gempa, Magnitudo Terbesar, Rata-rata Kedalaman)
        kpi1, kpi2, kpi3 = st.columns(3)
        
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
    st.write("Memetakan tingkat risiko bahaya gempa bumi global (Risiko Rendah, Sedang, Tinggi) secara spasial untuk melihat daerah-daerah rawan bencana di sepanjang batas lempeng tektonik.")
    
    if spatial_df.empty:
        st.warning("Data spasial kosong. Silakan jalankan notebook `03_custom_hazard_clustering.ipynb`.")
    else:
        st.write(f"Menampilkan **{len(spatial_df):,}** total gempa.")
        
        # Sampling mapping points to avoid crashing the browser
        sample_size = min(3000, len(spatial_df))
        if sample_size > 0:
            map_data = spatial_df.sample(n=sample_size, random_state=42)
            
            # Map Initialization (bounded world map with tectonic plates)
            m = create_world_map(center=[0, 115], zoom=3)
            
            for _, row in map_data.iterrows():
                cluster = int(row['kmeans_cluster'])
                info = HAZARD_INFO.get(cluster, {"label": "Unknown", "color": "#718096"})
                color = info["color"]
                
                popup_text = f"""
                <b>Lokasi:</b> {row['place']}<br>
                <b>Negara:</b> {row['country']}<br>
                <b>Magnitudo:</b> {row['mag']:.2f}<br>
                <b>Kedalaman:</b> {row['depth']:.1f} km<br>
                <b>Tingkat Risiko:</b> {info['label']}
                """
                
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=max(2.5, row['mag'] * 0.7),
                    stroke=False,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.8,
                    popup=folium.Popup(popup_text, max_width=300)
                ).add_to(m)
                
            st.components.v1.html(m._repr_html_(), height=600)
            
            # Legend mapping
            st.markdown("### Keterangan Tingkat Risiko Bahaya Spasial")
            cols = st.columns(3)
            for idx, info in sorted(HAZARD_INFO.items()):
                with cols[idx]:
                    st.markdown(f"""
                    <div style='background-color:#ffffff; padding:16px; border-radius:10px;
                                border-left: 5px solid {info['color']};
                                box-shadow: 0 2px 6px rgba(0,0,0,0.05); height:100%;'>
                        <strong style='color:#1A202C; font-size:0.95rem; display:block; margin-bottom:6px;'>
                            {info['label']}
                        </strong>
                        <span style='color:#4A5568; font-size:0.85rem; line-height:1.5; display:block;'>
                            {info['desc']}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Tidak ada data gempa bumi pada rentang filter ini.")

# --- PAGE 3: HAZARD PROFILING MAP ---
elif menu == "Klasifikasi Risiko Negara (Top 10)":
    st.title("Klasifikasi Risiko Negara Teraktif")
    st.write(
        "Halaman ini menampilkan klasifikasi tingkat kerawanan seismik untuk 10 negara paling aktif gempa bumi. "
        "Sistem secara otomatis mengelompokkan setiap negara ke dalam kategori **Risiko Tinggi (Rawan)**, **Risiko Sedang**, "
        "atau **Risiko Rendah** berdasarkan gempa terberat yang pernah tercatat di wilayah tersebut."
    )
    
    if spatial_df.empty:
        st.warning("Data kosong. Silakan jalankan notebook `03_custom_hazard_clustering.ipynb`.")
    else:
        # Explanation Cards
        st.markdown("### Logika Penentuan Risiko Negara")
        info_cols = st.columns(3)
        
        with info_cols[0]:
            st.markdown(
                "<div style='background-color:#fee2e2; padding:16px; border-radius:8px; border-left:5px solid #dc2626; height:100%;'>"
                "<strong style='color:#dc2626; font-size:0.95rem; display:block; margin-bottom:6px;'>Risiko Tinggi (Rawan)</strong>"
                "<span style='color:#4A5568; font-size:0.85rem; line-height:1.4; display:block;'>"
                "Negara diklasifikasikan sebagai <strong>Risiko Tinggi (Rawan)</strong> jika memiliki minimal 1 kejadian gempa Risiko Tinggi (Cluster 2). "
                "Meskipun jumlahnya sedikit, potensi gempa merusak sangat membahayakan wilayah daratan."
                "</span></div>",
                unsafe_allow_html=True
            )
        with info_cols[1]:
            st.markdown(
                "<div style='background-color:#ffedd5; padding:16px; border-radius:8px; border-left:5px solid #ea580c; height:100%;'>"
                "<strong style='color:#ea580c; font-size:0.95rem; display:block; margin-bottom:6px;'>Risiko Sedang</strong>"
                "<span style='color:#4A5568; font-size:0.85rem; line-height:1.4; display:block;'>"
                "Negara diklasifikasikan sebagai <strong>Risiko Sedang</strong> jika tidak mendeteksi gempa Risiko Tinggi, tetapi memiliki minimal 1 kejadian gempa Risiko Sedang (Cluster 1)."
                "</span></div>",
                unsafe_allow_html=True
            )
        with info_cols[2]:
            st.markdown(
                "<div style='background-color:#dbeafe; padding:16px; border-radius:8px; border-left:5px solid #2563eb; height:100%;'>"
                "<strong style='color:#2563eb; font-size:0.95rem; display:block; margin-bottom:6px;'>Risiko Rendah</strong>"
                "<span style='color:#4A5568; font-size:0.85rem; line-height:1.4; display:block;'>"
                "Negara diklasifikasikan sebagai <strong>Risiko Rendah</strong> jika seluruh gempa yang tercatat di wilayah tersebut hanya berkategori gempa minor/lemah (Cluster 0)."
                "</span></div>",
                unsafe_allow_html=True
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Calculations
        valid_countries_df = spatial_df[spatial_df['country'].notna() & (spatial_df['country'] != '')]
        
        # Group by country and hazard cluster
        country_stats = valid_countries_df.groupby(['country', 'kmeans_cluster']).size().unstack(fill_value=0)
        
        # Ensure columns 0, 1, 2 exist
        for col_idx in [0, 1, 2]:
            if col_idx not in country_stats.columns:
                country_stats[col_idx] = 0
        
        country_stats = country_stats.rename(columns={
            0: 'Risiko Rendah',
            1: 'Risiko Sedang',
            2: 'Risiko Tinggi'
        })
        
        country_stats['Total Gempa'] = country_stats['Risiko Rendah'] + country_stats['Risiko Sedang'] + country_stats['Risiko Tinggi']
        top_10_countries = country_stats.sort_values(by='Total Gempa', ascending=False).head(10).reset_index()
        
        def classify_country_risk(row):
            if row['Risiko Tinggi'] > 0:
                return 'Risiko Tinggi (Rawan)'
            elif row['Risiko Sedang'] > 0:
                return 'Risiko Sedang'
            else:
                return 'Risiko Rendah'
        
        top_10_countries['Klasifikasi Risiko'] = top_10_countries.apply(classify_country_risk, axis=1)
        
        # Layout: Table left, Stacked Chart right
        tab_col1, tab_col2 = st.columns([1.1, 0.9])
        
        with tab_col1:
            st.subheader("Tabel Distribusi & Klasifikasi Negara")
            # Premium HTML Table
            html_table = """
            <div style="overflow-x:auto;">
                <table style="width:100%; border-collapse:collapse; margin-top:10px; font-family:inherit;">
                    <thead>
                        <tr style="background-color:#f8fafc; border-bottom:2px solid #e2e8f0; text-align:left;">
                            <th style="padding:10px 6px; color:#475569; font-weight:600; font-size:0.85rem;">Negara</th>
                            <th style="padding:10px 6px; color:#3b82f6; font-weight:600; font-size:0.85rem; text-align:center;">Risiko Rendah</th>
                            <th style="padding:10px 6px; color:#f97316; font-weight:600; font-size:0.85rem; text-align:center;">Risiko Sedang</th>
                            <th style="padding:10px 6px; color:#ef4444; font-weight:600; font-size:0.85rem; text-align:center;">Risiko Tinggi</th>
                            <th style="padding:10px 6px; color:#1e293b; font-weight:700; font-size:0.85rem; text-align:center;">Total</th>
                            <th style="padding:10px 6px; color:#1e293b; font-weight:600; font-size:0.85rem; text-align:center;">Klasifikasi</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for idx, row in top_10_countries.iterrows():
                risk = row['Klasifikasi Risiko']
                if risk == 'Risiko Tinggi (Rawan)':
                    badge = "<span style='background-color:#fee2e2; color:#dc2626; padding:3px 6px; border-radius:4px; font-weight:700; font-size:0.75rem; display:inline-block; border:1px solid #fca5a5;'>Risiko Tinggi (Rawan)</span>"
                elif risk == 'Risiko Sedang':
                    badge = "<span style='background-color:#ffedd5; color:#ea580c; padding:3px 6px; border-radius:4px; font-weight:700; font-size:0.75rem; display:inline-block; border:1px solid #fdba74;'>Risiko Sedang</span>"
                else:
                    badge = "<span style='background-color:#dbeafe; color:#2563eb; padding:3px 6px; border-radius:4px; font-weight:700; font-size:0.75rem; display:inline-block; border:1px solid #93c5fd;'>Risiko Rendah</span>"
                
                bg_row = "#ffffff" if idx % 2 == 0 else "#f8fafc"
                html_table += f"""
                    <tr style="background-color:{bg_row}; border-bottom:1px solid #edf2f7;">
                        <td style="padding:10px 6px; font-weight:700; color:#1e293b; font-size:0.85rem;">{row['country']}</td>
                        <td style="padding:10px 6px; text-align:center; color:#3b82f6; font-weight:600; font-size:0.85rem;">{row['Risiko Rendah']:,}</td>
                        <td style="padding:10px 6px; text-align:center; color:#f97316; font-weight:600; font-size:0.85rem;">{row['Risiko Sedang']:,}</td>
                        <td style="padding:10px 6px; text-align:center; color:#ef4444; font-weight:600; font-size:0.85rem;">{row['Risiko Tinggi']:,}</td>
                        <td style="padding:10px 6px; text-align:center; font-weight:700; color:#1e293b; font-size:0.85rem;">{row['Total Gempa']:,}</td>
                        <td style="padding:10px 6px; text-align:center;">{badge}</td>
                    </tr>
                """
            html_table += "</tbody></table></div>"
            st.markdown(html_table, unsafe_allow_html=True)
            
        with tab_col2:
            st.subheader("Grafik Proporsi Risiko per Negara")
            plot_df_melted = top_10_countries.melt(
                id_vars=['country', 'Total Gempa', 'Klasifikasi Risiko'],
                value_vars=['Risiko Rendah', 'Risiko Sedang', 'Risiko Tinggi'],
                var_name='Tingkat Risiko',
                value_name='Jumlah Gempa'
            )
            fig_stacked = px.bar(
                plot_df_melted, x='Jumlah Gempa', y='country', color='Tingkat Risiko',
                orientation='h',
                color_discrete_map={
                    'Risiko Rendah': '#3b82f6',
                    'Risiko Sedang': '#f97316',
                    'Risiko Tinggi': '#ef4444'
                },
                labels={'Jumlah Gempa': 'Jumlah Gempa', 'country': 'Negara'}
            )
            fig_stacked.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                font=dict(color='#2D3748', size=11),
                xaxis=dict(gridcolor='#e2e8f0', title_font=dict(color='#2D3748'), tickfont=dict(color='#2D3748')),
                yaxis_title=None,
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=380,
                margin=dict(l=0, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_stacked, use_container_width=True)

