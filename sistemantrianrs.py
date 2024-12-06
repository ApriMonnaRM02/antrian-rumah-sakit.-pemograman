from datetime import datetime, timedelta
from enum import Enum, auto
import heapq

class StatusPasien(Enum):
    MENUNGGU = auto()
    DARURAT = auto()
    SEDANG_DITANGANI = auto()
    SELESAI = auto()
    DIBATALKAN = auto()

class Dokter:
    def __init__(self, nama, spesialisasi):
        self.nama = nama
        self.spesialisasi = spesialisasi
        self.pasien_dilayani = []
        self.status = "Tersedia"

class RekamMedis:
    def __init__(self, pasien):
        self.pasien = pasien
        self.riwayat_status = []
        self.dokter_yang_menangani = None
        self.catatan_tambahan = []
    
    def tambah_status(self, status, keterangan=""):
        rekaman = {
            'waktu': datetime.now(),
            'status': status,
            'keterangan': keterangan
        }
        self.riwayat_status.append(rekaman)

class Pasien:
    def __init__(self, nama, umur, kondisi, jenis_poli):
        self.nama = nama
        self.umur = umur
        self.jenis_poli = jenis_poli
        self.kondisi = kondisi
        self.status = StatusPasien.MENUNGGU
        self.waktu_kedatangan = datetime.now()
        self.prioritas = self._tentukan_prioritas()
        self.estimasi_tunggu = None
        self.rekam_medis = RekamMedis(self)
        self.nomor_antrian = None
    
    def _tentukan_prioritas(self):
        prioritas_map = {
            'darurat': 1,
            'kritis': 2,
            'parah': 3,
            'sedang': 4,
            'ringan': 5
        }
        return prioritas_map.get(self.kondisi.lower(), 6)
    
    def __lt__(self, other):
        return self.prioritas < other.prioritas

