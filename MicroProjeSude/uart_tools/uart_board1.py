"""
Board #1 (Klima) - UART Direkt Komut Gönderici
BM-1 Görevi - PC Tarafı UART İletişimi
Yazan: [SENIN ADIN SOYADIN]
Tarih: 11 Aralık 2025

Bu program Board #1 ile direkt UART komutları gönderir ve cevapları okur.
API kullanmadan ham UART iletişimi yapar (BM-1 gereksinimi).
"""

import serial
import time
import sys

class UARTBoard1:
    """
    Board #1 için direkt UART iletişim sınıfı
    
    UART Protokolü (R2.1.4-1):
    - 0x01: İstenen sıcaklık (ondalık) AL
    - 0x02: İstenen sıcaklık (tam) AL
    - 0x03: Ortam sıcaklığı (ondalık) AL
    - 0x04: Ortam sıcaklığı (tam) AL
    - 0x05: Fan hızı AL
    - 0xC0 | değer: Sıcaklık (tam) AYARLA
    - 0x80 | değer: Sıcaklık (ondalık) AYARLA
    """
    
    def __init__(self, port="COM14", baudrate=9600):
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
                timeout=1
            )
            time.sleep(2)  # PIC reset bekleme
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
    
    def get_desired_temp_integral(self):
        """İstenen sıcaklık (tam kısım) oku"""
        print("\n[Komut] İstenen Sıcaklık (Tam Kısım)")
        self.send_byte(0x02)
        return self.read_byte()
    
    def get_desired_temp_fractional(self):
        """İstenen sıcaklık (ondalık kısım) oku"""
        print("\n[Komut] İstenen Sıcaklık (Ondalık Kısım)")
        self.send_byte(0x01)
        return self.read_byte()
    
    def get_ambient_temp_integral(self):
        """Ortam sıcaklığı (tam kısım) oku"""
        print("\n[Komut] Ortam Sıcaklığı (Tam Kısım)")
        self.send_byte(0x04)
        return self.read_byte()
    
    def get_ambient_temp_fractional(self):
        """Ortam sıcaklığı (ondalık kısım) oku"""
        print("\n[Komut] Ortam Sıcaklığı (Ondalık Kısım)")
        self.send_byte(0x03)
        return self.read_byte()
    
    def get_fan_speed(self):
        """Fan hızı oku"""
        print("\n[Komut] Fan Hızı")
        self.send_byte(0x05)
        return self.read_byte()
    
    def set_desired_temp(self, temp):
        """İstenen sıcaklığı ayarla"""
        if temp < 10.0 or temp > 50.0:
            print(f"✗ Hata: Sıcaklık 10-50°C arası olmalı! (Girilen: {temp})")
            return False
        
        temp_h = int(temp)
        temp_l = int((temp - temp_h) * 10)
        
        print(f"\n[Komut] İstenen Sıcaklık Ayarla: {temp:.1f}°C")
        print(f"  Tam kısım: {temp_h}, Ondalık: {temp_l}")
        
        # Tam kısım gönder
        cmd_h = 0xC0 | (temp_h & 0x3F)
        self.send_byte(cmd_h)
        
        # Ondalık kısım gönder
        cmd_l = 0x80 | (temp_l & 0x3F)
        self.send_byte(cmd_l)
        
        print("✓ Komut gönderildi")
        return True
    
    def read_all_data(self):
        """Tüm verileri oku ve göster"""
        print("\n" + "="*50)
        print("  TÜM VERİLERİ OKU")
        print("="*50)
        
        # Ortam sıcaklığı
        amb_h = self.get_ambient_temp_integral()
        amb_l = self.get_ambient_temp_fractional()
        if amb_h is not None and amb_l is not None:
            ambient = float(amb_h) + float(amb_l) / 10.0
            print(f"\n📊 Ortam Sıcaklığı: {ambient:.1f}°C")
        
        # İstenen sıcaklık
        des_h = self.get_desired_temp_integral()
        des_l = self.get_desired_temp_fractional()
        if des_h is not None and des_l is not None:
            desired = float(des_h) + float(des_l) / 10.0
            print(f"📊 İstenen Sıcaklık: {desired:.1f}°C")
        
        # Fan hızı
        fan = self.get_fan_speed()
        if fan is not None:
            print(f"📊 Fan Hızı: {fan} rps")
        
        print("="*50)


def interactive_mode():
    """İnteraktif mod - Kullanıcı menüsü"""
    print("\n" + "="*60)
    print("  BOARD #1 - İNTERAKTİF UART KOMUT GÖNDERİCİ")
    print("  BM-1 Görevi - Direkt UART İletişimi")
    print("="*60)
    
    port = input("\nCOM Port (varsayılan: COM14): ").strip() or "COM14"
    
    uart = UARTBoard1(port=port)
    
    if not uart.connect():
        print("\n❌ Bağlantı kurulamadı!")
        return
    
    try:
        while True:
            print("\n" + "-"*60)
            print("MENÜ:")
            print("  1. Tüm verileri oku")
            print("  2. İstenen sıcaklığı oku")
            print("  3. Ortam sıcaklığını oku")
            print("  4. Fan hızını oku")
            print("  5. İstenen sıcaklığı ayarla")
            print("  6. Ham komut gönder (HEX)")
            print("  0. Çıkış")
            print("-"*60)
            
            choice = input("Seçim: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                uart.read_all_data()
            elif choice == "2":
                uart.get_desired_temp_integral()
                uart.get_desired_temp_fractional()
            elif choice == "3":
                uart.get_ambient_temp_integral()
                uart.get_ambient_temp_fractional()
            elif choice == "4":
                uart.get_fan_speed()
            elif choice == "5":
                try:
                    temp = float(input("Sıcaklık (10-50°C): "))
                    uart.set_desired_temp(temp)
                except ValueError:
                    print("✗ Geçersiz sayı!")
            elif choice == "6":
                try:
                    hex_val = input("HEX değer (örn: 0x04 veya 4): ").strip()
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
            
            input("\n⏸  Devam etmek için ENTER...")
    
    finally:
        uart.disconnect()
    
    print("\n✅ Program sonlandırıldı\n")


def demo_mode():
    """Demo mod - Otomatik test"""
    print("\n" + "="*60)
    print("  BOARD #1 - DEMO MODU")
    print("="*60)
    
    uart = UARTBoard1(port="COM14")
    
    if not uart.connect():
        return
    
    try:
        # 1. Tüm verileri oku
        uart.read_all_data()
        time.sleep(2)
        
        # 2. Sıcaklık ayarla
        print("\n[DEMO] Sıcaklık 24.5°C olarak ayarlanıyor...")
        uart.set_desired_temp(24.5)
        time.sleep(2)
        
        # 3. Tekrar oku
        uart.read_all_data()
        
    finally:
        uart.disconnect()


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  BOARD #1 UART ARAÇLARI".center(58) + "║")
    print("║" + "  BM-1 Görevi".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_mode()
    else:
        interactive_mode()
