import serial
import time
import subprocess

first_time=time.time()
atım_sayısı=0

# Arduino'ya bağlanmak için seri bağlantı ayarları
arduino_port = "COM7"  # Arduino'nun bağlı olduğu port (Windows: COMx, Mac/Linux: /dev/ttyUSBx)
baud_rate = 9600  # Arduino'nun baud rate ayarı
timeout = 2  # Zaman aşımı süresi (saniye)


# Example usage
num_latitude = 5  # Number of regions in latitude
num_longitude = 4  # Number of regions in longitude
lat_mm = 44.200  # Width of each region in mm
lon_mm = 42.800  # Height of each region in mm
start_lat_mm =46.700
start_lon_mm =141.500

sucses_burn_matris=[[0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0]]


# Komut parçalarını bir liste halinde tanımlayın
burn_sender = [
    "python", "tremo_loader.py",
    "--port", "COM13",
    "--baud", "1500000",
    "flash", "0x08000000",
    "Ra-08H_EU868_V1.4.0.bin"
]

        

def check_zero_positions(matrix):
    """
    Verilen matris içinde 0 olan elemanların konumlarını bulur ve yazdırır.
    Bu kez, önce sütunlara (column) bakarak çalışır.
    
    Args:
        matrix (list): İki boyutlu bir liste (matris).
    
    Returns:
        list: 0 olan elemanların (satır, sütun) konumlarının listesi.
    """
    zero_positions = []

    # Sütunları dış döngüde, satırları iç döngüde kontrol et
    for j in range(len(matrix[0])):  # Sütun sayısı kadar döner
        if j%2==0:
            for i in range(len(matrix)):  # Satır sayısı kadar döner
                if matrix[i][j] == 0:
                    zero_positions.append([i, j])
        else:
            for i in range(len(matrix)-1,-1,-1):  # Satır sayısı kadar döner
                if matrix[i][j] == 0:
                    zero_positions.append([i, j])
            
                

    return zero_positions



def generate_gcode_with_matrix(num_latitude, num_longitude, lat_mm, lon_mm, start_lat_mm, start_lon_mm, zero_matris):
    gcode = []
    # Start G-code setup (optional, you can adjust these based on your machine)
    gcode.append("$X")
    # Raise Z-axis (deactivate tool)
    gcode.append("M3 S20 ; Raise Z-axis")
    gcode.append("G4 P0.1")
    gcode.append("$H")
    gcode.append("G21 ; Set units to mm")
    gcode.append("G90 ; Absolute positioning")
    gcode.append("G10 P0 L20 X0 Y0 Z0 ; Reset to all axis")

    for konum in zero_matris:
        j= konum[0]
        i= konum[1]
        # Calculate the position for this region
        x =round(start_lat_mm + i * lat_mm,3)
        y =round(start_lon_mm - j * lon_mm,3) 

        gcode.append("M3 S20 ; Raise Z-axis")
        gcode.append("G4 P0.1")
        
        # Move to the region's position
        gcode.append(f"G0X{x:.2f}Y{y:.2f}; Move to position")
        gcode.append("?;"+str(x)+str(";")+str(y))
        
        gcode.append("M3 S1 ;"+str(j)+str(";")+str(i))
        gcode.append("G4 P0.1")

    # End G-code
    # Raise Z-axis (deactivate tool)
    #gcode.append("G4 P0.1")
    gcode.append("M3 S20 ; Raise Z-axis")
    gcode.append("G4 P0.1")
    gcode.append("G0X5Y5; Move to position")
    gcode.append("?;"+str(5)+str(";")+str(5))
    
    return gcode

matrix=check_zero_positions(sucses_burn_matris)

# Arduino'ya bağlan
print(f"Bağlanıyor: {arduino_port} ({baud_rate} baud)")
ser = serial.Serial(arduino_port, baud_rate, timeout=timeout)
time.sleep(2)  # Arduino'nun hazır olması için bekle
print("Bağlantı başarılı!\n")

