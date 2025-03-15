"""
Python ID Gönderici
Remzi ALPASLAN
19.02.2025
Otomatik reset eklenmiştir.
Otomatik serial gönderim bekleme eklenmiştir.

"""



import serial
import time


loraSettings =[ 
    "AT+CJOINMODE=0",
    #"AT+CDEVEUI=26824265", # Pedometer
    #"AT+CDEVEUI=26824867", # TempSensor
    #"AT+CDEVEUI=26824625", # NeckPedometer
    "AT+CDEVEUI=2682426525020405", # TempHumSens
    "AT+CAPPEUI=0000000000000000",
    "AT+CAPPKEY=FA280893DA268242652CB023AE111098",
    "AT+CFREQBANDMASK=0001",
    "AT+CULDLMODE=2",
    "AT+CCLASS=0",
    "AT+CTXP=0",
    "AT+CRXP= 1,1,869525000",
    "AT+CJOIN=1,1,15,1",
    "AT+CKEYSPROTECT=AFAFAF42FA0CBDA111098F75190D2023",
    "AT+DTRX=1,1,10,0001020304"]

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

ser.setRTS(False)

def LoraSetup():
    # Seri portu kontrol et
    if ser.is_open:
        print(f"{ser.port} bağlantısı başarılı!")   
    
    ser.reset_input_buffer()  # Giriş buffer'ını temizle
    ser.reset_output_buffer()  # Çıkış buffer'ını temizle
    
    print("/Firs data control")        
    while True:
        temp = ""
        if ser.in_waiting:
            temp = ser.readline().decode('utf-8', errors="ignore").strip()
        if temp:
            print(temp)
        
        if temp.find("601:~#") >= 0 or temp.find("+CJOIN:") >= 0:
            break
        
    ser.reset_input_buffer()  # Giriş buffer'ını temizle
    ser.reset_output_buffer()  # Çıkış buffer'ını temizle
    
    index = 0
    command = ""
    print("/Send ten data")        
    while True:
        response = ""
        command = (loraSettings[index]+"\r\n").encode()
        ser.write(command) 
        ser.flush()
        # time.sleep(0.1)
        
        strart_time = time.time()
        while ser.in_waiting == 0:
            # print("bekleniyor")
            time.sleep(0.01)
            if time.time() - strart_time > 0.3:
                break
        second= round(time.time() - strart_time, 2)
                

        while ser.in_waiting:
            response += ser.readline().decode('utf-8', errors="ignore").strip()+" "
            
        print(f"Sent: {command}, Received: {response}, Time: {second}")
        
        if response.find("OK")>=0:
            index+=1
            if index == 10:
                break  
                  
    print("/Join Control")        
    # Join Control
    while True:
        if JoinControl() == True:
            break
        time.sleep(0.1)
        
    ser.reset_input_buffer()  # Giriş buffer'ını temizle
    ser.reset_output_buffer()  # Çıkış buffer'ını temizle
        
    print("/Key protect and Reset")
    # Key protect and Reset 
    response = ""
    command = (loraSettings[index]+"\r\n").encode()
    ser.write(command) 
    ser.flush()
    time.sleep(0.1)
    
    strart_time = time.time()
    while ser.in_waiting == 0:
        print("bekleniyor")
        time.sleep(0.01)
        if time.time() - strart_time > 0.2:
            break
    second= round(time.time() - strart_time, 2)
    
    while ser.in_waiting:
        response += ser.readline().decode('utf-8', errors="ignore").strip()+" "
        
    print(f"Sent: {command}, Received: {response}, Time: {second}")

    if response.find("OK")>0:
        index+=1
    
    ser.setRTS(True)    
    time.sleep(0.5)
    ser.setRTS(False)   
    
    print("/Join Control 2")
    # Join Control
    while True:
        if JoinControl() == True:
            break
        time.sleep(0.3)
    
    ser.reset_input_buffer()  # Giriş buffer'ını temizle
    ser.reset_output_buffer()  # Çıkış buffer'ını temizle
        
    print("/Test Msg Send")
    # Test Msg Send
    time.sleep(0.5)
    command = (loraSettings[index]+"\r\n").encode()
    ser.write(command) 
    ser.flush()
    time.sleep(0.1)
    
    strart_time = time.time()
    while ser.in_waiting == 0:
        print("bekleniyor")
        time.sleep(0.01)
        if time.time() - strart_time > 0.2:
            break
    second= round(time.time() - strart_time, 2)
    
    while True:
        response = ""
        while ser.in_waiting:
            response += ser.readline().decode('utf-8', errors="ignore").strip()+" "
            
        if response:
            print(f"Sent: {command}, Received: {response}, Time: {second}")
        
        if response.find("OK+RECV:") > 0:
            index+=1
            break
        elif response.find("ERR+SENT") > 0 or response.find("+CJOIN:") > 0:
            time.sleep(3)
            command = (loraSettings[index]+"\r\n").encode()
            ser.write(command) 
            ser.flush()
            time.sleep(0.1)
            
            strart_time = time.time()
            while ser.in_waiting == 0:
                print("bekleniyor")
                time.sleep(0.01)
                if time.time() - strart_time > 0.2:
                    break
            second= round(time.time() - strart_time, 2)
            
    print("Kurulum Basariyla Tamamlandi.")
    
    
def JoinControl():
    temp = ""

    while ser.in_waiting:
        temp = ser.readline().decode('utf-8', errors="ignore").strip()
        print(temp)
        if temp.find("CJOIN:OK")>=0: 
            return True
        time.sleep(0.02) 
    return False
         
LoraSetup()



