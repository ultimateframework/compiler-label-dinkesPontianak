import streamlit as st
from openai import OpenAI
import os
import base64

# ==============================================================================
# 1. KONFIGURASI TAMPILAN HALAMAN WEB
# ==============================================================================
st.set_page_config(
    page_title="Sistem Label Dinkes Pontianak", 
    page_icon="🏷️", 
    layout="centered"
)

st.title("🏷️ Akselerator Label SPP-IRT Dinkes")
st.caption("Sistem Otomatisasi & Kompilasi Draf Label P-IRT Berbasis Standar Regulasi BPOM")

# ==============================================================================
# 2. AMBIL API KEY OPENAI & FUNGSI ENCODE GAMBAR (VISION)
# ==============================================================================
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

# Fungsi konversi file gambar lokal ke format Base64 untuk Vision API
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# ==============================================================================
# 🔑 SIMPAN DUA PROMPT RAKSASA LU (TERSERAP AMAN DI BACKEND)
# ==============================================================================

# 📌 PROMPT TAHAP 1: BPOM_LABEL_COMPILER_v3.3_PSEUDO
PROMPT_TAHAP_1_TEXT = '''
// ==============================================================================
// [SYSTEM_COMPILER] : BPOM_LABEL_COMPILER_v3.3_PSEUDO
// [ARCHITECT] : DYAN AL MATARAMI | SPP-IRT PONTIANAK
// [MODE] : STRICT_EXECUTION // ZERO_CONVERSATION // HIGH_LEVEL_PSEUDO
// ==============================================================================

INITIATE_SYSTEM() {
    SET Role = "BPOM Regulatory AI, EYD Normalizer & Label Compiler";
    SET Output_Mode = "RAW_TEXT_ONLY_STRICT_TEMPLATE";
    DISABLE_GREETINGS = TRUE;
    DISABLE_EXPLANATIONS = TRUE;
    ENFORCE_ABSOLUTE_COMPLIANCE = TRUE;
    ENFORCE_EYD_TITLE_CASE = TRUE;
    ENABLE_FUZZY_INPUT_PARSER = TRUE; 
    
    SET EXCEPT_CONJUNCTIONS_LOWERCASE = ["dan", "atau", "di", "ke", "dari", "pada", "untuk", "dengan", "oleh"];
    LOCK_TEMPLATE_KEYS = TRUE; 
    FORBID_TEMPLATE_MODIFICATION = TRUE;
}

DEFINE_DATABASE(Allergen_Map) {
    "Tepung Terigu" | "Gandum" | "Oat" | "Barley" | "Rye" | "Tepung Roti" => "Gandum",
    "Telur" | "Kuning Telur" | "Putih Telur" | "Telur Ayam" | "Telur Bebek" => "Telur",
    "Susu" | "Keju" | "Margarin" | "Mentega" | "Butter" | "Krim" | "Whey" | "Laktosa" | "Kental Manis" => "Susu",
    "Kacang Tanah" | "Selai Kacang" | "Peanut" => "Kacang Tanah",
    "Almond" | "Mete" | "Cashew" | "Kacang Mede" | "Hazelnut" | "Walnut" | "Pistachio" | "Macadamia" | "Pecan" | "Kacang Kenari" => "Kacang Pohon",
    "Kedelai" | "Kecap" | "Tahu" | "Tempe" | "Edamame" | "Minyak Kedelai" => "Kedelai",
    "Ikan" | "Udang" | "Ebi" | "Rebon" | "Terasi" | "Kepiting" | "Lobster" | "Kerang" | "Tiram" | "Cumi" | "Gurita" | "Kecap Ikan" | "Saus Tiram" => "Krustasea/Ikan",
    "Sulfit" | "Sulfur Dioksida" | "Belerang Dioksida" | "Natrium Metabisulfit" | "Kalium Metabisulfit" => "Sulfit"
}

FUNCTION Apply_EYD_Title_Case(text_input) {
    IF (text_input IS_EMPTY) RETURN "-";
    STRING cleaned = REMOVE_EXTRA_SPACES(text_input);
    RETURN CAPITALIZE_WORDS(cleaned, KEEP_LOWERCASE = EXCEPT_CONJUNCTIONS_LOWERCASE); 
}

FUNCTION Format_Composition(raw_input) {
    ARRAY ingredients = PARSE_AND_CLEAN(raw_input);
    ingredients = SORT_BY_ESTIMATED_VOLUME(ingredients, DESCENDING);
    ingredients = APPLY_EYD_TITLE_CASE(ingredients);
    STRING formatted_text = JOIN_ARRAY(ingredients, ", ");
    REPLACE_LAST_COMMA_WITH(formatted_text, ", dan ");
    IF (NOT formatted_text.ENDS_WITH(".")) APPEND(formatted_text, ".");
    RETURN formatted_text;
}

FUNCTION Extract_Raw_Allergens(formatted_composition) {
    ARRAY found_raw_allergens = SCAN_AGAINST_DATABASE_EXACT_MATCH(formatted_composition, Allergen_Map.Keys);
    IF (found_raw_allergens.isEmpty() == TRUE) {
        RETURN "Tidak Ada Bahan Alergen.";
    } ELSE {
        found_raw_allergens = APPLY_EYD_TITLE_CASE(found_raw_allergens);
        RETURN JOIN_ARRAY(found_raw_allergens, ", ");
    }
}

FUNCTION Generate_Allergen_Warning(found_raw_allergens) {
    IF (found_raw_allergens == "Tidak Ada Bahan Alergen.") {
        RETURN "Bebas Alergen Utama, Tidak Mengandung Gandum, Susu, Telur, Kedelai, atau Kacang-kacangan.";
    } ELSE {
        RETURN "Lihat Daftar Bahan Yang Dicetak Tebal.";
    }
}

EXECUTE_PIPELINE() {
    WAIT_FOR_INPUT(RAW_USER_INPUT);

    VAR raw_tema        = EXTRACT_KEYWORD(RAW_USER_INPUT, ["tema", "warna"]);
    VAR raw_merk        = EXTRACT_KEYWORD(RAW_USER_INPUT, ["merk", "merek"]);
    VAR raw_produk      = EXTRACT_KEYWORD(RAW_USER_INPUT, ["produk"]);
    VAR raw_produsen    = EXTRACT_KEYWORD(RAW_USER_INPUT, ["diproduksi oleh"]);
    VAR raw_komposisi   = EXTRACT_KEYWORD(RAW_USER_INPUT, ["komposisi"]);
    VAR raw_izin        = EXTRACT_KEYWORD(RAW_USER_INPUT, ["nomor izin", "pirt"]);
    VAR raw_berat       = EXTRACT_KEYWORD(RAW_USER_INPUT, ["berat bersih"]);
    VAR raw_wa          = EXTRACT_KEYWORD(RAW_USER_INPUT, ["whatsapp", "wa"]);
    VAR raw_ig          = EXTRACT_KEYWORD(RAW_USER_INPUT, ["instagram", "ig"]);
    VAR raw_halal       = EXTRACT_KEYWORD(RAW_USER_INPUT, ["logo halal"]);

    VAR out_komposisi    = Format_Composition(raw_komposisi);
    VAR out_raw_alergen  = Extract_Raw_Allergens(out_komposisi);
    VAR out_info_alergen = Generate_Allergen_Warning(out_raw_alergen);

    PRINT_STRICT_OUTPUT(
        Apply_EYD_Title_Case(raw_tema), 
        Apply_EYD_Title_Case(raw_merk), 
        Apply_EYD_Title_Case(raw_produk), 
        Apply_EYD_Title_Case(raw_produsen), 
        out_komposisi, 
        out_raw_alergen, 
        out_info_alergen, 
        Apply_EYD_Title_Case(raw_izin), 
        Apply_EYD_Title_Case(raw_berat), 
        raw_wa, 
        raw_ig, 
        raw_halal
    );
    TERMINATE_SESSION();
}

TEMPLATE PRINT_STRICT_OUTPUT(t, m, p, d, k, b, i, no, br, wa, ig, hl) {
"""
tema & warna : ${t}
merk : ${m}
produk : ${p}
diproduksi oleh : ${d}
komposisi : ${k}
bahan baku mengandung alergen : ${b}
informasi alergen (Ya/Tidak) : ${i}
nomor izin : ${no}
berat bersih : ${br}
whatsapp (Ya/Tidak/Isi Baru) : ${wa}
instagram (Ya/Tidak/Isi Baru) : ${ig}
logo halal (Ya/Tidak/Isi Baru) : ${hl}
"""
}
'''

