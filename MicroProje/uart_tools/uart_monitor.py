"""
UART Trafik İzleyici
BM-1 Görevi - UART İletişim Analizi
Yazan: [SENIN ADIN SOYADIN]
Tarih: 11 Aralık 2025

PIC ile PC arasındaki UART trafiğini izler ve loglar.
"""

import serial
import time
from datetime import datetime

class UARTMonitor:
    """UART trafiğini izle ve logla"""
    
    def __init__(self, port="COM14", baudrate=9600, log_file=None):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.log_file = log_file
        self.running = False
    
    def connect(self):
        """Porta bağlan"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0.1
            )
            print(f"✓ İzleme başladı: {self.port} @ {self.baudrate} baud")
            if self.log_file:
                print(f"✓ Log dosyası: {self.log_file}")
            return True
        except Exception as e:
            print(f"✗ Bağlantı hatası: {e}")
            return False
    
    def disconnect(self):
        """Bağlantıyı kes"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("\n✓ İzleme durduruldu")
    
    def log_message(self, message):
        """Mesajı ekrana ve dosyaya yaz"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_line = f"[{timestamp}] {message}"
        
        print(log_line)
        
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_line + "\n")
    
    def decode_command(self, byte_val):
        """Komutu decode et"""
        # Board #1 komutları
        commands_board1 = {
            0x01: "İstenen sıcaklık (ondalık) AL",
            0x02: "İstenen sıcaklık (tam) AL",
            0x03: "Ortam sıcaklığı (ondalık) AL",
            0x04: "Ortam sıcaklığı (tam) AL",
            0x05: "Fan hızı AL"
        }
        
        # Board #2 komutları
        commands_board2 = {
            0x01: "Perde (ondalık) AL",
            0x02: "Perde (tam) AL",
            0x03: "Dış sıcaklık (ondalık) AL",
            0x04: "Dış sıcaklık (tam) AL",
            0x05: "Dış basınç (ondalık) AL",
            0x06: "Dış basınç (tam) AL",
            0x07: "Işık (ondalık) AL",
            0x08: "Işık (tam) AL"
        }
        
        # Set komutları
        if byte_val & 0xC0 == 0xC0:
            value = byte_val & 0x3F
            return f"SET (tam) = {value}"
        elif byte_val & 0x80 == 0x80:
            value = byte_val & 0x3F
            return f"SET (ondalık) = {value}"
        
        # Get komutları
        if byte_val in commands_board1:
            return f"[B1] {commands_board1[byte_val]}"
        elif byte_val in commands_board2:
            return f"[B2] {commands_board2[byte_val]}"
        else:
            return f"Bilinmeyen komut"
    
    def monitor(self):
        """Trafiği izle"""
        if not self.connect():
            return
        
        print("\n" + "="*60)
        print("  UART TRAFİK İZLEYİCİ")
        print("  CTRL+C ile durdurun")
        print("="*60 + "\n")
        
        self.running = True
        byte_count = 0
        
        try:
            while self.running:
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting)
                    
                    for byte_val in data:
                        byte_count += 1
                        decoded = self.decode_command(byte_val)
                        self.log_message(f"#{byte_count:04d} → 0x{byte_val:02X} ({byte_val:3d}) | {decoded}")
                
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("\n\n⏸ Kullanıcı tarafından durduruldu")
        
        finally:
            self.disconnect()
            print(f"\n📊 Toplam {byte_count} byte izlendi")


def main():
    """Ana program"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  UART TRAFİK İZLEYİCİ".center(58) + "║")
    print("║" + "  BM-1 Görevi".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝\n")
    
    port = input("COM Port (varsayılan: COM14): ").strip() or "COM14"
    
    log_choice = input("Log dosyası oluştur? (E/H, varsayılan: H): ").strip().upper()
    log_file = None
    
    if log_choice == "E":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"uart_log_{timestamp}.txt"
    
    monitor = UARTMonitor(port=port, log_file=log_file)
    monitor.monitor()


if __name__ == "__main__":
    main()
