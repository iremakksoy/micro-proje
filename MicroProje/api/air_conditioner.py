"""
Board #1 - Klima Sistemi API
EEM Projesi - BM-2 Görevi
Yazan: [SENIN ADIN SOYADIN]
Tarih: 11 Aralık 2025

Bu modül Board #1 (PIC16F877A) ile iletişim kurarak
klima kontrolü ve sensör okuma işlemlerini yapar.

Özellikler:
- İstenen sıcaklık ayarlama (10-50°C)
- Ortam sıcaklığı okuma (DS18B20)
- Fan hızı okuma
"""

from .home_automation import HomeAutomationSystemConnection
import time


class AirConditionerSystemConnection(HomeAutomationSystemConnection):
    """
    Board #1 ile iletişim - Klima Sistemi
    
    UART Protokolü (R2.1.4-1):
    ┌─────────┬────────────────────────────────┬──────────────┐
    │ Komut   │ Açıklama                       │ Cevap        │
    ├─────────┼────────────────────────────────┼──────────────┤
    │ 0x01    │ İstenen sıcaklık (ondalık) AL  │ 1 byte (0-9) │
    │ 0x02    │ İstenen sıcaklık (tam) AL      │ 1 byte       │
    │ 0x03    │ Ortam sıcaklığı (ondalık) AL   │ 1 byte (0-9) │
    │ 0x04    │ Ortam sıcaklığı (tam) AL       │ 1 byte       │
    │ 0x05    │ Fan hızı AL                    │ 1 byte       │
    │ 0x80|val│ Sıcaklık (ondalık) AYARLA      │ -            │
    │ 0xC0|val│ Sıcaklık (tam) AYARLA          │ -            │
    └─────────┴────────────────────────────────┴──────────────┘
    
    Örnek Kullanım:
        >>> ac = AirConditionerSystemConnection()
        >>> ac.setComPort("COM1")
        >>> ac.open()
        >>> ac.update()  # Sensör verilerini oku
        >>> print(f"Ortam Sıcaklığı: {ac.getAmbientTemp()}°C")
        >>> ac.setDesiredTemp(24.5)  # 24.5°C ayarla
        >>> ac.close()
    """
    
    def __init__(self):
        """
        Constructor - Board #1 için başlangıç değerleri
        """
        super().__init__()
        self.ambientTemperature = 0.0    # Ortam sıcaklığı (°C)
        self.desiredTemperature = 0.0     # İstenen sıcaklık (°C)
        self.fanSpeed = 0                # Fan hızı (rps)
    
    def update(self):
        """
        Board #1'den tüm sensör verilerini oku
        
        Bu metod sırayla şu işlemleri yapar:
        1. Ortam sıcaklığını oku (DS18B20 sensörü)
        2. İstenen sıcaklığı oku
        3. Fan hızını oku
        
        Returns:
            bool: Tüm okumalar başarılı ise True
            
        Example:
            >>> ac.update()
            ✓ Veriler güncellendi
              Ortam Sıcaklığı: 22.5°C
              İstenen Sıcaklık: 24.0°C
              Fan Hızı: 3 rps
        """
        try:
            print("\n📥 Board #1'den veriler okunuyor...")
            
            # ─────────────────────────────────────────────────────
            # 1. ORTAM SICAKLIĞINI OKU (DS18B20 - AMBIENT_TEMP)
            # ─────────────────────────────────────────────────────
            self._send_byte(0x04)  # Komut: Ambient temp (integral)
            temp_h = self._read_byte()
            
            self._send_byte(0x03)  # Komut: Ambient temp (fractional)
            temp_l = self._read_byte()
            
            if temp_h is not None and temp_l is not None:
                self.ambientTemperature = float(temp_h) + float(temp_l) / 10.0
                print(f"  ✓ Ortam Sıcaklığı: {self.ambientTemperature:.1f}°C")
            else:
                print(f"  ✗ Ortam sıcaklığı okunamadı!")
            
            # ─────────────────────────────────────────────────────
            # 2. İSTENEN SICAKLIĞI OKU (DESIRED_TEMP)
            # ─────────────────────────────────────────────────────
            self._send_byte(0x02)  # Komut: Desired temp (integral)
            des_h = self._read_byte()
            
            self._send_byte(0x01)  # Komut: Desired temp (fractional)
            des_l = self._read_byte()
            
            if des_h is not None and des_l is not None:
                self.desiredTemperature = float(des_h) + float(des_l) / 10.0
                print(f"  ✓ İstenen Sıcaklık: {self.desiredTemperature:.1f}°C")
            else:
                print(f"  ✗ İstenen sıcaklık okunamadı!")
            
            # ─────────────────────────────────────────────────────
            # 3. FAN HIZINI OKU (FAN_SPEED)
            # ─────────────────────────────────────────────────────
            self._send_byte(0x05)  # Komut: Fan speed
            fan = self._read_byte()
            
            if fan is not None:
                self.fanSpeed = int(fan)
                print(f"  ✓ Fan Hızı: {self.fanSpeed} rps")
            else:
                print(f"  ✗ Fan hızı okunamadı!")
            
            print("✓ Veriler başarıyla güncellendi!\n")
            return True
            
        except Exception as e:
            print(f"✗ Update sırasında hata: {e}")
            return False
    
    def setDesiredTemp(self, temperature):
        """
        İstenen sıcaklığı ayarla
        
        Args:
            temperature (float): İstenen sıcaklık (°C)
                - 10.0°C ile 50.0°C arası geçerli
        
        Returns:
            bool: Başarılı ise True, geçersiz değer veya hata varsa False
            
        Raises:
            Exception: İletişim hatası durumunda
            
        Note:
            - 10-50°C arası geçerli
            - Protokol: 0xC0|tam_kısım + 0x80|ondalık_kısım
            
        Example:
            >>> ac.setDesiredTemp(24.5)
            ✓ Sıcaklık ayarlandı: 24.5°C
            True
            
            >>> ac.setDesiredTemp(5.0)
            ✗ Hata: Sıcaklık 10-50°C arası olmalı!
            False
        """
        # ─────────────────────────────────────────────────────
        # GEÇERLİLİK KONTROLÜ
        # ─────────────────────────────────────────────────────
        if temperature < 10.0 or temperature > 50.0:
            print(f"✗ Hata: Sıcaklık 10-50°C arası olmalı! (Girilen: {temperature:.1f}°C)")
            print(f"  → Geçerli aralık: 10.0°C - 50.0°C")
            return False
        
        try:
            # ─────────────────────────────────────────────────────
            # SICAKLIK DEĞERINI TAM VE ONDALIK OLARAK AYIR
            # ─────────────────────────────────────────────────────
            # Örnek: 24.5°C → tam=24, ondalık=5
            temp_h = int(temperature)                      # Tam kısım
            temp_l = int((temperature - temp_h) * 10)     # Ondalık kısım
            
            print(f"📤 Sıcaklık ayarlanıyor: {temperature:.1f}°C")
            print(f"   → Tam kısım: {temp_h}")
            print(f"   → Ondalık kısım: {temp_l}")
            
            # ─────────────────────────────────────────────────────
            # PDF'DEKİ PROTOKOLE GÖRE KOMUT GÖNDER
            # ─────────────────────────────────────────────────────
            # Format: 11XXXXXX (tam), 10XXXXXX (ondalık)
            
            # 1. Tam kısımı gönder (0xC0 = 11000000 binary)
            cmd_h = 0xC0 | (temp_h & 0x3F)  # 0x3F = 00111111 (6-bit mask)
            self._send_byte(cmd_h)
            print(f"   → Komut gönderildi: 0x{cmd_h:02X} (tam kısım)")
            
            # 2. Ondalık kısımı gönder (0x80 = 10000000 binary)
            cmd_l = 0x80 | (temp_l & 0x3F)
            self._send_byte(cmd_l)
            print(f"   → Komut gönderildi: 0x{cmd_l:02X} (ondalık kısım)")
            
            # PIC'in işlemesi için bekle
            time.sleep(0.2)
            
            print(f"✓ Sıcaklık başarıyla ayarlandı: {temperature:.1f}°C\n")
            return True
            
        except Exception as e:
            print(f"✗ Sıcaklık ayarlama hatası: {e}")
            return False
    
    # ═════════════════════════════════════════════════════════
    # GETTER METODLARI
    # ═════════════════════════════════════════════════════════
    
    def getAmbientTemp(self):
        """
        Son okunan ortam sıcaklığını döndür
        
        Returns:
            float: Ortam sıcaklığı (°C)
            
        Note:
            DS18B20 sensörü: -55°C ile 125°C arası
            Güncel değer için önce update() çağırın
        """
        return self.ambientTemperature
    
    def getDesiredTemp(self):
        """
        Son okunan istenen sıcaklığı döndür
        
        Returns:
            float: İstenen sıcaklık (°C)
            
        Note:
            Güncel değer için önce update() çağırın
        """
        return self.desiredTemperature
    
    def getFanSpeed(self):
        """
        Son okunan fan hızını döndür
        
        Returns:
            int: Fan hızı (rps - revolutions per second)
            
        Note:
            Güncel değer için önce update() çağırın
        """
        return self.fanSpeed
    
    # ═════════════════════════════════════════════════════════
    # DEBUG METODLARI
    # ═════════════════════════════════════════════════════════
    
    def print_status(self):
        """
        Tüm sensör değerlerini ekrana yazdır (debug için)
        """
        print("\n" + "="*50)
        print("  BOARD #1 - KLİMA SİSTEMİ DURUMU")
        print("="*50)
        print(f"  Ortam Sıcaklığı     : {self.ambientTemperature:.1f}°C")
        print(f"  İstenen Sıcaklık    : {self.desiredTemperature:.1f}°C")
        print(f"  Fan Hızı            : {self.fanSpeed} rps")
        print("="*50 + "\n")
