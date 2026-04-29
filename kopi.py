import streamlit as st
import requests
import py3Dmol
from stmol import showmol
import math
import streamlit.components.v1 as components
import io
import matplotlib.pyplot as plt

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="ChemPro AI - Kelompok 1", 
    page_icon="🧪", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. DATABASE ALAT KIMIA LOKAL (SUPER LENGKAP & GAMBAR REALISTIS) ---
DATABASE_ALAT = {
    "gelas kimia": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?q=80&w=600&auto=format&fit=crop", 
    "labu erlenmeyer": "https://commons.wikimedia.org/wiki/Special:FilePath/Erlenmeyer_flask.jpg?width=480",
    "gelas ukur": "https://commons.wikimedia.org/wiki/Special:FilePath/Measuring_cylinder.jpg?width=480",
    "tabung reaksi": "https://images.unsplash.com/photo-1576086213369-97a306d36557?q=80&w=600&auto=format&fit=crop", 
    "rak tabung reaksi": "https://images.unsplash.com/photo-1583912265922-98fc11c10924?q=80&w=600&auto=format&fit=crop", 
    "pipet tetes": "https://commons.wikimedia.org/wiki/Special:FilePath/Pipette_01.jpg?width=480",
    "pipet volume": "https://commons.wikimedia.org/wiki/Special:FilePath/Volumetric_pipette.jpg?width=480",
    "pipet ukur": "https://commons.wikimedia.org/wiki/Special:FilePath/Graduated_pipette.jpg?width=480",
    "buret": "https://commons.wikimedia.org/wiki/Special:FilePath/Burette.jpg?width=480",
    "labu ukur": "https://commons.wikimedia.org/wiki/Special:FilePath/Volumetric_flask.jpg?width=480",
    "batang pengaduk": "https://commons.wikimedia.org/wiki/Special:FilePath/Glass_stir_rod.jpg?width=480",
    "corong kaca": "https://commons.wikimedia.org/wiki/Special:FilePath/Funnel.jpg?width=480",
    "kaca arloji": "https://commons.wikimedia.org/wiki/Special:FilePath/Watch_glass.jpg?width=480",
    "mortar dan alu": "https://commons.wikimedia.org/wiki/Special:FilePath/Mortar_and_pestle.jpg?width=480",
    "spatula": "https://commons.wikimedia.org/wiki/Special:FilePath/Spatula.jpg?width=480",
    "neraca analitik": "https://commons.wikimedia.org/wiki/Special:FilePath/Analytical_balance.jpg?width=480",
    "pembakar bunsen": "https://commons.wikimedia.org/wiki/Special:FilePath/Bunsen_burner.jpg?width=480",
    "kaki tiga": "https://commons.wikimedia.org/wiki/Special:FilePath/Tripod_(laboratory).jpg?width=480",
    "kawat kasa": "https://commons.wikimedia.org/wiki/Special:FilePath/Wire_gauze.jpg?width=480",
    "cawan penguap": "https://commons.wikimedia.org/wiki/Special:FilePath/Evaporating_dish.jpg?width=480",
    "krusibel": "https://commons.wikimedia.org/wiki/Special:FilePath/Crucible.jpg?width=480",
    "botol semprot": "https://commons.wikimedia.org/wiki/Special:FilePath/Wash_bottle.jpg?width=480",
    "termometer": "https://commons.wikimedia.org/wiki/Special:FilePath/Thermometer.jpg?width=480",
    "klem dan statif": "https://commons.wikimedia.org/wiki/Special:FilePath/Retort_stand.jpg?width=480",
    "desikator": "https://commons.wikimedia.org/wiki/Special:FilePath/Desiccator.jpg?width=480",
    "sentrifugasi": "https://commons.wikimedia.org/wiki/Special:FilePath/Tabletop_centrifuge.jpg?width=480",
    "kertas saring": "https://commons.wikimedia.org/wiki/Special:FilePath/Filter_paper.jpg?width=480",
    "corong pisah": "https://commons.wikimedia.org/wiki/Special:FilePath/Separatory_funnel.jpg?width=480",
    "indikator universal": "https://commons.wikimedia.org/wiki/Special:FilePath/Universal_indicator_paper.jpg?width=480",
    "lemari asam": "https://commons.wikimedia.org/wiki/Special:FilePath/Fume_hood.jpg?width=480"
}