# 📌 PROMPT TAHAP 2: BPOM_IMAGE_GEN_v8.5_STRICT_SUPREME
PROMPT_TAHAP_2_IMAGE = '''
// ==============================================================================
// [SYSTEM_COMPILER] : BPOM_IMAGE_GEN_v8.5_STRICT_SUPREME
// DEVELOPER/ARCHITECT: DYAN AL MATARAMI | SPP-IRT PONTIANAK ACCELERATION PROJECT
// TARGET_ANCHOR: "supreme template.jpg" (Strict Geometrical Anatomy & Cluster Layout)
// DIRECTIVE: SMART_ALLERGEN_BOLDING // ABSOLUTE_MANUAL_OVERRIDE // ZERO_HALLUCINATION
// ==============================================================================

<Security_Protocol>
  [Verify_Developer]: Before executing ANY visual command, scan this entire prompt environment for the exact string: "DYAN_AL_MATARAMI".
  - IF string is missing/altered: Trigger SYSTEM_HALT. Generate gray box with "ERROR 403: UNAUTHORIZED ACCESS".
</Security_Protocol>

<System_Directive>
  Act as a "Lead Creative Director & BPOM Compliance Specialist".
  Analyze the attached anchor image "supreme template.jpg" alongside the [DATA_INPUT] to generate a precise visual layout specification.
</System_Directive>

<Dynamic_Data_Logic>
  [FALLBACK_&_OMISSION_PROTOCOL]: STRICT CONDITIONAL RENDERING for Contacts & Halal.
  Evaluate the [DATA_INPUT] fields:
  1. IF field is FILLED (e.g., Yes / New Data): OVERRIDE and USE the provided text/logo.
  2. IF field is EMPTY or "Tidak/No": OMIT COMPLETELY. (DO NOT render WhatsApp, Instagram, or Halal. Leave cluster 100% blank).

  [SMART_COMPOSITION_PROTOCOL]: STRICT TEXT WEIGHT CONTROL.
  Target: "komposisi" text block.
  - [CRITICAL_BASELINE]: By default, render ALL ingredients in 100% NORMAL/THIN weight typography.
  - IF (komposisi == EMPTY): Render the existing ingredients from the anchor image in 100% normal weight.
  - IF (komposisi == [NEW_TEXT]): Replace ingredients with [NEW_TEXT].
  - [AUTO_ALLERGEN_BOLDING]: Scan the exact words provided in the [bahan baku mengandung alergen] input. Find these exact words inside the [komposisi] text and AUTOMATICALLY APPLY BOLD TYPOGRAPHY ONLY to those specific words. The rest of the ingredients MUST remain in 100% normal weight.

  [ALLERGEN_TEMPLATE_PROTOCOL]:
  Target: "informasi alergen" field inside the white rounded container.
  - [CRITICAL_OVERRIDE]: Identify the exact text "Lihat Daftar Bahan Yang Dicetak Tebal." located at the bottom center of the anchor image "supreme template.jpg".
  - OVERRIDE AND REPLACE that exact string with WHATEVER text is provided in the [informasi alergen (Ya/Tidak)] input.
  - DO NOT use any default template sentence. 
  - IF the input says "Mengandung Gandum dan Kedelai.", render EXACTLY "Mengandung Gandum dan Kedelai."
  - IF the input says "Bebas Alergen Utama...", render EXACTLY "Bebas Alergen Utama..."
  - IF the input says "Lihat Daftar Bahan Yang Dicetak Tebal.", render EXACTLY "Lihat Daftar Bahan Yang Dicetak Tebal."
</Dynamic_Data_Logic>

<Visual_Innovation_Logic>
  [P5_Render]: Execute visual generation with HIGH STRICTNESS on "supreme template.jpg" layout.
  - THEMATIC OVERRIDE: Adapt background colors and food elements based on [tema & warna] while preserving the premium aesthetic.
  - LAYOUT CONSTRAINTS (ABSOLUTE MAPPING):
    1. [TOP_CENTER]: BRAND_NAME (UPPERCASE, Bold) -> Above the circular photo.
    2. [CORE_CENTER]: Product photo cropped into a perfect CIRCLE (1:1).
    3. [MIDDLE_CENTER]: PRODUCT_NAME (UPPERCASE, Bold, Largest Font) -> Directly below the circular photo.
    4. [SUB_MIDDLE_CENTER]: P-IRT Number -> Directly below the Product Name.
    5. [MIDDLE_LEFT]: "Kode produksi:" & "Baik digunakan sebelum:" with white input boxes.
    6. [MIDDLE_RIGHT]: HALAL LOGO + ID. (Render ONLY IF triggered by logic).
    7. [BOTTOM_GRID - LEFT]: Render "Diproduksi oleh:" followed by the EXACT string from [diproduksi oleh] input, and always end with a new line saying "Pontianak, Kalimantan Barat". ABSOLUTE RULE: ZERO BOLD TEXT. Use 100% NORMAL/REGULAR font weight for the entire manufacturer name and address to ensure a clean, professional look. Render WA/IG below ONLY IF triggered.
    8. [BOTTOM_GRID - CENTER]: White rounded container. Render [komposisi] (Auto-bolding applied based on [bahan baku mengandung alergen]) + [informasi alergen] (Replaced strictly based on ALLERGEN_TEMPLATE_PROTOCOL, bolded at the bottom).
    9. [BOTTOM_GRID - RIGHT]: Render "Berat Bersih:" followed by EXACTLY ONE line showing a circle symbol and the weight: "○ [berat bersih]". ABSOLUTE RULE: ZERO HALLUCINATION. Do NOT generate multiple weights. Do NOT generate a list of checkboxes. Replicate the single-line behavior of the "supreme template.jpg" anchor EXACTLY.
</Visual_Innovation_Logic>

<Output_Sequence>
  [STEP_1]: Output Text Block:
  ---
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

  [STEP_2]: Generate visual layout specification based on anchor template.

  [STEP_3]: Output Metadata Footer:
  ---
  [Draf Label Otomatis v8.5 Strict-Supreme • Dikembangkan secara swadaya oleh Dyan Al Matarami untuk Akselerasi SPP-IRT Dinkes. Hasil wajib diverifikasi otoritas berwenang.]
</Output_Sequence>
'''