while matrix:
    list_konum=0
    ard_arda_başarısız_atım=0
    tekrar_dene=[[1,1,1,1,1],
                 [1,1,1,1,1],
                 [1,1,1,1,1],
                 [1,1,1,1,1]]
    # Generate the G-code
    gcode_output = generate_gcode_with_matrix(num_latitude, num_longitude, lat_mm, lon_mm, start_lat_mm, start_lon_mm, matrix)
    for output in gcode_output:
        print(output)
        
    try:
        if  not ser.is_open:
            # Arduino'ya bağlan
            print(f"Bağlanıyor: {arduino_port} ({baud_rate} baud)")
            ser = serial.Serial(arduino_port, baud_rate, timeout=timeout)
            time.sleep(2)  # Arduino'nun hazır olması için bekle
            print("Bağlantı başarılı!\n")

        # G-code komutlarını sırayla gönder
        while  list_konum <= len(gcode_output)-1:
            command=gcode_output[list_konum]
            command = command.strip()  # Gereksiz boşlukları kaldır
            if not command:
                continue

            print(f"Gönderiliyor: {command}")
            ser.write((command + "\n").encode())  # Komutu gönder
            
            time.sleep(0.1)  # Arduino'nun komutu işlemesi için kısa bir bekleme

            start_time=time.time()
            response_breaker=False
            while True:
                response = ser.readline().decode("utf-8", errors="ignore").strip()  # Yanıtı oku
                if response:  # Boş olmayan bir yanıt varsa yazdır   
                    print(f"Yanıt: {response}")
                    pass
                
                if command.startswith("$H"):
                    if response.lower() == "ok":  # Yanıt "ok" ise döngüden çık
                        break
                    else:
                        if time.time()-start_time>=20:
                            list_konum-=1
                            break
                elif command.startswith("?"):
                    if response.startswith("<"):  # Yanıt "ok" ise döngüden çık
                        print("################################################")
                        print(round(float(command.split(";")[1]),3),round(float(command.split(";")[2]),3))
                        print(round(float(response.split(":")[1].split(",")[0]),3),round(float(response.split(":")[1].split(",")[1]),3))
                        print("################################################")
                        commandLocationx=round(float(command.split(";")[1]),3)
                        commandLocationy=round(float(command.split(";")[2]),3)
                        responseLocationx=round(float(response.split(":")[1].split(",")[0]),3)
                        responseLocationy=round(float(response.split(":")[1].split(",")[1]),3)
                        response_breaker=True
                        if commandLocationx != responseLocationx or commandLocationy != responseLocationy:
                            list_konum-=1
                            break
                    if response.lower() == "ok" and response_breaker:  # Yanıt "ok" ise döngüden çık
                        break
                    else:
                        if time.time()-start_time>=4:
                            list_konum-=1
                            break
                else:
                    if response.lower() == "ok":  # Yanıt "ok" ise döngüden çık
                        break
                    else:
                        if time.time()-start_time>=2:
                            list_konum-=1
                            break

                if response.startswith("eror") or response.startswith("ALARM") or response.startswith("[MSG:Reset to continue]"):
                    print(f"Gönderiliyor: $X")
                    ser.write(("$X" + "\n").encode())  # Komutu gönder
                    if response.lower() == "ok":  # Yanıt "ok" ise döngüden çık
                        break
                       
                time.sleep(0.05)
                
                
            if command.startswith("M3 S1"):
                atım_sayısı+=1
                print("###################################################")
                print("Komut çıktıları:")
                konum=command.split(";")
                print(konum)
                try:
                    # Komutu başlat ve çıktıları anlık olarak oku
                    process = subprocess.Popen(burn_sender, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                    # Çıktıları satır satır oku
                    for line in process.stdout:
                        if not line.startswith("send"):
                            print(line.strip())  # Satırı yazdır (strip gereksiz boşlukları kaldırır)
                            if line.startswith("Download files successfully"):
                                sucses_burn_matris[int(konum[1])][int(konum[2])]=1
                    
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
                            
                if  sucses_burn_matris[int(konum[1])][int(konum[2])]==1:          
                    ard_arda_başarısız_atım=0
                else:
                    ard_arda_başarısız_atım += 1
                    if tekrar_dene[int(konum[1])][int(konum[2])]==1:
                        list_konum-=5
                        tekrar_dene[int(konum[1])][int(konum[2])]=0
                
                if ard_arda_başarısız_atım >=4:
                    print("başarısız atımlar")
                    list_konum = len(gcode_output)-5
                
                for i in sucses_burn_matris:
                    print(i)    

                    
            list_konum+=1
                

        print("Tüm komutlar başarıyla gönderildi!")

    except serial.SerialException as e:
        print(f"Seri bağlantı hatası: {e}") 
            
    matrix=check_zero_positions(sucses_burn_matris)


if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Bağlantı kapatıldı.")
    
print("################################################")
print("Tüm İşlemler Bitti")
print("################################################")    
    
    
last_time=time.time()
print(str(atım_sayısı)+" de attı "+str(int(last_time-first_time))+" sn")




