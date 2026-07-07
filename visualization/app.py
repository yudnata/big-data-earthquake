import os
import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster
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

# Load datasets
spatial_df = load_collection_data("kmeans_results_emsc")
hazard_df = load_collection_data("custom_hazard_results_emsc")
if not hazard_df.empty:
    if 'hazard_cluster' in hazard_df.columns:
        hazard_df['kmeans_cluster'] = hazard_df['hazard_cluster']
country_risk_df = load_collection_data("kmeans_country_risk_results_emsc")

# Navigation Sidebar (No Emojis, Clean UI)
st.sidebar.title("Navigasi Analisis")
menu = st.sidebar.radio(
    "Pilih Halaman Visualisasi:",
    [
        "Ringkasan & Tren Seismik", 
        "Peta Zona Rawan Spasial (Ring of Fire)", 
        "Peta & Profil Bahaya Gempa (Hazard)"
    ]
)



# Colors for mapping clusters
SPATIAL_COLORS = ['#e53e3e', '#3182ce', '#38a169', '#dd6b20', '#805ad5', '#d69e2e', '#319795', '#b7791f']

# Warna dan deskripsi per kategori bahaya (4 kategori tetap)
_HAZARD_PALETTE = [
    {"key": "dangkal_lemah",   "color": "#3b82f6", "label": "Dangkal & Lemah",
     "desc": "Magnitudo rendah (< 4.0), kedalaman dangkal (< 70 km). Sangat sering terjadi, risiko bahaya sangat rendah. Umumnya hanya dirasakan peralatan seismograf dan tidak menimbulkan kerusakan."},
    {"key": "dangkal_kuat",    "color": "#ef4444", "label": "Dangkal & Kuat",
     "desc": "Magnitudo tinggi (>= 5.5), kedalaman dangkal (< 70 km). Jenis paling merusak — melepaskan energi besar dekat permukaan. Berpotensi tsunami dan menyebabkan kerusakan bangunan masif."},
    {"key": "menengah_sedang", "color": "#10b981", "label": "Menengah & Sedang",
     "desc": "Magnitudo sedang (4.0–5.5), kedalaman menengah (70–300 km). Getaran dirasakan sedang oleh penduduk. Kerusakan ringan hingga sedang pada bangunan tidak tahan gempa."},
    {"key": "dalam_kuat",      "color": "#f97316", "label": "Dalam & Kuat",
     "desc": "Magnitudo tinggi (> 5.5), kedalaman sangat dalam (> 300 km). Terjadi di zona subduksi dalam. Getaran terasa di area luas namun jarang menimbulkan kerusakan struktural masif."},
]

