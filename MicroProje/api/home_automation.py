"""
Home Automation System Connection - Base Class
EEM Projesi - Temel UART İletişim Sınıfı

Bu sınıf tüm home automation sistemleri için temel UART iletişim
fonksiyonlarını sağlar.
"""

import serial
import time


class HomeAutomationSystemConnection:
    """
    Home Automation Sistemleri için temel bağlantı sınıfı
    
    Bu sınıf seri port iletişimi için temel metodları sağlar:
    - Port açma/kapama
    - Byte gönderme/okuma
    - Bağlantı yönetimi
    """
    
    def __init__(self):
        """Constructor - Başlangıç değerleri"""
        self.comPort = None
        self.baudRate = 9600
        self.ser = None
    
    def setComPort(self, port):
        """
        COM port numarasını ayarla
        
        Args:
            port (str): COM port adı (örn: "COM14", "COM1")
        """
        self.comPort = port
        print(f"✓ COM Port ayarlandı: {port}")
    
    def setBaudRate(self, baudrate):
        """
        Baud rate'i ayarla
        
        Args:
            baudrate (int): Baud rate değeri (varsayılan: 9600)
        """
        self.baudRate = baudrate
        print(f"✓ Baud rate ayarlandı: {baudrate}")
    
    def open(self):
        """
        Seri portu aç ve bağlantı kur
        
        Returns:
            bool: Başarılı ise True, hata varsa False
        """
        if not self.comPort:
            print("✗ Hata: COM port ayarlanmamış!")
            return False
        
        try:
            self.ser = serial.Serial(
                port=self.comPort,
                baudrate=self.baudRate,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=1
            )
            time.sleep(2)  # PIC reset bekleme
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            print(f"✓ Port açıldı: {self.comPort} @ {self.baudRate} baud")
            return True
        except serial.SerialException as e:
            print(f"✗ Port açma hatası: {e}")
            return False
        except Exception as e:
            print(f"✗ Beklenmeyen hata: {e}")
            return False
    
    def close(self):
        """
        Seri portu kapat
        
        Returns:
            bool: Başarılı ise True
        """
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"✓ Port kapatıldı: {self.comPort}")
            return True
        return False
    
    def _send_byte(self, byte_val):
        """
        Tek byte gönder (internal method)
        
        Args:
            byte_val (int): Gönderilecek byte değeri (0-255)
        
        Returns:
            bool: Başarılı ise True
        """
        if not self.ser or not self.ser.is_open:
            print("✗ Hata: Port açık değil!")
            return False
        
        try:
            self.ser.write(bytes([byte_val]))
            time.sleep(0.05)  # PIC işleme zamanı
            return True
        except Exception as e:
            print(f"✗ Byte gönderme hatası: {e}")
            return False
    
    def _read_byte(self):
        """
        Tek byte oku (internal method)
        
        Returns:
            int or None: Okunan byte değeri veya None (timeout/error)
        """
        if not self.ser or not self.ser.is_open:
            print("✗ Hata: Port açık değil!")
            return None
        
        try:
            data = self.ser.read(1)
            if len(data) == 1:
                return data[0]
            else:
                return None  # Timeout
        except Exception as e:
            print(f"✗ Byte okuma hatası: {e}")
            return None
    
    def is_open(self):
        """
        Port açık mı kontrol et
        
        Returns:
            bool: Port açık ise True
        """
        return self.ser is not None and self.ser.is_open