# --- 3. FUNGSI PENDUKUNG ---
def tampilkan_gambar_aman(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            st.image(io.BytesIO(response.content), width=380)
        else:
            st.warning("⚠️ Server gambar sedang sibuk, visualisasi tidak dapat dimuat saat ini.")
    except Exception:
        st.warning("⚠️ Kesalahan koneksi saat memuat gambar.")

@st.cache_data
def cari_gambar_wikipedia_pro(query):
    try:
        search_url = f"https://id.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=1&format=json"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res_search = requests.get(search_url, headers=headers).json()
        if len(res_search[1]) > 0:
            best_title = res_search[1][0]
            summary_url = f"https://id.wikipedia.org/api/rest_v1/page/summary/{best_title.replace(' ', '_')}"
            res_summary = requests.get(summary_url, headers=headers).json()
            if 'thumbnail' in res_summary:
                return res_summary['thumbnail']['source'], f"🔍 Ditemukan: **{best_title}**"
    except: return None, None
    return None, None

@st.cache_data
def cari_struktur_pubchem(query):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{query.strip()}/PNG"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200: return url, f"🔬 Struktur Kimia 2D: **{query.title()}**"
    except: return None, None
    return None, None

@st.cache_data
def get_chem_data(nama_zat):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{nama_zat}/property/MolecularWeight,MolecularFormula,IUPACName/JSON"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['PropertyTable']['Properties'][0]
            return {"mr": float(data.get('MolecularWeight', 0)), "formula": data.get('MolecularFormula', 'N/A')}
        return None
    except: return None

@st.cache_data
def get_3d_sdf(nama_zat):
    nama_zat = nama_zat.strip()
    url_3d = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{nama_zat}/record/SDF/?record_type=3d"
    try:
        response = requests.get(url_3d)
        if response.status_code == 200: return response.text
        url_2d = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{nama_zat}/record/SDF/?record_type=2d"
        res_2d = requests.get(url_2d)
        if res_2d.status_code == 200: return res_2d.text
        return None
    except: return None

@st.cache_data
def get_wiki_summary(nama_zat):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{nama_zat}"
        response = requests.get(url)
        if response.status_code == 200: return response.json().get('extract', 'Deskripsi tidak ditemukan.')
        return "Deskripsi tidak tersedia."
    except: return "Gagal memuat ensiklopedia."

def render_3d_molecule(sdf_data):
    view = py3Dmol.view(width=800, height=450)
    view.addModel(sdf_data, 'sdf')
    view.setStyle({'stick': {'radius': 0.15}, 'sphere': {'scale': 0.3}})
    view.setBackgroundColor('rgba(14, 17, 23, 0)') 
    view.zoomTo()
    view.spin(True)
    showmol(view, height=450, width=800)

@st.cache_data(ttl=3600)
def cari_jurnal_akademik(query, batas_tahun, jumlah_hasil=5):
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "filter": f"type:journal-article,from-pub-date:{batas_tahun}-01-01",
        "select": "title,author,published,URL,DOI,is-referenced-by-count,publisher",
        "sort": "relevance",
        "rows": jumlah_hasil
    }
    headers = {'User-Agent': 'ChemProAI_EduProject/5.0'}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if response.status_code == 200: return response.json()['message']['items']
        return None
    except: return None

