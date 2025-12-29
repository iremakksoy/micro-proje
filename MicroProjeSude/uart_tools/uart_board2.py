"""
Board #2 (Perde) - UART Direkt Komut Gönderici
BM-1 Görevi - PC Tarafı UART İletişimi
Yazan: [SENIN ADIN SOYADIN]
Tarih: 11 Aralık 2025

DÜZELTME: Timeout kısaltıldı (0.3s), döngü hatası giderildi
"""

import serial
import time
import sys

class UARTBoard2:
    """Board #2 için direkt UART iletişim sınıfı"""
    
    def _init_(self, port="COM14", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
    
    def connect(self):
        """Seri porta bağlan"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=0.3  # DÜZELTME: 1 saniye → 0.3 saniye
            )
            time.sleep(1)  # DÜZELTME: 2 saniye → 1 saniye
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            print(f"✓ Bağlantı kuruldu: {self.port} @ {self.baudrate}")
            return True
        except Exception as e:
            print(f"✗ Bağlantı hatası: {e}")
            return False
    
    def disconnect(self):
        """Bağlantıyı kes"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("✓ Bağlantı kapatıldı")
    
    def send_byte(self, byte_val):
        """Tek byte gönder"""
        if not self.ser or not self.ser.is_open:
            print("✗ Port açık değil!")
            return False
        
        self.ser.write(bytes([byte_val]))
        print(f"  → Gönderildi: 0x{byte_val:02X}")
        time.sleep(0.05)
        return True
    
    def read_byte(self):
        """Tek byte oku"""
        if not self.ser or not self.ser.is_open:
            print("✗ Port açık değil!")
            return None
        
        data = self.ser.read(1)
        if len(data) == 1:
            print(f"  ← Alındı: 0x{data[0]:02X} ({data[0]})")
            return data[0]
        else:
            print("  ⚠ Timeout - cevap yok")
            return None
    
    def get_curtain_status(self):
        """Perde durumunu oku"""
        print("\n[Komut] Perde Durumu")
        self.send_byte(0x02)  # Tam
        curt_h = self.read_byte()
        self.send_byte(0x01)  # Ondalık
        curt_l = self.read_byte()
        
        if curt_h is not None and curt_l is not None:
            status = float(curt_h) + float(curt_l) / 10.0
            print(f"📊 Perde: %{status:.1f}")
            return status
        return None
    
    def get_outdoor_temp(self):
        """Dış sıcaklık oku"""
        print("\n[Komut] Dış Sıcaklık")
        self.send_byte(0x04)  # Tam
        temp_h = self.read_byte()
        self.send_byte(0x03)  # Ondalık
        temp_l = self.read_byte()
        
        if temp_h is not None and temp_l is not None:
            temp = float(temp_h) + float(temp_l) / 10.0
            print(f"📊 Dış Sıcaklık: {temp:.1f}°C")
            return temp
        return None
    
    def get_outdoor_pressure(self):
        """Dış basınç oku"""
        print("\n[Komut] Dış Basınç")
        self.send_byte(0x06)  # Tam
        press_h = self.read_byte()
        self.send_byte(0x05)  # Ondalık
        press_l = self.read_byte()
        
        if press_h is not None and press_l is not None:
            pressure = float(press_h) + float(press_l) / 10.0
            print(f"📊 Dış Basınç: {pressure:.1f} hPa")
            return pressure
        return None
    
    def get_light_intensity(self):
        """Işık şiddeti oku"""
        print("\n[Komut] Işık Şiddeti")
        self.send_byte(0x08)  # Tam
        light_h = self.read_byte()
        self.send_byte(0x07)  # Ondalık
        light_l = self.read_byte()
        
        if light_h is not None and light_l is not None:
            light = float(light_h) + float(light_l) / 10.0
            print(f"📊 Işık: {light:.1f} Lux")
            return light
        return None
    
    def set_curtain_status(self, status):
        """Perde durumu ayarla"""
        if status < 0 or status > 100:
            print(f"✗ Hata: Perde %0-100 arası olmalı! (Girilen: {status})")
            return False
        
        status_h = int(status)
        status_l = int((status - status_h) * 10)
        
        print(f"\n[Komut] Perde Ayarla: %{status:.1f}")
        print(f"  Tam kısım: {status_h}, Ondalık: {status_l}")
        
        cmd_h = 0xC0 | (status_h & 0x3F)
        self.send_byte(cmd_h)
        
        cmd_l = 0x80 | (status_l & 0x3F)
        self.send_byte(cmd_l)
        
        print("✓ Komut gönderildi")
        return True
    
    def read_all_data(self):
        """Tüm verileri oku"""
        print("\n" + "="*50)
        print("  TÜM VERİLERİ OKU")
        print("="*50)
        
        self.get_outdoor_temp()
        self.get_outdoor_pressure()
        self.get_light_intensity()
        self.get_curtain_status()
        
        print("="*50)  # DÜZELTME: Bu satır eklendi


def interactive_mode():
    """İnteraktif mod"""
    print("\n" + "="*60)
    print("  BOARD #2 - İNTERAKTİF UART KOMUT GÖNDERİCİ")
    print("  BM-1 Görevi - Direkt UART İletişimi")
    print("="*60)
    
    port = input("\nCOM Port (varsayılan: COM14): ").strip() or "COM14"
    
    uart = UARTBoard2(port=port)
    
    if not uart.connect():
        print("\n❌ Bağlantı kurulamadı!")
        input("\n⏸  Kapatmak için ENTER...")  # DÜZELTME: Eklendi
        return
    
    try:
        while True:
            print("\n" + "-"*60)
            print("MENÜ:")
            print("  1. Tüm verileri oku")
            print("  2. Dış sıcaklık oku")
            print("  3. Dış basınç oku")
            print("  4. Işık şiddeti oku")
            print("  5. Perde durumu oku")
            print("  6. Perde durumu ayarla")
            print("  7. Ham komut gönder (HEX)")
            print("  0. Çıkış")
            print("-"*60)
            
            choice = input("Seçim: ").strip()
            
            if choice == "0":
                print("\n🚪 Çıkılıyor...")
                break
            elif choice == "1":
                uart.read_all_data()
            elif choice == "2":
                uart.get_outdoor_temp()
            elif choice == "3":
                uart.get_outdoor_pressure()
            elif choice == "4":
                uart.get_light_intensity()
            elif choice == "5":
                uart.get_curtain_status()
            elif choice == "6":
                try:
                    status = float(input("Perde durumu (%0-100): "))
                    uart.set_curtain_status(status)
                except ValueError:
                    print("✗ Geçersiz sayı!")
            elif choice == "7":
                try:
                    hex_val = input("HEX değer (örn: 0x04): ").strip()
                    if hex_val.startswith("0x"):
                        byte_val = int(hex_val, 16)
                    else:
                        byte_val = int(hex_val)
                    
                    uart.send_byte(byte_val)
                    response = uart.read_byte()
                    if response is not None:
                        print(f"Cevap: {response} (0x{response:02X})")
                except ValueError:
                    print("✗ Geçersiz HEX değeri!")
            else:
                print("✗ Geçersiz seçim!")
            
            input("\n⏸  Devam etmek için ENTER...")  # DÜZELTME: Her test sonrası bekle
    
    except KeyboardInterrupt:  # DÜZELTME: CTRL+C yakalama
        print("\n\n⚠ CTRL+C ile durduruldu!")
    
    finally:
        uart.disconnect()
    
    print("\n✅ Program sonlandırıldı\n")


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  BOARD #2 UART ARAÇLARI".center(58) + "║")
    print("║" + "  BM-1 Görevi (DÜZELTME v2)".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    interactive_mode()