import subprocess

# Komut parçalarını bir liste halinde tanımlayın
burn_sender = [
    "python", "tremo_loader.py",
    "--port", '/dev/ttyUSB0',
    "--baud", "115200",
    "erase", "0x08000000","131072"
]

try:
    # Komutu başlat ve çıktıları anlık olarak oku
    process = subprocess.Popen(burn_sender, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Çıktıları satır satır oku
    print("Komut çıktıları:")
    for line in process.stdout:
        print(line.strip())  # Satırı yazdır (strip gereksiz boşlukları kaldırır)

    # Komut tamamlandıktan sonra hata çıktısını kontrol et
    stderr = process.stderr.read()
    if stderr:
        print("Hata mesajları:")
        print(stderr.strip())

    # İşlem kodunu kontrol et
    process.wait()
    if process.returncode == 0:
        print("Komut başarıyla tamamlandı.")
    else:
        print(f"Komut bir hata ile sonlandı. Çıkış kodu: {process.returncode}")

except Exception as e:
    print("Bir hata oluştu:")
    print(str(e))
