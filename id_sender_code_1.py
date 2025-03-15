import RPi.GPIO as GPIO
import serial
import time


loraSettings =[ 
    "AT+CJOINMODE=0",
    #"AT+CDEVEUI=26824265", # Pedometer
    #"AT+CDEVEUI=26824867", # TempSensor
    #"AT+CDEVEUI=26824625", # NeckPedometer
    "AT+CDEVEUI=26824486000", # TempHumSens
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
# GPIO ayarları
resetPin = 18
GPIO.setmode(GPIO.BCM)  # BCM pin numaralandırma sistemi kullanılır
GPIO.setup(resetPin, GPIO.OUT)  # GPIO 23 output (çıkış) olarak ayarlanır
GPIO.output(resetPin, GPIO.LOW) 

def LoraSetup():
    # Seri portu kontrol et
    if ser.is_open:
        print(f"{ser.port} bağlantısı başarılı!")
        
    time.sleep(0.5)
    print("/Firs data control")        
    while True:
        temp = ""
        if ser.in_waiting:
            temp = ser.readline().decode('utf-8', errors="ignore").strip()
        if temp:
            print(temp)
        
        if temp.find("601:~#") >= 0 or temp.find("+CJOIN:") >= 0:
            break
        
    while ser.in_waiting:
        ser.readline().decode('utf-8', errors="ignore").strip()    
        
        
    
    index = 0
    answer = ""
    print("/Send ten data")        
    while True:
        ser.write((loraSettings[index]+"\n").encode('utf-8')) 
        ser.flush()
        answer = ser.readline().decode('utf-8', errors="ignore").strip()
        print("---")
        print((loraSettings[index]+"\n").encode('utf-8'))
        print(answer)
        
        if answer.find("OK")>=0:
            index+=1
            if index == 10:
                break
        time.sleep(0.3)            
    print("/Join Control")        
    # Join Control
    while True:
        if JoinControl() == True:
            break
        time.sleep(0.1)
    print("/Key protect and Reset")
    # Key protect and Reset 
    msg=(loraSettings[index]+"\n").encode('utf-8')
    print(msg)
    ser.write(msg)  
    ser.flush()

    answer = ser.readline().decode('utf-8', errors="ignore").strip()
    print("---")
    print(answer)

    if answer.find("OK")>0:
        index+=1
     
    GPIO.output(resetPin, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(resetPin, GPIO.LOW)   
    
    print("/Join Control 2")
    # Join Control
    while True:
        if JoinControl() == True:
            break
        time.sleep(0.3)
        
    print("/Test Msg Send")
    # Test Msg Send
    time.sleep(0.5)
    msg = (loraSettings[index]+"\n").encode('utf-8')
    print(msg)
    ser.write(msg)  
    ser.flush()

    while True:
        answer = ser.readline().decode('utf-8', errors="ignore").strip()
        print("---")
        print(answer)
        
        if answer.find("OK+RECV:") > 0:
            index+=1
            break
        elif answer.find("ERR+SENT") > 0 or answer.find("+CJOIN:") > 0:
            time.sleep(3)
            msg = (loraSettings[index]+"\n").encode('utf-8')
            print(msg)
            ser.write(msg)  
            ser.flush()
            
    print("Kurulum Basariyla Tamamlandi.")
    
    
def JoinControl():
    temp = ""
    joinState = False

    while ser.in_waiting:
        temp = ser.readline().decode('utf-8', errors="ignore").strip()
        print(temp)
        if temp.find("CJOIN:")>=0: #"CJOIN:OK" normalde bu yazıyor ama ben değiştirdim
            joinState = True
        time.sleep(0.02)
        return joinState
         
LoraSetup()



