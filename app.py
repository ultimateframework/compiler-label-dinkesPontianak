import streamlit as st
from google import genai
from PIL import Image
import os

# Set Konfigurasi Halaman
st.set_page_config(
    page_title="Akselerator Label SPP-IRT Dinkes",
    page_icon="🏷️",
    layout="centered"
)

# Inisialisasi Client dari Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    client = genai.Client(api_key=api_key)

st.title("🏷️ Akselerator Label SPP-IRT Dinkes")
st.caption("Sistem Otomatisasi & Kompilasi Draf Label P-IRT Berbasis Standar Regulasi BPOM")

tab1, tab2 = st.tabs(["📄 Tahap 1: Kompilasi Teks (v3.3)", "🎨 Tahap 2: Layout Visual (v8.5)"])

# ==========================================
# TAB 1: BPOM_LABEL_COMPILER_v3.3_PSEUDO
# ==========================================
with tab1:
    st.header("📄 Langkah 1: Normalisasi EYD & Filter Alergen (v3.3)")
    
    input_text = st.text_area(
        "📝 Input Data Mentah UMKM:",
        height=220,
        placeholder="Paste data mentah produk UMKM di sini..."
    )
    
    if st.button("🚀 Proses Kompilasi Teks BPOM", key="btn_tab1"):
        if not api_key:
            st.error("❌ GEMINI_API_KEY belum dikonfigurasi di Streamlit Secrets!")
        elif not input_text.strip():
            st.warning("⚠️ Mohon masukkan data mentah UMKM terlebih dahulu.")
        else:
            with st.spinner("Sedang menjalankan BPOM_LABEL_COMPILER_v3.3_PSEUDO..."):
                try:
                    prompt = f"""
                    // ==============================================================================
                    // [SYSTEM_COMPILER] : BPOM_LABEL_COMPILER_v3.3_PSEUDO
                    // [ARCHITECT] : DYAN AL MATARAMI | SPP-IRT PONTIANAK
                    // [MODE] : STRICT_EXECUTION // ZERO_CONVERSATION // HIGH_LEVEL_PSEUDO
                    // ==============================================================================

                    ROLE: BPOM Regulatory AI, EYD Normalizer & Label Compiler
                    OUTPUT_MODE: RAW_TEXT_ONLY_STRICT_TEMPLATE

                    ATURAN MUTLAK & EXECUTION PIPELINE:
                    1. Terapkan Apply_EYD_Title_Case: Ubah ke Title Case, tapi KATA HUBUNG / PREPOSISI WAJIB HURUF KECIL ("dan", "atau", "di", "ke", "dari", "pada", "untuk", "dengan", "oleh") kecuali di awal kalimat.
                    2. Format_Composition: 
                       - Urutkan bahan berdasarkan estimasi volume terbanyak.
                       - Terapkan EYD Title Case.
                       - Pisahkan dengan koma, dan ganti koma terakhir dengan ", dan ".
                       - Pastikan diakhiri dengan tanda titik.
                    3. Extract_Raw_Allergens berdasarkan Allergen_Map:
                       - Gandum: Tepung Terigu, Gandum, Oat, Barley, Rye, Tepung Roti.
                       - Telur: Telur, Kuning Telur, Putih Telur, Telur Ayam, Telur Bebek.
                       - Susu: Susu, Keju, Margarin, Mentega, Butter, Krim, Whey, Laktosa, Kental Manis.
                       - Kacang Tanah: Kacang Tanah, Selai Kacang, Peanut.
                       - Kacang Pohon: Almond, Mete, Cashew, Kacang Mede, Hazelnut, Walnut, Pistachio, Macadamia, Pecan, Kacang Kenari.
                       - Kedelai: Kedelai, Kecap, Tahu, Tempe, Edamame, Minyak Kedelai.
                       - Krustasea/Ikan: Ikan, Udang, Ebi, Rebon, Terasi, Kepiting, Lobster, Kerang, Tiram, Cumi, Gurita, Kecap Ikan, Saus Tiram.
                       - Sulfit: Sulfit, Sulfur Dioksida, Belerang Dioksida, Natrium Metabisulfit, Kalium Metabisulfit.
                    4. Generate_Allergen_Warning:
                       - Jika TIDAK ADA alergen: "Bebas Alergen Utama, Tidak Mengandung Gandum, Susu, Telur, Kedelai, atau Kacang-kacangan."
                       - Jika ADA alergen: "Lihat Daftar Bahan Yang Dicetak Tebal."
                    5. STRICT TEMPLATE OUTPUT: JANGAN TAMBAH BASA-BASI, SAPAAN, ATAU PENJELASAN APAPUN. Cetak HANYA format di bawah ini persis, jangan ubah satu huruf pun di sebelah kiri tanda titik dua (:).

                    TEMPLATE WAJIB:
                    tema & warna : [isi]
                    merk : [isi]
                    produk : [isi]
                    diproduksi oleh : [isi]
                    komposisi : [isi]
                    bahan baku mengandung alergen : [isi]
                    informasi alergen (Ya/Tidak) : [isi]
                    nomor izin : [isi]
                    berat bersih : [isi]
                    whatsapp (Ya/Tidak/Isi Baru) : [isi]
                    instagram (Ya/Tidak/Isi Baru) : [isi]
                    logo halal (Ya/Tidak/Isi Baru) : [isi]

                    [DATA_INPUT]:
                    {input_text}
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=prompt,
                    )
                    
                    st.success("✅ Teks Berhasil Dikompilasi!")
                    st.subheader("📋 Hasil Output Strict Compiler v3.3:")
                    st.text_area("Salin Teks Di Bawah Ini untuk Tahap 2:", value=response.text, height=320)
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

# ==========================================
# TAB 2: BPOM_IMAGE_GEN_v8.5_STRICT_SUPREME
# ==========================================
with tab2:
    st.header("🎨 Langkah 2: Layout Visual & Draf Supreme (v8.5)")
    
    input_matang = st.text_area(
        "📋 Paste Output Hasil Compiler v3.3 dari Tahap 1:",
        height=220,
        placeholder="Paste teks hasil kompilasi Tahap 1 di sini..."
    )
    
    # Cek keberadaan file gambar jangkar
    template_path = "supreme template.png"
    image_loaded = None
    
    if os.path.exists(template_path):
        try:
            image_loaded = Image.open(template_path)
            st.info("👁️ Gambar jangkar 'supreme template.png' terdeteksi dan dianalisis oleh Vision AI.")
        except Exception as e:
            st.warning(f"⚠️ Berkas 'supreme template.png' ditemukan tapi gagal dibuka: {e}")
    else:
        st.warning("⚠️ Gambar jangkar 'supreme template.png' tidak ditemukan di repository. Analisis vision dijalankan tanpa acuan gambar jangkar.")

    if st.button("🎨 Proses Draf Visual Supreme v8.5", key="btn_tab2"):
        if not api_key:
            st.error("❌ GEMINI_API_KEY belum dikonfigurasi di Streamlit Secrets!")
        elif not input_matang.strip():
            st.warning("⚠️ Mohon masukkan hasil kompilasi v3.3 dari Tahap 1 terlebih dahulu.")
        else:
            with st.spinner("Vision AI sedang mengeksekusi BPOM_IMAGE_GEN_v8.5_STRICT_SUPREME..."):
                try:
                    prompt = f"""
                    // ==============================================================================
                    // [SYSTEM_COMPILER] : BPOM_IMAGE_GEN_v8.5_STRICT_SUPREME
                    // DEVELOPER/ARCHITECT: DYAN AL MATARAMI | SPP-IRT PONTIANAK ACCELERATION PROJECT
                    // TARGET_ANCHOR: "supreme template.png" (Strict Geometrical Anatomy & Cluster Layout)
                    // DIRECTIVE: SMART_ALLERGEN_BOLDING // ABSOLUTE_MANUAL_OVERRIDE // ZERO_HALLUCINATION
                    // ==============================================================================

                    <Security_Protocol>
                      DYAN_AL_MATARAMI
                    </Security_Protocol>

                    <System_Directive>
                      Act as a "Lead Creative Director & BPOM Compliance Specialist".
                      Transform [DATA_INPUT] into a high-end food label visual layout breakdown using the EXACT geometric layout of the anchor template "supreme template.png".
                    </System_Directive>

                    <Dynamic_Data_Logic>
                      [FALLBACK_&_OMISSION_PROTOCOL]:
                      1. Jika field terisi (misal: Ya / Data Baru): Gunakan teks/logo tersebut.
                      2. Jika field Kosong / "Tidak/No": OMIT COMPLETELY (Hilangkan total area WA/IG/Halal).

                      [SMART_COMPOSITION_PROTOCOL]:
                      - Default: Cetak seluruh bahan dalam huruf normal (100% normal weight).
                      - AUTO_ALLERGEN_BOLDING: Pindai kata-kata dari [bahan baku mengandung alergen]. Cari kata persis tersebut di dalam [komposisi] dan OTOMATIS CETAK TEBAL (BOLD) HANYA pada kata alergen tersebut. Sisa bahan wajib tetap cetak normal.

                      [ALLERGEN_TEMPLATE_PROTOCOL]:
                      - Timpa string default "Lihat Daftar Bahan Yang Dicetak Tebal." pada gambar jangkar dengan APAPUN string yang ada pada field [informasi alergen (Ya/Tidak)].
                    </Dynamic_Data_Logic>

                    <Visual_Innovation_Logic>
                      [P5_Render] Hirarki Tata Letak "supreme template.png":
                      1. [TOP_CENTER]: BRAND_NAME (UPPERCASE, Bold) -> Di atas foto lingkaran.
                      2. [CORE_CENTER]: Foto produk terpotong LINGKARAN sempurna (1:1).
                      3. [MIDDLE_CENTER]: PRODUCT_NAME (UPPERCASE, Bold, Font Terbesar) -> Tepat di bawah foto lingkaran.
                      4. [SUB_MIDDLE_CENTER]: Nomor P-IRT -> Tepat di bawah Nama Produk.
                      5. [MIDDLE_LEFT]: "Kode produksi:" & "Baik digunakan sebelum:" dengan kotak putih.
                      6. [MIDDLE_RIGHT]: LOGO HALAL + ID (HANYA jika dipicu logic).
                      7. [BOTTOM_GRID - LEFT]: "Diproduksi oleh:" diikuti [diproduksi oleh], dan baris baru "Pontianak, Kalimantan Barat". ATURAN MUTLAK: ZERO BOLD TEXT (Gunakan 100% normal weight font).
                      8. [BOTTOM_GRID - CENTER]: Container putih bulat: [komposisi] (Alergen dicetak tebal) + [informasi alergen].
                      9. [BOTTOM_GRID - RIGHT]: "Berat Bersih:" diikuti SATU BARIS SIMBOL LINGKARAN: "○ [berat bersih]". ATURAN MUTLAK: Dilarang membuat list/checkbox, HANYA 1 BARIS.
                    </Visual_Innovation_Logic>

                    <Output_Sequence>
                      Susun hasil balasan dalam urutan persis seperti berikut:

                      [HASIL ATURAN LABEL ANDA - v8.5-STRICT-SUPREME]
                      1. (BRAND/MERK): [merk] 
                      2. NAMA PRODUK: [produk] 
                      3. Diproduksi Oleh: [diproduksi oleh], Pontianak, Kalimantan Barat.
                      4. Kontak: WA [whatsapp] | IG [instagram] *(Jika kosong/tidak = dihilangkan)*
                      5. Status Halal: [logo halal] *(Jika kosong/tidak = dihilangkan)*
                      6. Komposisi: [Status Eksekusi: Teks dicetak normal, mendeteksi dan menebalkan alergen: "[bahan baku mengandung alergen]"]
                      7. Informasi Alergen: [Status Eksekusi: Menimpa teks jangkar dengan instruksi input mutlak]
                      8. Berat Bersih: [Status Eksekusi: HANYA 1 BARIS MUTLAK]
                      9. Nomor Izin: [nomor izin]
                      ---
                      [EVALUASI LAYOUT VISUAL & ANATOMI GEOMETRIS]
                      (Berikan instruksi tata letak visual detail sesuai P5_Render di atas)
                      ---
                      [Draf Label Otomatis v8.5 Strict-Supreme • Dikembangkan secara swadaya oleh Dyan Al Matarami untuk Akselerasi SPP-IRT Dinkes. Hasil wajib diverifikasi otoritas berwenang.]
                    </Output_Sequence>

                    [DATA_INPUT]:
                    {input_matang}
                    """
                    
                    if image_loaded:
                        contents = [prompt, image_loaded]
                    else:
                        contents = [prompt]

                    response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=contents,
                    )
                        
                    st.success("✅ Analisis Visual v8.5 Strict-Supreme Selesai!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
