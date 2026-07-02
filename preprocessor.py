import pandas as pd
import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from tqdm import tqdm

# ── 📦 RELEVANSI GLOBAL (Dipakai Bersama oleh Dashboard & Training) ──────────
# Komponen di bawah ini tetap dimuat di luar agar bisa dipinjam langsung oleh app.py
kamus_alay = pd.read_csv("new_kamusalay.csv", encoding='latin-1', header=None)
alay_dict = dict(zip(kamus_alay[0], kamus_alay[1]))

stopword_remover = StopWordRemoverFactory().create_stop_word_remover()
stemmer = StemmerFactory().create_stemmer()


# ── 🧼 FUNGSI PEMBERSIH SUPER (Mesin Utama) ──────────────────────────────────
def cuci_teks_super(teks_mentah):
    # Case Folding
    teks = str(teks_mentah).lower() 
    
    # Cleansing Dasar (Hapus RT, USER, URL)
    teks = re.sub(r'rt\s|user\s', '', teks) # Menghapus kata 'rt' dan 'user' bawaan dataset
    teks = re.sub(r'http\S+|www\S+|https\S+', '', teks, flags=re.MULTILINE)
    teks = re.sub(r'\@\w+|\#', '', teks)
    teks = re.sub(r'[^\w\s]', ' ', teks) # Hapus tanda baca
    teks = re.sub(r'\d+', '', teks) # Hapus angka
    teks = re.sub(r'\s+', ' ', teks).strip() # Rapikan spasi berlebih
    
    # Normalisasi Kata Alay
    kata_kata = teks.split()
    kata_normal = [alay_dict.get(kata, kata) for kata in kata_kata]
    teks = ' '.join(kata_normal)
    
    # Stopword Removal
    teks = stopword_remover.remove(teks)
    
    # Stemming
    teks_clean = stemmer.stem(teks)
    
    return teks_clean


# ==============================================================================
# 🎯 GERBANG ISOLASI EKSEKUSI MASSAL
# ==============================================================================
# Bagian di bawah ini HANYA akan aktif jika kamu menjalankan perintah 'python preprocessor.py'.
# Dashboard Streamlit (app.py) secara mutlak TIDAK AKAN PERNAH membaca atau mengeksekusi area ini.
if __name__ == "__main__":
    print("\n=======================================================")
    print("🚀 MEMULAI FASE 1: BULK PREPROCESSING DATASET TRAINING")
    print("=======================================================")
    
    # Memuat berkas training lama
    print("Memuat dataset utama (data.csv)...")
    df = pd.read_csv("data.csv", encoding='latin-1')

    # Menyederhanakan Label (Binary Classification: Cyberbullying vs Aman)
    df['Label'] = ((df['HS'] == 1) | (df['Abusive'] == 1)).astype(int)

    print("\nMencuci belasan ribu data training. Perhatikan progress bar di bawah:")
    tqdm.pandas(desc="Mencuci Teks")

    # Menerapkan fungsi ke seluruh baris
    df['Teks_Bersih'] = df['Tweet'].progress_apply(cuci_teks_super)

    # Memilih kolom yang penting saja untuk disimpan
    df_final = df[['Tweet', 'Teks_Bersih', 'Label']]

    # Menulis ulang file csv hasil training tanpa merusak berkas lain
    nama_file_final = "dataset_siap_training.csv"
    df_final.to_csv(nama_file_final, index=False)

    print(f"\n--- BULK PREPROCESSING SELESAI! ---")
    print(f"Data bersih eksperimen berhasil disimpan ke: '{nama_file_final}'")