# --- 4. SIDEBAR (NAVIGASI) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/995/995440.png", width=80)
    st.title("ChemPro AI")
    st.caption("Lab Assistant v4.0")
    st.divider()
    menu = st.radio("Pilih Modul Lab:", 
             ["⚖️ Stoikiometri Padatan", "💧 Kalkulator Pengenceran", "🌡️ pH & Analitik", 
              "🌐 Ensiklopedia 3D", "🔋 Simulasi Sel Volta", "📈 Laju & Kinetika",
              "🛡️ K3 & Keamanan Lab", "📋 Generator Diagram Alir", "🤖 Asisten AI Kimia",
              "📚 Pustaka Jurnal Pro"], key="modul_lab")
    st.divider()
    st.markdown("### 🛠️ Developer:")
    st.success("✨ Kelompok 1\n\nPendidikan Kimia 2024\nUniversitas Lampung")


# --- 5. LOGIKA DYNAMIC BACKGROUND (5 VARIASI BINTANG MALAM) ---
BG_SPACE_1 = "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?q=80&w=2000&auto=format&fit=crop" # Milky Way
BG_SPACE_2 = "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2000&auto=format&fit=crop" # Blue Space
BG_SPACE_3 = "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?q=80&w=2000&auto=format&fit=crop" # Starry Night
BG_SPACE_4 = "https://images.unsplash.com/photo-1464802686167-b939a6910659?q=80&w=2000&auto=format&fit=crop" # Nebula Ungu
BG_SPACE_5 = "https://images.unsplash.com/photo-1534447677768-be436bb09401?q=80&w=2000&auto=format&fit=crop" # Aurora Bintang

if menu in ["🤖 Asisten AI Kimia", "🌐 Ensiklopedia 3D"]:
    active_bg = BG_SPACE_1
elif menu in ["⚖️ Stoikiometri Padatan", "💧 Kalkulator Pengenceran"]:
    active_bg = BG_SPACE_2
elif menu in ["🌡️ pH & Analitik", "🔋 Simulasi Sel Volta"]:
    active_bg = BG_SPACE_3
elif menu in ["📈 Laju & Kinetika", "🛡️ K3 & Keamanan Lab"]:
    active_bg = BG_SPACE_4
elif menu in ["📋 Generator Diagram Alir", "📚 Pustaka Jurnal Pro"]:
    active_bg = BG_SPACE_5


# --- 6. INJEKSI CSS DENGAN KEYFRAMES ANIMASI LUAR ANGKASA ---
st.markdown(f"""
    <style>
    /* MENGHILANGKAN BACKGROUND DEFAULT STREAMLIT */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {{
        background-color: transparent !important;
    }}

    /* MEMBUAT ANIMASI PERGERAKAN BINTANG MELAYANG (PANNING EFFECT) */
    @keyframes panBackground {{
        0% {{ background-position: 0% 0%; }}
        50% {{ background-position: 100% 100%; }}
        100% {{ background-position: 0% 0%; }}
    }}

    .stApp {{
        background-image: url("{active_bg}") !important;
        background-size: 150% 150% !important; 
        animation: panBackground 120s linear infinite !important; 
        transition: background-image 0.8s ease-in-out;
    }}

    /* OVERLAY GRADASI GELAP (Membantu teks putih menyala) */
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(135deg, rgba(5, 8, 15, 0.6) 0%, rgba(2, 4, 8, 0.9) 100%) !important;
        z-index: -1;
    }}

    /* SIDEBAR KACA FILM GELAP */
    [data-testid="stSidebar"] {{
        background-color: rgba(10, 12, 16, 0.5) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}

    /* CONTAINER DAN KOTAK INPUT (EFEK KACA PREMIUM) */
    div[data-testid="stVerticalBlock"] > div[style*="border"], 
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"],
    div[data-testid="stMetric"], .stChatMessage, div[data-testid="stExpander"], 
    .stChatFloatingInputContainer {{
        background-color: rgba(20, 25, 35, 0.5) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important; 
        border-radius: 15px !important;
        color: white !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5) !important; 
    }}

    ul[data-baseweb="menu"] {{
        background-color: rgba(20, 25, 35, 0.95) !important;
        color: white !important;
    }}

    /* TOMBOL GRADASI PREMIUM */
    .stButton button {{
        background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important;
        padding: 10px 20px !important;
    }}
    
    .stButton button:hover {{
        transform: translateY(-2px) !important;
        background: linear-gradient(135deg, #5c7ecf 0%, #20355e 100%) !important;
        box-shadow: 0 6px 20px rgba(75, 108, 183, 0.6) !important;
    }}

    /* TEKS HEADER & BAYANGAN */
    h1, h2, h3, p, span, label, div[data-testid="stMarkdownContainer"] {{
        color: #fdfdfd !important;
        text-shadow: 1px 1px 4px rgba(0,0,0,1.0) !important; 
    }}

    /* FOOTER TRANSLUCENT */
    .footer {{
        position: fixed;
        left: 0; bottom: 0; width: 100%;
        background-color: rgba(10, 12, 16, 0.8);
        backdrop-filter: blur(10px);
        color: #d1d5db;
        text-align: center;
        padding: 8px; font-size: 12px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        z-index: 999;
    }}
    </style>
    
    <div class="footer">
        © 2026 Developed by Kelompok 1 | Pendidikan Kimia 2024 Universitas Lampung
    </div>
    """, unsafe_allow_html=True)


