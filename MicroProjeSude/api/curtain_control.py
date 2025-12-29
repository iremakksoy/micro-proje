"""
Board #2 - Perde Kontrol Sistemi API
EEM Projesi - BM-2 Görevi
Yazan: [SENIN ADIN SOYADIN]
Tarih: 11 Aralık 2025

Bu modül Board #2 (PIC16F877A) ile iletişim kurarak
perde kontrolü ve sensör okuma işlemlerini yapar.

Özellikler:
- Perde durumu ayarlama (0-100%)
- Dış sıcaklık okuma (BMP180)
- Dış basınç okuma (BMP180)
- Işık şiddeti okuma (LDR)
"""

from .home_automation import HomeAutomationSystemConnection
import time

class CurtainControlSystemConnection(HomeAutomationSystemConnection):
    """
    Board #2 ile iletişim - Perde Kontrol Sistemi
    
    UART Protokolü (R2.2.6-1 - PDF sayfa 18-19):
    ┌─────────┬────────────────────────────────┬──────────────┐
    │ Komut   │ Açıklama                       │ Cevap        │
    ├─────────┼────────────────────────────────┼──────────────┤
    │ 0x01    │ Perde durumu (ondalık) AL      │ 1 byte (0-9) │
    │ 0x02    │ Perde durumu (tam) AL          │ 1 byte       │
    │ 0x03    │ Dış sıcaklık (ondalık) AL      │ 1 byte (0-9) │
    │ 0x04    │ Dış sıcaklık (tam) AL          │ 1 byte       │
    │ 0x05    │ Dış basınç (ondalık) AL        │ 1 byte       │
    │ 0x06    │ Dış basınç (tam) AL            │ 1 byte       │
    │ 0x07    │ Işık (ondalık) AL              │ 1 byte       │
    │ 0x08    │ Işık (tam) AL                  │ 1 byte       │
    │ 0x80|val│ Perde (ondalık) AYARLA         │ -            │
    │ 0xC0|val│ Perde (tam) AYARLA             │ -            │
    └─────────┴────────────────────────────────┴──────────────┘
    
    Örnek Kullanım:
        >>> curtain = CurtainControlSystemConnection()
        >>> curtain.setComPort("COM2")
        >>> curtain.open()
        >>> curtain.update()  # Sensör verilerini oku
        >>> print(f"Dış Sıcaklık: {curtain.getOutdoorTemp()}°C")
        >>> curtain.setCurtainStatus(50.0)  # Perde %50 aç
        >>> curtain.close()
    """
    
    def __init__(self):
        """
        Constructor - Board #2 için başlangıç değerleri
        """
        super().__init__()
        self.curtainStatus = 0.0         # Perde durumu (0=açık, 100=kapalı)
        self.outdoorTemperature = 0.0    # Dış sıcaklık (°C)
        self.outdoorPressure = 0.0       # Dış basınç (hPa)
        self.lightIntensity = 0.0        # Işık şiddeti (Lux)
    
    def update(self):
        """
        Board #2'den tüm sensör verilerini oku
        
        Bu metod sırayla şu işlemleri yapar:
        1. Dış sıcaklığı oku (BMP180 sensörü)
        2. Dış basıncı oku (BMP180 sensörü)
        3. Işık şiddetini oku (LDR sensörü)
        4. Perde durumunu oku (Step motor pozisyonu)
        
        Returns:
            bool: Tüm okumalar başarılı ise True
            
        Example:
            >>> curtain.update()
            ✓ Veriler güncellendi
              Dış Sıcaklık: 15.5°C
              Dış Basınç: 1013.2 hPa
              Işık: 450.0 Lux
              Perde: %25.0
        """
        try:
            print("\n📥 Board #2'den veriler okunuyor...")
            
            # ─────────────────────────────────────────────────────
            # 1. DIŞ SICAKLIĞI OKU (BMP180 - OUTDOOR_TEMP)
            # ─────────────────────────────────────────────────────
            self._send_byte(0x04)  # Komut: Outdoor temp (integral)
            temp_h = self._read_byte()
            
            self._send_byte(0x03)  # Komut: Outdoor temp (fractional)
            temp_l = self._read_byte()
            
            if temp_h is not None and temp_l is not None:
                self.outdoorTemperature = float(temp_h) + float(temp_l) / 10.0
                print(f"  ✓ Dış Sıcaklık: {self.outdoorTemperature:.1f}°C")
            else:
                print(f"  ✗ Dış sıcaklık okunamadı!")
            
            # ─────────────────────────────────────────────────────
            # 2. DIŞ BASINCI OKU (BMP180 - OUTDOOR_PRESS)
            # ─────────────────────────────────────────────────────
            self._send_byte(0x06)  # Komut: Outdoor pressure (integral)
            press_h = self._read_byte()
            
            self._send_byte(0x05)  # Komut: Outdoor pressure (fractional)
            press_l = self._read_byte()
            
            if press_h is not None and press_l is not None:
                # Basınç 300-1100 hPa arası (BMP180 özelliği)
                self.outdoorPressure = float(press_h) + float(press_l) / 10.0
                print(f"  ✓ Dış Basınç: {self.outdoorPressure:.1f} hPa")
            else:
                print(f"  ✗ Dış basınç okunamadı!")
            
            # ─────────────────────────────────────────────────────
            # 3. IŞIK ŞİDDETİNİ OKU (LDR - LIGHT_INTENSITY)
            # ─────────────────────────────────────────────────────
            self._send_byte(0x08)  # Komut: Light intensity (integral)
            light_h = self._read_byte()
            
            self._send_byte(0x07)  # Komut: Light intensity (fractional)
            light_l = self._read_byte()
            
            if light_h is not None and light_l is not None:
                self.lightIntensity = float(light_h) + float(light_l) / 10.0
                print(f"  ✓ Işık Şiddeti: {self.lightIntensity:.1f} Lux")
            else:
                print(f"  ✗ Işık şiddeti okunamadı!")
            
            # ─────────────────────────────────────────────────────
            # 4. PERDE DURUMUNU OKU (CURTAIN_STATE)
            # ─────────────────────────────────────────────────────
            self._send_byte(0x02)  # Komut: Curtain status (integral)
            curt_h = self._read_byte()
            
            self._send_byte(0x01)  # Komut: Curtain status (fractional)
            curt_l = self._read_byte()
            
            if curt_h is not None and curt_l is not None:
                self.curtainStatus = float(curt_h) + float(curt_l) / 10.0
                print(f"  ✓ Perde Durumu: %{self.curtainStatus:.1f}")
            else:
                print(f"  ✗ Perde durumu okunamadı!")
            
            print("✓ Veriler başarıyla güncellendi!\n")
            return True
            
        except Exception as e:
            print(f"✗ Update sırasında hata: {e}")
            return False
    
    def setCurtainStatus(self, status):
        """
        Perde durumunu ayarla
        
        Args:
            status (float): Perde açıklık oranı
                - 0.0 = Tam açık
                - 100.0 = Tam kapalı
                - Ara değerler = Kısmi açık
        
        Returns:
            bool: Başarılı ise True, geçersiz değer veya hata varsa False
            
        Raises:
            Exception: İletişim hatası durumunda
            
        Note:
            - Step motor 10 step/% oranında döner (R2.2.1)
            - 0-100% arası geçerli
            - Protokol: 0xC0|tam_kısım + 0x80|ondalık_kısım
            
        Example:
            >>> curtain.setCurtainStatus(50.0)
            ✓ Perde ayarlandı: %50.0
            True
            
            >>> curtain.setCurtainStatus(150.0)
            ✗ Hata: Perde %0-100 arası olmalı!
            False
        """
        # ─────────────────────────────────────────────────────
        # GEÇERLİLİK KONTROLÜ
        # ─────────────────────────────────────────────────────
        if status < 0.0 or status > 100.0:
            print(f"✗ Hata: Perde %0-100 arası olmalı! (Girilen: {status:.1f}%)")
            print(f"  → Geçerli aralık: 0.0% (tam açık) - 100.0% (tam kapalı)")
            return False
        
        try:
            # ─────────────────────────────────────────────────────
            # PERDE DEĞERINI TAM VE ONDALIK OLARAK AYIR
            # ─────────────────────────────────────────────────────
            # Örnek: 75.5% → tam=75, ondalık=5
            status_h = int(status)                      # Tam kısım
            status_l = int((status - status_h) * 10)   # Ondalık kısım
            
            print(f"📤 Perde ayarlanıyor: %{status:.1f}")
            print(f"   → Tam kısım: {status_h}")
            print(f"   → Ondalık kısım: {status_l}")
            
            # ─────────────────────────────────────────────────────
            # PDF'DEKİ PROTOKOLE GÖRE KOMUT GÖNDER
            # ─────────────────────────────────────────────────────
            # Format: 11XXXXXX (tam), 10XXXXXX (ondalık)
            
            # 1. Tam kısımı gönder (0xC0 = 11000000 binary)
            cmd_h = 0xC0 | (status_h & 0x3F)  # 0x3F = 00111111 (6-bit mask)
            self._send_byte(cmd_h)
            print(f"   → Komut gönderildi: 0x{cmd_h:02X} (tam kısım)")
            
            # 2. Ondalık kısımı gönder (0x80 = 10000000 binary)
            cmd_l = 0x80 | (status_l & 0x3F)
            self._send_byte(cmd_l)
            print(f"   → Komut gönderildi: 0x{cmd_l:02X} (ondalık kısım)")
            
            # Step motorun dönmesi için bekle
            time.sleep(0.2)
            
            print(f"✓ Perde başarıyla ayarlandı: %{status:.1f}\n")
            return True
            
        except Exception as e:
            print(f"✗ Perde ayarlama hatası: {e}")
            return False
    
    # ═════════════════════════════════════════════════════════
    # GETTER METODLARI
    # ═════════════════════════════════════════════════════════
    
    def getOutdoorTemp(self):
        """
        Son okunan dış sıcaklığı döndür
        
        Returns:
            float: Dış sıcaklık (°C)
            
        Note:
            BMP180 sensörü: -40°C ile 85°C arası
            Güncel değer için önce update() çağırın
        """
        return self.outdoorTemperature
    
    def getOutdoorPress(self):
        """
        Son okunan dış basıncı döndür
        
        Returns:
            float: Dış basınç (hPa)
            
        Note:
            BMP180 sensörü: 300-1100 hPa arası
            Güncel değer için önce update() çağırın
        """
        return self.outdoorPressure
    
    def getLightIntensity(self):
        """
        Son okunan ışık şiddetini döndür
        
        Returns:
            float: Işık şiddeti (Lux)
            
        Note:
            LDR sensörü analog değer
            Güncel değer için önce update() çağırın
        """
        return self.lightIntensity
    
    def getCurtainStatus(self):
        """
        Son okunan perde durumunu döndür
        
        Returns:
            float: Perde durumu (%)
                - 0.0 = Tam açık
                - 100.0 = Tam kapalı
        """
        return self.curtainStatus
    
    # ═════════════════════════════════════════════════════════
    # DEBUG METODLARI
    # ═════════════════════════════════════════════════════════
    
    def print_status(self):
        """
        Tüm sensör değerlerini ekrana yazdır (debug için)
        """
        print("\n" + "="*50)
        print("  BOARD #2 - PERDE KONTROL SİSTEMİ DURUMU")
        print("="*50)
        print(f"  Dış Sıcaklık       : {self.outdoorTemperature:.1f}°C")
        print(f"  Dış Basınç         : {self.outdoorPressure:.1f} hPa")
        print(f"  Işık Şiddeti       : {self.lightIntensity:.1f} Lux")
        print(f"  Perde Durumu       : %{self.curtainStatus:.1f}")
        print("="*50 + "\n")
