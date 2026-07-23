import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# Set Konfigurasi Halaman
st.set_page_config(
    page_title="Akselerator Label SPP-IRT Dinkes",
    page_icon="🏷️",
    layout="centered"
)

# Inisialisasi API Key dari Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

st.title("🏷️ Akselerator Label SPP-IRT Dinkes")
st.caption("Sistem Otomatisasi & Kompilasi Draf Label P-IRT Berbasis Standar Regulasi BPOM (Powered by Gemini AI)")

tab1, tab2 = st.tabs(["📄 Tahap 1: Kompilasi Teks (v3.3)", "🎨 Tahap 2: Layout Visual (v8.5)"])

# ==========================================
# TAB 1: KOMPILASI TEKS
# ==========================================
with tab1:
    st.header("📄 Langkah 1: Normalisasi EYD & Filter Alergen")
    
    input_text = st.text_area(
        "📝 Input Data Mentah UMKM:",
        height=200,
        placeholder="Paste data mentah produk UMKM di sini..."
    )
    
    if st.button("🚀 Proses Kompilasi Teks BPOM", key="btn_tab1"):
        if not api_key:
            st.error("❌ GEMINI_API_KEY belum dikonfigurasi di Streamlit Secrets!")
        elif not input_text.strip():
            st.warning("⚠️ Mohon masukkan data mentah UMKM terlebih dahulu.")
        else:
            with st.spinner("Sedang memproses teks sesuai regulasi BPOM..."):
                try:
                    # Menggunakan model Gemini 1.5 Flash (Sangat Cepat & Pintar)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""
                    Anda adalah pakar regulasi kompilasi label pangan SPP-IRT Dinkes dan BPOM.
                    Tugas Anda adalah merapikan data mentah UMKM berikut menjadi teks draf label matang yang patuh standar BPOM.

                    Aturan Wajib:
                    1. Perbaiki penulisan EYD, kapitalisasi, dan ejaan.
                    2. Identifikasi bahan Alergen pada komposisi (seperti: kedelai, tepung terigu, telur, kacang, udang, susu, dll) dan Wajib CETAK TEBAL (contoh: **kedelai**).
                    3. Format nomor izin P-IRT, berat bersih, dan informasi produsen secara rapi.
                    4. Susun output dalam format poin-poin label resmi yang mudah dibaca.

                    Data Mentah UMKM:
                    {input_text}
                    """
                    
                    response = model.generate_content(prompt)
                    
                    st.success("✅ Teks Berhasil Dikompilasi!")
                    st.subheader("📋 Hasil Kompilasi Teks BPOM:")
                    st.text_area("Salin Teks Di Bawah Ini:", value=response.text, height=300)
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

# ==========================================
# TAB 2: LAYOUT VISUAL & VISION AI
# ==========================================
with tab2:
    st.header("🎨 Langkah 2: Evaluasi Layout Visual & Draf Supreme")
    
    input_matang = st.text_area(
        "📋 Paste Teks Matang dari Tahap 1:",
        height=200,
        placeholder="Paste teks hasil kompilasi Tahap 1 di sini..."
    )
    
    # Cek keberadaan file gambar jangkar
    template_path = "supreme template.jpg"
    image_loaded = None
    
    if os.path.exists(template_path):
        try:
            image_loaded = Image.open(template_path)
            st.info("👁️ Gambar jangkar 'supreme template.jpg' terdeteksi dan dikirim ke Vision AI.")
        except Exception as e:
            st.warning(f"⚠️ Berkas 'supreme template.jpg' ditemukan tapi gagal dibuka: {e}")
    else:
        st.warning("⚠️ Gambar jangkar 'supreme template.jpg' tidak ditemukan di repository. Analisis vision dijalankan tanpa acuan gambar jangkar.")

    if st.button("🎨 Proses Draf Visual Supreme", key="btn_tab2"):
        if not api_key:
            st.error("❌ GEMINI_API_KEY belum dikonfigurasi di Streamlit Secrets!")
        elif not input_matang.strip():
            st.warning("⚠️ Mohon masukkan teks matang dari Tahap 1 terlebih dahulu.")
        else:
            with st.spinner("Vision AI sedang merancang dan mengevaluasi draf visual..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""
                    Anda adalah Desainer Grafis Senior dan Auditor Visual Label Kemasan Kemkes/BPOM.
                    Analisis teks draf label matang berikut ini:
                    
                    {input_matang}
                    
                    Tugas Anda:
                    1. Buatkan rekomendasi tata letak visual (Layout Hierarchy) yang paling estetis, proporsional, dan sesuai regulasi BPOM.
                    2. Tentukan posisi elemen kunci: Mana yang di Fasad Depan (Front Panel) dan mana yang di Fasad Belakang/Samping (Back/Side Panel).
                    3. Berikan saran kontras warna, pembagian area logo halal, nomor P-IRT, komposisi, serta tabel nilai gizi (jika ada).
                    4. Jika ada gambar jangkar template yang disertakan, bandingkan hirarki teks ini agar pas dengan tata letak visual template tersebut.
                    """
                    
                    # Jika ada gambar jangkar, kirimkan Teks + Gambar ke Gemini Vision
                    if image_loaded:
                        response = model.generate_content([prompt, image_loaded])
                    else:
                        response = model.generate_content(prompt)
                        
                    st.success("✅ Analisis & Layout Visual Selesai!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