# --- 7. LOGIKA MODUL ---
if menu == "⚖️ Stoikiometri Padatan":
    st.markdown("<h1 style='text-align: center;'>⚖️ Kalkulator Massa Padatan</h1>", unsafe_allow_html=True)
    col_mid = st.columns([1, 2, 1])[1]
    with col_mid:
        with st.container(border=True):
            zat = st.text_input("Nama Zat (Inggris):", "Sodium Hydroxide")
            molar = st.number_input("Molaritas (M):", 0.001, 10.0, 0.1)
            vol = st.number_input("Volume (mL):", 10, 5000, 250)
            if st.button("Hitung Massa", use_container_width=True):
                data = get_chem_data(zat)
                if data:
                    massa = molar * (vol/1000) * data['mr']
                    st.metric("Massa Wajib Timbang", f"{massa:.4f} g")
                    st.info(f"Senyawa: **{data['formula']}** | Mr: **{data['mr']}**")
                else: st.error("Zat tidak ditemukan di database.")

elif menu == "💧 Kalkulator Pengenceran":
    st.title("💧 Pengenceran Larutan")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        m1 = c1.number_input("M1 (Pekat):", 0.1, 18.0, 1.0)
        m2 = c2.number_input("M2 (Target):", 0.01, 10.0, 0.1)
        v2 = c3.number_input("V2 (Akhir) mL:", 10, 1000, 100)
    if m2 < m1:
        v1 = (m2 * v2) / m1
        st.success(f"Ambil larutan pekat sebanyak: **{v1:.2f} mL**")
    else: st.warning("M2 harus lebih kecil dari M1")

elif menu == "🌡️ pH & Analitik":
    st.title("🌡️ Analisis pH")
    with st.container(border=True):
        kat = st.selectbox("Jenis Larutan:", ["Asam Kuat", "Basa Kuat", "Asam Lemah", "Basa Lemah"])
        m = st.number_input("Konsentrasi (M):", 0.0001, 1.0, 0.1, format="%.4f")
        val = st.number_input("Valensi:", 1, 3, 1)
        if "Lemah" in kat: ka = st.number_input("Ka/Kb:", value=1.8e-5, format="%.2e")
        if st.button("Hitung pH", use_container_width=True):
            if "Kuat" in kat: h = m * val
            else: h = math.sqrt(ka * m)
            ph = -math.log10(h) if "Asam" in kat else 14 - (-math.log10(h))
            st.metric("Hasil Perhitungan pH", f"{ph:.2f}")