class ManajemenAntrian:
    def __init__(self):
        self.antrian = []
        self.daftar_dokter = {}
        self.waktu_pelayanan = {
            'umum': timedelta(minutes=15),
            'anak': timedelta(minutes=20),
            'penyakit-dalam': timedelta(minutes=25),
            'bedah': timedelta(minutes=30)
        }
        self.nomor_antrian_terakhir = 0
    
    def tambah_dokter(self, nama, spesialisasi):
        dokter = Dokter(nama, spesialisasi)
        if spesialisasi not in self.daftar_dokter:
            self.daftar_dokter[spesialisasi] = []
        self.daftar_dokter[spesialisasi].append(dokter)
        print(f"Dokter {nama} ({spesialisasi}) ditambahkan.")
    
    def tambah_pasien(self, pasien):
        self.nomor_antrian_terakhir += 1
        pasien.nomor_antrian = self.nomor_antrian_terakhir
        
        heapq.heappush(self.antrian, pasien)
        pasien.rekam_medis.tambah_status(StatusPasien.MENUNGGU, "Pasien baru masuk antrian")
        self._hitung_estimasi_tunggu(pasien)
        print(f"Pasien {pasien.nama} ditambahkan ke antrian {pasien.jenis_poli}. Nomor Antrian: {pasien.nomor_antrian}")
    
    def _hitung_estimasi_tunggu(self, pasien):
        dokter_tersedia = len(self.daftar_dokter.get(pasien.jenis_poli, []))
        waktu_pelayanan = self.waktu_pelayanan.get(pasien.jenis_poli, timedelta(minutes=15))
        
        jumlah_antrian = len([p for p in self.antrian if p.jenis_poli == pasien.jenis_poli])
        estimasi = waktu_pelayanan * (jumlah_antrian // max(dokter_tersedia, 1) + 1)
        
        pasien.estimasi_tunggu = estimasi
        pasien.rekam_medis.tambah_status(StatusPasien.MENUNGGU, f"Estimasi tunggu: {estimasi}")
    
    def panggil_pasien_berikutnya(self):
        if not self.antrian:
            print("Tidak ada pasien dalam antrian.")
            return None
        
        pasien = heapq.heappop(self.antrian)
        
        dokter_cocok = self._pilih_dokter(pasien.jenis_poli)
        
        if dokter_cocok:
            pasien.status = StatusPasien.SEDANG_DITANGANI
            pasien.rekam_medis.dokter_yang_menangani = dokter_cocok
            pasien.rekam_medis.tambah_status(
                StatusPasien.SEDANG_DITANGANI, 
                f"Ditangani oleh Dr. {dokter_cocok.nama}"
            )
            dokter_cocok.pasien_dilayani.append(pasien)
            dokter_cocok.status = "Sedang Bertugas"
            
            print(f"\n--- PEMANGGILAN PASIEN ---")
            print(f"Nomor Antrian: {pasien.nomor_antrian}")
            print(f"Nama: {pasien.nama}")
            print(f"Poli: {pasien.jenis_poli}")
            print(f"Kondisi: {pasien.kondisi}")
            print(f"Dokter: {dokter_cocok.nama}")
            print(f"Estimasi Tunggu: {pasien.estimasi_tunggu}")
        
        return pasien
    
    def _pilih_dokter(self, spesialisasi):
        dokter_spesialis = self.daftar_dokter.get(spesialisasi, [])
        dokter_tersedia = [d for d in dokter_spesialis if d.status == "Tersedia"]
        
        return dokter_tersedia[0] if dokter_tersedia else None
    
    def selesaikan_pasien(self, pasien, catatan_tambahan=""):
        pasien.status = StatusPasien.SELESAI
        pasien.rekam_medis.tambah_status(
            StatusPasien.SELESAI, 
            f"Perawatan selesai. {catatan_tambahan}"
        )
        
        if pasien.rekam_medis.dokter_yang_menangani:
            dokter = pasien.rekam_medis.dokter_yang_menangani
            dokter.status = "Tersedia"
        
        print(f"Pasien {pasien.nama} selesai ditangani.")
    
    def tampilkan_antrian(self):
        print("\n--- DAFTAR ANTRIAN PASIEN ---")
        if not self.antrian:
            print("Tidak ada pasien dalam antrian.")
            return
        
        # Buat salinan antrian untuk ditampilkan tanpa merusak antrian asli
        antrian_sementara = sorted(self.antrian)
        
        print("No | Nama | Poli | Kondisi | Estimasi Tunggu")
        print("-" * 55)
        
        for pasien in antrian_sementara:
            print(f"{pasien.nomor_antrian:2d} | {pasien.nama:10s} | {pasien.jenis_poli:5s} | {pasien.kondisi:7s} | {pasien.estimasi_tunggu}")
    
    def tampilkan_dokter(self):
        print("\n--- DAFTAR DOKTER ---")
        for spesialisasi, dokter_list in self.daftar_dokter.items():
            print(f"\nSpesialisasi {spesialisasi.capitalize()}:")
            for dokter in dokter_list:
                print(f"Nama: {dokter.nama}")
                print(f"Status: {dokter.status}")
                print("---")

def main():
    antrian = ManajemenAntrian()
    
    # Tambah beberapa dokter
    antrian.tambah_dokter("Dr. Seivy", "umum")
    antrian.tambah_dokter("Dr. Ariel", "umum")
    antrian.tambah_dokter("Dr. Key", "anak")
    antrian.tambah_dokter("Dr. Apri", "penyakit-dalam")
    
    while True:
        print("\n--- SISTEM ANTRIAN RUMAH SAKIT ---")
        print("1. Tambah Pasien")
        print("2. Panggil Pasien Berikutnya")
        print("3. Tampilkan Antrian")
        print("4. Tampilkan Dokter")
        print("5. Selesaikan Pasien")
        print("6. Keluar")
        
        pilihan = input("Masukkan pilihan (1-6): ")
        
        if pilihan == '1':
            nama = input("Masukkan nama pasien: ")
            umur = int(input("Masukkan umur pasien: "))
            
            print("Pilih kondisi:")
            kondisi_map = {
                '1': 'darurat', '2': 'kritis', '3': 'parah', 
                '4': 'sedang', '5': 'ringan'
            }
            for key, value in kondisi_map.items():
                print(f"{key}. {value.capitalize()}")
            kondisi_pilih = input("Masukkan nomor kondisi: ")
            kondisi = kondisi_map.get(kondisi_pilih, 'ringan')
            
            print("Pilih Poli:")
            poli_map = {
                '1': 'umum', '2': 'anak', 
                '3': 'penyakit-dalam', '4': 'bedah'
            }
            for key, value in poli_map.items():
                print(f"{key}. {value.capitalize()}")
            poli_pilih = input("Masukkan nomor poli: ")
            jenis_poli = poli_map.get(poli_pilih, 'umum')
            
            pasien_baru = Pasien(nama, umur, kondisi, jenis_poli)
            antrian.tambah_pasien(pasien_baru)
        
        elif pilihan == '2':
            pasien = antrian.panggil_pasien_berikutnya()
        
        elif pilihan == '3':
            antrian.tampilkan_antrian()
        
        elif pilihan == '4':
            antrian.tampilkan_dokter()
        
        elif pilihan == '5':
            if len(antrian.antrian) > 0:
                pasien_terakhir = antrian.antrian[0]
                catatan = input("Masukkan catatan tambahan (opsional): ")
                antrian.selesaikan_pasien(pasien_terakhir, catatan)
            else:
                print("Tidak ada pasien untuk diselesaikan.")
        
        elif pilihan == '6':
            print("Terima kasih. Keluar dari sistem.")
            break
        
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

if __name__ == "__main__":
    main()