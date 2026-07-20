# import pandas as pd
# import joblib
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import classification_report, confusion_matrix

# # 1. Memuat Data Bersih (Gunakan file yang sama persis dengan script training)
# print("Memuat dataset_siap_training.csv...")
# df = pd.read_csv("dataset_siap_training.csv")

# # PENTING: Wajib dropna agar urutan dan jumlah data sama persis saat split!
# df = df.dropna(subset=['Teks_Bersih'])

# # 2. Membagi Data (80% Latih, 20% Uji) dengan random_state=42
# X = df['Teks_Bersih']
# y = df['Label']

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # 3. Load Model SVM dan TF-IDF Vectorizer sesuai nama file asli kamu
# print("Memuat model dan vectorizer...")
# model_svm = joblib.load('model_svm.pkl') 
# tfidf = joblib.load('tfidf_vectorizer.pkl') # <-- Sudah disesuaikan dengan script trainingmu

# # 4. Transformasikan data uji (X_test) menggunakan TF-IDF
# X_test_vec = tfidf.transform(X_test)

# # 5. Lakukan Prediksi
# y_pred = model_svm.predict(X_test_vec)

# # 6. Cetak Hasil Akhir Valid untuk Lampiran Skripsi
# print("\n=== HASIL EVALUASI TERMINAL FOR SVM ===")
# print(classification_report(y_test, y_pred, digits=4)) # digits=4 supaya keluar 4 angka di belakang koma (standar skripsi)
# print("\n=== CONFUSION MATRIX ===")
# print(confusion_matrix(y_test, y_pred))

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# 1. Memuat Data Bersih
print("Memuat dataset_siap_training.csv...")
df = pd.read_csv("dataset_siap_training.csv")
df = df.dropna(subset=['Teks_Bersih'])

# 2. Membagi Data (80% Latih, 20% Uji) dengan random_state=42
X = df['Teks_Bersih']
y = df['Label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Load Model Naïve Bayes dan TF-IDF Vectorizer
print("Memuat model Naïve Bayes dan vectorizer...")
model_nb = joblib.load('model_nb.pkl') 
tfidf = joblib.load('tfidf_vectorizer.pkl')

# 4. Transformasikan data uji (X_test)
X_test_vec = tfidf.transform(X_test)

# 5. Lakukan Prediksi
y_pred_nb = model_nb.predict(X_test_vec)

# 6. Cetak Hasil Akhir Valid untuk Naïve Bayes
print("\n=== HASIL EVALUASI TERMINAL FOR MULTINOMIAL NAÏVE BAYES ===")
print(classification_report(y_test, y_pred_nb, digits=4))
print("\n=== CONFUSION MATRIX ===")
print(confusion_matrix(y_test, y_pred_nb))