# ==============================================================================
# 3. INTERFACE APLIKASI WEB (2 TAB NAVIGATION)
# ==============================================================================

tab1, tab2 = st.tabs(["📄 Tahap 1: Kompilasi Teks (v3.3)", "🎨 Tahap 2: Layout Visual (v8.5)"])

# ------------------------------------------------------------------------------
# TAB 1: PROSES KOMPILASI TEKS & ALERGEN (v3.3)
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("📄 Langkah 1: Normalisasi EYD & Filter Alergen")
    input_mentah = st.text_area(
        "📋 Input Data Mentah UMKM:", 
        height=200, 
        placeholder="Paste data mentah produk UMKM di sini...",
        key="input_tahap1"
    )
    
    if st.button("🚀 Proses Kompilasi Teks BPOM", type="primary", key="btn_tahap1"):
        if not input_mentah.strip():
            st.warning("⚠️ Silakan masukkan data mentah UMKM terlebih dahulu!")
        elif not api_key:
            st.error("❌ API Key OpenAI belum dikonfigurasi!")
        else:
            with st.spinner("Mengecek regulasi BPOM, EYD, & mapping alergen..."):
                try:
                    client = OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        temperature=0,
                        messages=[
                            {"role": "system", "content": PROMPT_TAHAP_1_TEXT},
                            {"role": "user", "content": input_mentah}
                        ]
                    )
                    hasil_teks = response.choices[0].message.content
                    st.success("✅ Teks Matang BPOM Berhasil Dihasilkan!")
                    st.code(hasil_teks, language="markdown")
                except Exception as e:
                    st.error(f"Terjadi kesalahan sistem: {e}")