def build_hazard_info(df: pd.DataFrame) -> dict:
    """
    Mengembalikan label bahaya kustom yang konsisten dengan hasil notebook clustering aturan (rule-based).
    """
    return {
        0: {"label": "Cluster 0: Dangkal & Lemah", "color": _HAZARD_PALETTE[0]["color"], "desc": _HAZARD_PALETTE[0]["desc"]},
        1: {"label": "Cluster 1: Dangkal & Kuat", "color": _HAZARD_PALETTE[1]["color"], "desc": _HAZARD_PALETTE[1]["desc"]},
        2: {"label": "Cluster 2: Menengah & Sedang", "color": _HAZARD_PALETTE[2]["color"], "desc": _HAZARD_PALETTE[2]["desc"]},
        3: {"label": "Cluster 3: Dalam & Kuat", "color": _HAZARD_PALETTE[3]["color"], "desc": _HAZARD_PALETTE[3]["desc"]}
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
    st.write("Mengelompokkan gempa berdasarkan lokasi geografis 3D (x, y, z) untuk memetakan batas lempeng sabuk gempa bumi global.")
    
    if spatial_df.empty:
        st.warning("Data spasial kosong. Silakan jalankan notebook `03_data_analysis.ipynb`.")
    else:
        st.write(f"Menampilkan **{len(spatial_df):,}** total gempa.")
        
        # Sampling mapping points to avoid crashing the browser
        sample_size = min(3000, len(spatial_df))
        if sample_size > 0:
            map_data = spatial_df.sample(n=sample_size, random_state=42)
            
            # Map Initialization
            m = folium.Map(location=[0, 115], zoom_start=3, tiles="CartoDB positron")
            
            # Create MarkerCluster group
            marker_cluster_spatial = MarkerCluster().add_to(m)
            
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
                ).add_to(marker_cluster_spatial)
                
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
    st.title("Klasifikasi Profil Bahaya Seismik")
    st.write(
        "Menggunakan pendekatan **Klasifikasi Berbasis Aturan (Rule-Based Hazard Classification)**, setiap kejadian gempa "
        "dikelompokkan berdasarkan dua parameter fisik utama: **kedalaman hiposenter** dan **magnitudo**. "
        "Hasil klasifikasi menghasilkan 4 profil bahaya kustom yang berbeda secara karakteristik."
    )
    
    if hazard_df.empty:
        st.warning("Data hazard kosong. Silakan jalankan notebook `03_data_analysis_hazard.ipynb`.")
    else:
        st.write(f"Menampilkan **{len(hazard_df):,}** total data kejadian gempa.")        

        
        # Build HAZARD_INFO dynamically from actual centroid values in MongoDB data
        HAZARD_INFO = build_hazard_info(hazard_df)
        
        # Prepare labelled data once, reuse across all charts
        plot_data = hazard_df.copy()
        plot_data['Kategori Bahaya'] = plot_data['kmeans_cluster'].map(
            lambda x: HAZARD_INFO.get(int(x), {"label": "Unknown"})["label"]
        )
        color_map = {v['label']: v['color'] for k, v in HAZARD_INFO.items()}

        # Auto-compute insights
        total = len(plot_data)
        cluster_pct = plot_data['Kategori Bahaya'].value_counts(normalize=True) * 100
        dominant = cluster_pct.idxmax() if not cluster_pct.empty else "-"
        dominant_pct = cluster_pct.max() if not cluster_pct.empty else 0
        danger_label = HAZARD_INFO[1]['label']
        danger_pct = cluster_pct.get(danger_label, 0)
        
        # ============================================================
        # SECTION 1: Scatter Plot — Sebaran Klaster di Ruang Fitur
        # ============================================================
        st.subheader("1. Sebaran Klaster: Kekuatan vs Kedalaman Gempa")
        st.caption(
            "Grafik ini menunjukkan posisi setiap gempa dalam koordinat kekuatan (magnitudo) dan kedalaman. "
            "Warna mewakili kategori bahaya hasil pengelompokan otomatis. "
            "Sumbu kedalaman dibalik: angka 0 di atas = permukaan bumi, semakin ke bawah = semakin jauh ke dalam bumi."
        )
        if not plot_data.empty:
            fig_scatter = px.scatter(
                plot_data.sample(n=min(8000, len(plot_data)), random_state=42),
                x='mag', y='depth', color='Kategori Bahaya',
                color_discrete_map=color_map,
                labels={'mag': 'Magnitudo', 'depth': 'Kedalaman (km)', 'Kategori Bahaya': 'Profil Bahaya'},
                opacity=0.65,
                hover_data={'mag': ':.2f', 'depth': ':.1f'}
            )
            fig_scatter.update_layout(
                font=dict(color='#2D3748', size=13),
                xaxis=dict(gridcolor='#e2e8f0', title_font=dict(color='#2D3748'), tickfont=dict(color='#2D3748')),
                yaxis=dict(autorange='reversed', gridcolor='#e2e8f0', title_font=dict(color='#2D3748'), tickfont=dict(color='#2D3748')),
                legend=dict(font=dict(color='#2D3748'), title_font=dict(color='#2D3748')),
                plot_bgcolor='white', paper_bgcolor='white', height=470
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Build per-cluster percentage rows
            cluster_rows = []
            for cid, info in sorted(HAZARD_INFO.items()):
                lbl = info['label']
                pct = cluster_pct.get(lbl, 0)
                cnt = int(round(pct / 100 * total))
                cluster_rows.append((lbl, info['color'], pct, cnt))

            # Find "Dangkal & Kuat" cluster dynamically
            danger_label = next(
                (info['label'] for info in HAZARD_INFO.values()
                 if 'Kuat' in info['label'] and 'Dalam' not in info['label']),
                cluster_rows[0][0]
            )
            danger_pct = cluster_pct.get(danger_label, 0)

            # Render insight box using markdown with HTML
            rows_html = "".join(
                f"<tr>"
                f"<td style='padding:5px 16px 5px 0; white-space:nowrap;'>"
                f"<span style='display:inline-block;width:11px;height:11px;border-radius:50%;"
                f"background:{color};margin-right:7px;vertical-align:middle;'></span>"
                f"<b>{label}</b></td>"
                f"<td style='padding:5px 12px; font-weight:700; color:#1A202C;'>{pct:.1f}%</td>"
                f"<td style='padding:5px 0; color:#4A5568;'>{count:,} gempa</td>"
                f"</tr>"
                for label, color, pct, count in cluster_rows
            )
            st.markdown(
                f"""<div style="background-color:#ebf8ff; border-left:4px solid #3182ce;
                              padding:16px 20px; border-radius:6px; margin-top:8px;">
                    <p style="font-weight:700; color:#2C5282; margin:0 0 12px 0; font-size:0.97rem;">
                        Temuan Utama &mdash; Total <strong>{total:,}</strong> gempa diklasifikasikan ke dalam 4 profil bahaya:
                    </p>
                    <table style="border-collapse:collapse; width:auto;">{rows_html}</table>
                    <p style="margin:12px 0 0 0; color:#2D3748; font-size:0.9rem;">
                        Kategori paling berbahaya (<em>{danger_label}</em>) mewakili
                        <strong>{danger_pct:.1f}%</strong> dari seluruh kejadian &mdash;
                        meskipun proporsinya kecil, dampaknya terhadap permukaan sangat signifikan.
                    </p>
                </div>""",
                unsafe_allow_html=True
            )

        else:
            st.info("Tidak ada data untuk divisualisasikan.")
        
        # ============================================================
        # SECTION 2: Peta Spasial Distribusi Bahaya Gempa (Geospatial Map)
        # ============================================================
        st.subheader("2. Peta Spasial Distribusi Bahaya Gempa")
        st.caption(
            "Peta interaktif sebaran lokasi kejadian gempa bumi berdasarkan kategori bahaya di seluruh dunia. "
            "Pola titik merah di sekitar Indonesia menunjukkan wilayah rawan bencana (Ring of Fire) dengan bahaya tinggi."
        )
        sample_size_haz = min(3000, len(plot_data))
        if sample_size_haz > 0:
            map_data_haz = plot_data.sample(n=sample_size_haz, random_state=42)
            # Map Initialization (center around Indonesia [0, 115])
            m_haz = folium.Map(location=[0, 115], zoom_start=3, tiles="CartoDB positron")
            
            # Create MarkerCluster group
            marker_cluster_haz = MarkerCluster().add_to(m_haz)
            
            for _, row in map_data_haz.iterrows():
                cluster = int(row['kmeans_cluster'])
                info = HAZARD_INFO.get(cluster, {"label": "Unknown", "color": "#718096"})
                color = info["color"]
                
                popup_text = f"""
                <b>Lokasi:</b> {row['place']}<br>
                <b>Negara:</b> {row['country']}<br>
                <b>Magnitudo:</b> {row['mag']:.2f}<br>
                <b>Kedalaman:</b> {row['depth']:.1f} km<br>
                <b>Profil Bahaya:</b> {info['label']}
                """
                
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=max(3, row['mag'] * 1.5),
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.6,
                    popup=folium.Popup(popup_text, max_width=300)
                ).add_to(marker_cluster_haz)
                
            st.components.v1.html(m_haz._repr_html_(), height=600)
        


        
        # ============================================================
        # SECTION 3: Proporsi Klaster (Bar Chart full width)
        # ===========================================================
        st.subheader("3. Frekuensi Setiap Kategori Bahaya")
        st.caption("Seberapa sering tiap jenis bahaya gempa terjadi dari total data yang dianalisis?")
        
        cluster_counts = plot_data['Kategori Bahaya'].value_counts().reset_index()
        cluster_counts.columns = ['Kategori Bahaya', 'Jumlah']
        order = [HAZARD_INFO[i]['label'] for i in sorted(HAZARD_INFO.keys())]
        cluster_counts['sort_key'] = cluster_counts['Kategori Bahaya'].map(
            {v: k for k, v in enumerate(order)}
        )
        cluster_counts = cluster_counts.sort_values('sort_key')
        
        fig_bar = px.bar(
            cluster_counts, x='Jumlah', y='Kategori Bahaya', orientation='h',
            color='Kategori Bahaya', color_discrete_map=color_map,
            labels={'Jumlah': 'Jumlah Kejadian', 'Kategori Bahaya': ''},
            text='Jumlah'
        )
        fig_bar.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig_bar.update_layout(
            showlegend=False,
            font=dict(color='#2D3748', size=13),
            xaxis=dict(gridcolor='#e2e8f0', title_font=dict(color='#2D3748'), tickfont=dict(color='#2D3748')),
            yaxis=dict(title_font=dict(color='#2D3748'), tickfont=dict(color='#2D3748', size=11)),
            plot_bgcolor='white', paper_bgcolor='white', height=320,
            margin=dict(r=80)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        

        
        # ============================================================
        # SECTION 4: Kartu Deskripsi Klaster
        # ============================================================
        st.subheader("4. Penjelasan Setiap Kategori Profil Bahaya")
        st.caption(
            "Interpretasi dari setiap klaster berdasarkan kombinasi magnitudo dan kedalaman gempa "
            "yang dihasilkan model K-Means:"
        )
        desc_cols = st.columns(4)
        for cluster_id, info in HAZARD_INFO.items():
            with desc_cols[cluster_id]:
                st.markdown(f"""
                <div style="background-color:#ffffff; padding:18px; border-radius:12px;
                            border-top: 5px solid {info['color']};
                            box-shadow: 0 4px 10px rgba(0,0,0,0.08); height:100%;">
                    <div style="font-size:0.72rem; font-weight:700; text-transform:uppercase;
                                letter-spacing:0.1em; color:{info['color']}; margin-bottom:8px;">
                        Klaster {cluster_id}
                    </div>
                    <strong style="color:#1A202C; font-size:0.95rem; display:block;
                                   margin-bottom:10px; line-height:1.35;">
                        {info['label']}
                    </strong>
                    <span style="color:#4A5568; font-size:0.85rem; line-height:1.65;">
                        {info['desc']}
                    </span>
                </div>
                """, unsafe_allow_html=True)

