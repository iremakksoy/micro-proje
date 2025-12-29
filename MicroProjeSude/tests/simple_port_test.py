
"""
COM Port Basit Test
com0com'un çalışıp çalışmadığını test eder
"""
import serial
import time

# !!!!! SENİN SİSTEMİNDEKİ PORT NUMARASI !!!!!
PORT = "COM14"  # Cihaz Yöneticisi'nde gördüğün numara

print("="*50)
print("  COM PORT TEST PROGRAMI")
print("="*50)
print(f"\nTest edilen port: {PORT}")
print("Baud rate: 9600")
print("\n" + "-"*50)

try:
    print(f"\n[1] {PORT} açılıyor...")
    ser = serial.Serial(PORT, 9600, timeout=1)
    print(f"    ✓ {PORT} başarıyla açıldı!")
    
    print(f"\n[2] Test byte'ı gönderiliyor...")
    ser.write(b'\x01')
    print("    ✓ Byte gönderildi: 0x01")
    
    print(f"\n[3] Cevap bekleniyor (3 saniye)...")
    time.sleep(3)
    
    if ser.in_waiting > 0:
        data = ser.read(ser.in_waiting)
        print(f"    ✓ Cevap alındı: {data.hex()}")
        print("    🎉 PICSimLab ile iletişim var!")
    else:
        print("    ⚠ Cevap yok")
        print("    → Bu normal! PICSimLab henüz çalışmıyor.")
    
    print(f"\n[4] Port kapatılıyor...")
    ser.close()
    print("    ✓ Port kapatıldı")
    
    print("\n" + "="*50)
    print("  ✅ TEST BAŞARILI - COM PORT ÇALIŞIYOR!")
    print("="*50)
    print("\n💡 Sonraki adım: PICSimLab'ı kur ve assembly kodunu yükle\n")
    
except serial.SerialException as e:
    print(f"    ✗ HATA: {e}")
    print("\n" + "="*50)
    print("  ❌ TEST BAŞARISIZ")
    print("="*50)
    print("\n💡 ÇÖZÜMLER:")
    print("  1. Port numarasını değiştir:")
    print("     PORT = 'COM12'  # COM14 yerine COM12 dene")
    print("\n  2. Cihaz Yöneticisi'nden portları kontrol et:")
    print("     Başlat → Cihaz Yöneticisi → Bağlantı Noktaları")
    print("\n  3. Başka program portu kullanıyor olabilir")
    print("     (Arduino IDE, PuTTY, vs. kapalı olmalı)")
    
except Exception as e:
    print(f"    ✗ Beklenmeyen hata: {e}")

input("\n⏸  Kapatmak için ENTER'a bas...")