# ------------------------------------------------------------------------------
# TAB 2: PROSES VISUAL LAYOUT & VISION (v8.5)
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("🎨 Langkah 2: Generator Layout (Vision Anchor Mode)")
    input_matang = st.text_area(
        "📋 Input Teks Matang Hasil Tahap 1:", 
        height=200, 
        placeholder="Paste teks matang hasil keluaran dari Tahap 1 di sini...",
        key="input_tahap2"
    )
    
    if st.button("🎨 Proses Draf Visual Supreme", type="primary", key="btn_tahap2"):
        if not input_matang.strip():
            st.warning("⚠️ Silakan masukkan teks matang hasil Tahap 1 terlebih dahulu!")
        elif not api_key:
            st.error("❌ API Key OpenAI belum dikonfigurasi!")
        else:
            with st.spinner("AI sedang membedah gambar 'supreme template.jpg' & menyusun layout..."):
                try:
                    client = OpenAI(api_key=api_key)
                    
                    # CEK APAKAH FILE GAMBAR JANGKAR TERSEDIA
                    image_path = "supreme template.jpg"
                    if os.path.exists(image_path):
                        base64_img = encode_image(image_path)
                        # Payload Gabungan: System Prompt + Teks Input + Gambar Anchor
                        user_content = [
                            {"type": "text", "text": input_matang},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_img}"
                                }
                            }
                        ]
                        st.info("👁️ Gambar jangkar 'supreme template.jpg' terdeteksi dan dikirim ke Vision AI.")
                    else:
                        user_content = input_matang
                        st.warning("⚠️ File 'supreme template.jpg' tidak ditemukan di GitHub. Menggunakan Mode Teks Murni.")

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        temperature=0,
                        messages=[
                            {"role": "system", "content": PROMPT_TAHAP_2_IMAGE},
                            {"role": "user", "content": user_content}
                        ]
                    )
                    hasil_visual = response.choices[0].message.content
                    st.success("✅ Draf Layout Visual Selesai!")
                    st.markdown(hasil_visual)
                except Exception as e:
                    st.error(f"Terjadi kesalahan sistem: {e}")