elif menu == "🌐 Ensiklopedia 3D":
    st.title("🌐 Visualisasi Molekuler")
    cari = st.text_input("Ketik Nama Molekul (Inggris):", "Caffeine")
    if cari:
        sdf, c_data, desc = get_3d_sdf(cari), get_chem_data(cari), get_wiki_summary(cari)
        if sdf and c_data:
            c1, c2 = st.columns([1.5, 1])
            with c1: render_3d_molecule(sdf)
            with c2:
                st.subheader("🧬 Informasi")
                st.write(f"**Formula:** {c_data['formula']}")
                st.divider()
                st.write(desc)

elif menu == "🔋 Simulasi Sel Volta":
    st.title("🔋 Simulasi Sel Volta")
    e_nol = {"Li":-3.04, "K":-2.92, "Na":-2.71, "Mg":-2.37, "Al":-1.66, "Zn":-0.76, "Fe":-0.44, "Ni":-0.25, "Sn":-0.14, "Pb":-0.13, "H2":0.0, "Cu":0.34, "Ag":0.80, "Au":1.50}
    c1, c2 = st.columns(2)
    l1 = c1.selectbox("Logam A (Anoda/Katoda):", list(e_nol.keys()), index=9)
    l2 = c2.selectbox("Logam B (Anoda/Katoda):", list(e_nol.keys()), index=12)
    if st.button("Reaksikan", use_container_width=True):
        v1, v2 = e_nol[l1], e_nol[l2]
        anoda, katoda = (l1, l2) if v1 < v2 else (l2, l1)
        st.metric("Potensial Sel (E°cell)", f"{abs(v1-v2):.2f} V")
        st.code(f"Notasi Sel: {anoda} | {anoda}ⁿ⁺ || {katoda}ⁿ⁺ | {katoda}")

elif menu == "📈 Laju & Kinetika":
    st.title("📈 Grafik Kinetika Reaksi")
    orde = st.selectbox("Orde Reaksi:", [0, 1, 2])
    c1, c2, c3 = st.columns(3)
    k = c1.number_input("Konstanta Laju (k):", 0.01, 1.0, 0.05)
    a0 = c2.number_input("Konsentrasi Awal (A0):", 0.1, 2.0, 1.0)
    t_max = c3.slider("Rentang Waktu:", 10, 200, 50)
    
    if st.button("Gambarkan Grafik Laju", use_container_width=True):
        ts = list(range(t_max))
        if orde==0: ys = [max(0, a0 - k*t) for t in ts]
        elif orde==1: ys = [a0 * math.exp(-k*t) for t in ts]
        else: ys = [1/(1/a0 + k*t) for t in ts]
        
        # --- PERBAIKAN GRAFIK MATPLOTLIB ANTI-ERROR ---
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Atur latar belakang menggunakan 'none' agar tembus pandang
        fig.patch.set_alpha(0.0)
        ax.set_facecolor("none")
        
        ax.plot(ts, ys, color='#fc466b', linewidth=3)
        
        # Styling menyatu dengan Glassmorphism
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.set_xlabel("Waktu (s)", color='white', fontweight='bold')
        ax.set_ylabel("Konsentrasi [A]", color='white', fontweight='bold')
        
        st.pyplot(fig, transparent=True) 

elif menu == "🛡️ K3 & Keamanan Lab":
    st.title("🛡️ Panduan Keamanan Lab")
    haz = {"H2SO4 (Asam Sulfat)": "Sangat Korosif! Dapat menyebabkan luka bakar serius.", "NaOH (Natrium Hidroksida)": "Iritasi kuat! Bahaya jika terkena mata.", "Metanol": "Sangat mudah terbakar dan beracun!", "HCl (Asam Klorida)": "Menghasilkan uap beracun, kerjakan di lemari asam!"}
    p = st.selectbox("Pilih Bahan Kimia Berbahaya:", list(haz.keys()))
    st.error(f"**Peringatan:** {haz[p]}")
    st.info("Aturan Wajib Lab:\n1. Selalu Gunakan Jas Lab\n2. Gunakan Goggles/Kacamata Pelindung\n3. Dilarang keras makan/minum di area lab")

