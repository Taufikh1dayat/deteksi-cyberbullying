import pandas as pd
import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from tqdm import tqdm

print("--- MEMULAI FASE 1: BULK PREPROCESSING ---")

# 1. Memuat Data Utama
print("Memuat dataset utama...")
df = pd.read_csv("data.csv", encoding='latin-1')

# 2. Menyederhanakan Label (Binary Classification: Cyberbullying vs Aman)
# Jika HS == 1 ATAU Abusive == 1, maka Label = 1. Jika tidak, 0.
df['Label'] = ((df['HS'] == 1) | (df['Abusive'] == 1)).astype(int)

# 3. Memuat Kamus Alay (Slang Dictionary)
print("Memuat Kamus Bahasa Gaul (Alay)...")
kamus_alay = pd.read_csv("new_kamusalay.csv", encoding='latin-1', header=None)
# Mengubah tabel kamus menjadi format dictionary Python { 'kata_alay': 'kata_baku' }
alay_dict = dict(zip(kamus_alay[0], kamus_alay[1]))

# 4. Inisialisasi Sastrawi
print("Menyiapkan mesin NLP Sastrawi (Tunggu sebentar)...")
stopword_remover = StopWordRemoverFactory().create_stop_word_remover()
stemmer = StemmerFactory().create_stemmer()

# 5. Fungsi Pembersih Super (Termasuk Normalisasi Bahasa Gaul)
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
    teks_bersih = stemmer.stem(teks)
    
    return teks_bersih

# ==========================================
# 6. EKSEKUSI MASSAL
# ==========================================
# Pastikan gerbang ini berada di paling kiri (tanpa spasi awal)
if __name__ == "__main__":
    print("\nMemulai pencucian belasan ribu data. Proses ini bisa memakan waktu 30 menit - 2 Jam.")
    print("Perhatikan Progress Bar di bawah ini:")

    # SEMUA baris di bawah ini WAJIB menjorok 1 TAB / 4 SPASI ke kanan
    tqdm.pandas(desc="Mencuci Teks")

    # Menerapkan fungsi ke seluruh baris
    df['Teks_Bersih'] = df['Tweet'].progress_apply(cuci_teks_super)

    # Memilih kolom yang penting saja untuk disimpan
    df_final = df[['Tweet', 'Teks_Bersih', 'Label']]

    # ==========================================
    # 7. MENYIMPAN HASIL FINAL (Sekarang aman di dalam gerbang)
    # ==========================================
    nama_file_final = "dataset_siap_training.csv"
    df_final.to_csv(nama_file_final, index=False)

    print(f"\n--- PREPROCESSING SELESAI! ---")
    print(f"Data bersih berhasil diamankan ke file: '{nama_file_final}'")