elif menu == "📋 Generator Diagram Alir":
    st.title("📋 Pembuat Diagram Alir Praktikum")
    teks = st.text_area("Masukkan Prosedur (Satu langkah per baris):", "Timbang 2g bahan padat\nLarutkan ke dalam 50ml akuades\nAduk menggunakan batang pengaduk\nMasukkan ke dalam labu ukur 100ml\nTambahkan air sampai tanda batas")
    if st.button("Generate Diagram", use_container_width=True):
        lines = [l.strip() for l in teks.split('\n') if l.strip()]
        mm = "graph TD\n"
        for i, line in enumerate(lines):
            mm += f'    Node{i}["{line}"]\n'
            if i > 0: mm += f'    Node{i-1} --> Node{i}\n'
        html = f"""<div class="mermaid">{mm}</div><script type="module">import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';mermaid.initialize({{startOnLoad:true, theme:'dark'}});</script>"""
        components.html(html, height=len(lines)*100)

elif menu == "🤖 Asisten AI Kimia":
    col_t, col_b = st.columns([4, 1])
    with col_t:
        st.title("🤖 ChemBot (Visual Assistant)")
        st.caption("Sebutkan alat lab atau senyawa kimia yang ingin kamu visualisasikan.")
    with col_b:
        if st.button("🗑️ Reset Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    if "messages" not in st.session_state or len(st.session_state.messages) == 0:
        st.session_state.messages = [{"role": "assistant", "content": "Halo! Saya ChemBot. Butuh visualisasi alat lab seperti **'buret'** atau struktur kimia seperti **'aspirin'**?", "image": None}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("image"): tampilkan_gambar_aman(msg["image"])

    if prompt := st.chat_input("Ketik di sini (contoh: tolong carikan corong pisah)"):
        st.session_state.messages.append({"role": "user", "content": prompt, "image": None})
        with st.chat_message("user"): st.markdown(prompt)

        prompt_l = prompt.lower()
        junk = ["tolong", "tampilkan", "carikan", "gambar", "foto", "apa", "itu", "dari", "dong", "cari", "kasih", "lihat"]
        kunci = prompt_l
        for j in junk: kunci = kunci.replace(j, "").strip()

        sinonim = {
            "beaker glass": "gelas kimia", "beaker": "gelas kimia", "gelas beker": "gelas kimia",
            "erlenmeyer": "labu erlenmeyer", "pipet gondok": "pipet volume", "mortal": "mortar dan alu",
            "lumpang": "mortar dan alu", "alu": "mortar dan alu", "timbangan": "neraca analitik",
            "tripod": "kaki tiga", "crucible": "krusibel", "centrifuge": "sentrifugasi",
            "statif": "klem dan statif", "klem": "klem dan statif", "pemanas": "pembakar bunsen",
            "bunsen": "pembakar bunsen", "pembakar spiritus": "pembakar bunsen", "kertas ph": "indikator universal"
        }
        for s, b in sinonim.items():
            if s in kunci: kunci = kunci.replace(s, b)

        res_txt, res_img, ketemu = "", None, False

        for alat, link in DATABASE_ALAT.items():
            if alat in kunci:
                res_txt, res_img, ketemu = f"🧪 Ini adalah visualisasi dari **{alat.title()}**.", link, True
                break
        
        if not ketemu and kunci:
            p_img, p_txt = cari_struktur_pubchem(kunci)
            if p_img: res_txt, res_img, ketemu = p_txt, p_img, True
            
        if not ketemu and kunci:
            w_img, w_txt = cari_gambar_wikipedia_pro(kunci)
            if w_img: res_txt, res_img, ketemu = w_txt, w_img, True

        if not ketemu:
            if any(k in prompt_l for k in ["bahaya", "k3", "aman", "jas lab"]):
                res_txt = "🛡️ **Keamanan adalah prioritas!** Selalu gunakan jas lab, kacamata pelindung, dan sarung tangan sebelum eksperimen."
            elif any(k in prompt_l for k in ["halo", "hai", "pagi", "siang"]):
                res_txt = "Halo! Senang bertemu denganmu. Ada alat laboratorium atau senyawa kimia yang ingin dicari?"
            else:
                res_txt = f"Maaf, saya belum menemukan visualisasi untuk **'{kunci}'**. Pastikan ejaannya benar atau gunakan nama standar."

        with st.chat_message("assistant"):
            st.markdown(res_txt)
            if res_img: tampilkan_gambar_aman(res_img)
        
        st.session_state.messages.append({"role": "assistant", "content": res_txt, "image": res_img})

elif menu == "📚 Pustaka Jurnal Pro":
    st.title("📚 Pustaka Jurnal Ilmiah Pro")
    st.caption("Mesin pencari pintar untuk menemukan literatur, paper, dan jurnal kimia terpercaya berbasis DOI (Crossref).")
    
    with st.container(border=True):
        col_search, col_year, col_num = st.columns([3, 1, 1])
        with col_search:
            kata_kunci = st.text_input("Ketik Topik Riset (Disarankan Bahasa Inggris):", "Green Chemistry", placeholder="Contoh: Titration, Nanomaterials...")
        with col_year:
            tahun_min = st.selectbox("Terbitan Sejak Tahun:", [2024, 2023, 2020, 2015, 2010], index=2)
        with col_num:
            max_hasil = st.number_input("Maksimal Hasil:", 1, 20, 5)
            
        gas_cari = st.button("🔍 Cari Jurnal", type="primary", use_container_width=True)

    if gas_cari:
        if kata_kunci:
            with st.spinner("⏳ Menjelajahi database akademik global..."):
                hasil_jurnal = cari_jurnal_akademik(kata_kunci, tahun_min, max_hasil)
                
            if hasil_jurnal:
                st.success(f"Berhasil menemukan {len(hasil_jurnal)} jurnal relevan untuk **'{kata_kunci}'**")
                
                for i, jurnal in enumerate(hasil_jurnal):
                    judul = jurnal.get('title', ['Judul Tidak Tersedia'])[0]
                    doi = jurnal.get('DOI', 'Tidak ada DOI')
                    url_jurnal = jurnal.get('URL', '#')
                    sitasi_count = jurnal.get('is-referenced-by-count', 0)
                    publisher = jurnal.get('publisher', 'Penerbit Tidak Diketahui')
                    
                    try:
                        tahun_terbit = jurnal['published']['date-parts'][0][0]
                    except:
                        tahun_terbit = "Tahun N/A"
                        
                    penulis_list = jurnal.get('author', [])
                    nama_penulis = []
                    for p in penulis_list[:3]:
                        if 'given' in p and 'family' in p:
                            nama_penulis.append(f"{p['family']}, {p['given'][0]}.")
                        elif 'name' in p:
                            nama_penulis.append(p['name'])
                    
                    penulis_str = ", ".join(nama_penulis) if nama_penulis else "Penulis Anonim"
                    if len(penulis_list) > 3: penulis_str += " et al."

                    with st.expander(f"📄 {judul} ({tahun_terbit})"):
                        st.markdown(f"**Penulis:** {penulis_str}")
                        st.markdown(f"**Penerbit:** {publisher}")
                        st.markdown(f"**Telah disitasi oleh:** `{sitasi_count} penelitian`")
                        st.markdown(f"**Link DOI:** [{doi}]({url_jurnal})")
                        
                        st.link_button("🌐 Buka Halaman Jurnal Asli", url_jurnal)
                        
                        st.divider()
                        sitasi_apa = f"{penulis_str} ({tahun_terbit}). {judul}. *{publisher}*. https://doi.org/{doi}"
                        st.text_area("📋 Copy Sitasi Otomatis (Format APA):", sitasi_apa, height=68, key=f"sitasi_{i}")
            else:
                st.warning("Maaf, tidak ditemukan jurnal yang cocok. Coba gunakan kata kunci bahasa Inggris yang berbeda atau perluas rentang tahun.")
        else:
            st.error("Masukkan topik riset terlebih dahulu sebelum mencari.")