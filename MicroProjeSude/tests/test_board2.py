"""
Board #2 (Perde Kontrol Sistemi) Test Programı
EEM Projesi - BM-2 Görevi
R2.3-2: API test gereksinimine uygun

Bu test programı CurtainControlSystemConnection sınıfının
tüm fonksiyonlarını test eder.

Yazan: [SENIN ADIN SOYADIN]
Tarih: 11 Aralık 2025
"""

import sys
import os

# Üst dizini (MicroProje) path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.curtain_control import CurtainControlSystemConnection
import time

def print_header(text):
    """Test başlığı yazdır"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_subheader(text):
    """Alt başlık yazdır"""
    print(f"\n[{text}]")

def test_connection():
    """
    Test 1: Bağlantı testi
    """
    print_subheader("TEST 1: Bağlantı")
    
    curtain = CurtainControlSystemConnection()
    
    # COM port ayarla (Board #2 için farklı port olabilir)
    curtain.setComPort("COM14")  # veya COM1, COM3 (PICSimLab'e göre)
    curtain.setBaudRate(9600)
    
    # Port aç
    if curtain.open():
        print("✓ Port başarıyla açıldı")
        curtain.close()
        return True
    else:
        print("✗ Port açılamadı!")
        print("\n⚠ KONTROL ET:")
        print("  1. PICSimLab Board #2 çalışıyor mu?")
        print("  2. COM port numarası doğru mu?")
        print("  3. Board #1 ile aynı portu kullanıyor musun? (Farklı olmalı)")
        print("  4. UART IO modülü Board #2'ye ekli mi?")
        return False

def test_read_sensors(curtain):
    """
    Test 2: Sensör okuma testi
    """
    print_subheader("TEST 2: Sensör Verilerini Okuma")
    
    try:
        curtain.update()
        
        print(f"\n📊 Okunan Değerler:")
        print(f"  • Dış Sıcaklık       : {curtain.getOutdoorTemp():.1f}°C")
        print(f"  • Dış Basınç         : {curtain.getOutdoorPress():.1f} hPa")
        print(f"  • Işık Şiddeti       : {curtain.getLightIntensity():.1f} Lux")
        print(f"  • Perde Durumu       : %{curtain.getCurtainStatus():.1f}")
        
        return True
    except Exception as e:
        print(f"✗ Sensör okuma hatası: {e}")
        return False

def test_curtain_positions(curtain):
    """
    Test 3: Perde pozisyon ayarlama testi
    """
    print_subheader("TEST 3: Perde Pozisyon Kontrolü")
    
    # Farklı perde pozisyonları
    positions = [0.0, 25.0, 50.0, 75.0, 100.0]
    success_count = 0
    
    for pos in positions:
        print(f"\n  → %{pos:.0f} ayarlanıyor...")
        
        if curtain.setCurtainStatus(pos):
            time.sleep(1.5)  # Step motor için daha uzun bekleme
            curtain.update()
            
            actual = curtain.getCurtainStatus()
            diff = abs(actual - pos)
            
            if diff < 2.0:  # 2% tolerans
                print(f"  ✓ Başarılı! (Beklenen: %{pos:.0f}, Okunan: %{actual:.1f})")
                success_count += 1
            else:
                print(f"  ⚠ Uyarı: Fark var (Beklenen: %{pos:.0f}, Okunan: %{actual:.1f})")
        else:
            print(f"  ✗ Ayarlama başarısız!")
    
    print(f"\n  Başarı oranı: {success_count}/{len(positions)}")
    return success_count >= len(positions) - 1  # 1 hata tolere et

def test_invalid_curtain_values(curtain):
    """
    Test 4: Geçersiz perde değeri testi
    """
    print_subheader("TEST 4: Geçersiz Değer Kontrolü")
    
    invalid_positions = [
        (-10.0, "negatif değer"),
        (150.0, "çok yüksek (>100%)"),
        (-50.0, "negatif değer"),
        (200.0, "aralık dışı")
    ]
    
    success_count = 0
    
    for pos, reason in invalid_positions:
        print(f"\n  → %{pos:.0f} ({reason}) deneniyor...")
        
        if not curtain.setCurtainStatus(pos):
            print(f"  ✓ Doğru şekilde reddedildi!")
            success_count += 1
        else:
            print(f"  ✗ Hata: Geçersiz değer kabul edildi!")
    
    print(f"\n  Başarı oranı: {success_count}/{len(invalid_positions)}")
    return success_count == len(invalid_positions)

def test_sensor_accuracy(curtain):
    """
    Test 5: Sensör doğruluk testi
    """
    print_subheader("TEST 5: Sensör Değer Kontrolleri")
    
    try:
        curtain.update()
        
        checks = []
        
        # Sıcaklık kontrolü (-40°C ile 85°C arası olmalı - BMP180 spec)
        temp = curtain.getOutdoorTemp()
        temp_ok = -40 <= temp <= 85
        checks.append(("Dış Sıcaklık", temp_ok, f"{temp:.1f}°C", "-40°C ile 85°C arası"))
        
        # Basınç kontrolü (300-1100 hPa arası olmalı - BMP180 spec)
        press = curtain.getOutdoorPress()
        press_ok = 300 <= press <= 1100
        checks.append(("Dış Basınç", press_ok, f"{press:.1f} hPa", "300-1100 hPa arası"))
        
        # Işık kontrolü (pozitif olmalı)
        light = curtain.getLightIntensity()
        light_ok = light >= 0
        checks.append(("Işık Şiddeti", light_ok, f"{light:.1f} Lux", "≥0 Lux"))
        
        # Perde kontrolü (0-100% arası)
        curt = curtain.getCurtainStatus()
        curt_ok = 0 <= curt <= 100
        checks.append(("Perde Durumu", curt_ok, f"%{curt:.1f}", "%0-100 arası"))
        
        # Sonuçları yazdır
        print("\n")
        success_count = 0
        for name, ok, value, expected in checks:
            status = "✓" if ok else "✗"
            print(f"  {status} {name:.<20} {value:>15} (Beklenen: {expected})")
            if ok:
                success_count += 1
        
        print(f"\n  Başarı oranı: {success_count}/{len(checks)}")
        return success_count == len(checks)
        
    except Exception as e:
        print(f"✗ Hata: {e}")
        return False

def test_continuous_monitoring(curtain):
    """
    Test 6: Sürekli izleme testi
    """
    print_subheader("TEST 6: Sürekli Sensör İzleme (5 saniye)")
    
    try:
        for i in range(5):
            time.sleep(1)
            curtain.update()
            print(f"  {i+1}/5 - Sıcaklık: {curtain.getOutdoorTemp():.1f}°C, "
                  f"Basınç: {curtain.getOutdoorPress():.1f} hPa, "
                  f"Işık: {curtain.getLightIntensity():.1f} Lux, "
                  f"Perde: %{curtain.getCurtainStatus():.1f}")
        
        return True
    except Exception as e:
        print(f"✗ Hata: {e}")
        return False

def test_curtain_sweep(curtain):
    """
    Test 7: Perde süpürme testi (0'dan 100'e)
    """
    print_subheader("TEST 7: Perde Süpürme Testi")
    
    try:
        print("\n  → Perde %0'dan %100'e hareket edecek...")
        
        for pos in range(0, 101, 20):  # 0, 20, 40, 60, 80, 100
            curtain.setCurtainStatus(float(pos))
            time.sleep(0.8)
            curtain.update()
            print(f"  • Pozisyon: %{pos} → Okunan: %{curtain.getCurtainStatus():.1f}")
        
        print("\n  → Perde %100'den %0'a geri dönecek...")
        
        for pos in range(100, -1, -20):  # 100, 80, 60, 40, 20, 0
            curtain.setCurtainStatus(float(pos))
            time.sleep(0.8)
            curtain.update()
            print(f"  • Pozisyon: %{pos} → Okunan: %{curtain.getCurtainStatus():.1f}")
        
        print("  ✓ Süpürme testi tamamlandı!")
        return True
        
    except Exception as e:
        print(f"  ✗ Hata: {e}")
        return False

def run_all_tests():
    """
    Tüm testleri sırayla çalıştır
    """
    print_header("BOARD #2 - PERDE KONTROL SİSTEMİ TEST PROGRAMI")
    print("EEM Projesi - BM-2 Görevi")
    print("Test başlangıç: " + time.strftime("%H:%M:%S"))
    
    # Test sonuçları
    results = {
        "Bağlantı": False,
        "Sensör Okuma": False,
        "Perde Pozisyonları": False,
        "Geçersiz Değer": False,
        "Sensör Doğruluk": False,
        "Sürekli İzleme": False,
        "Perde Süpürme": False
    }
    
    # Test 1: Bağlantı
    results["Bağlantı"] = test_connection()
    
    if not results["Bağlantı"]:
        print("\n❌ BAĞLANTI HATASI - TESTLER DURDURULUYOR")
        print_test_summary(results)
        return False
    
    # Bağlantıyı aç
    curtain = CurtainControlSystemConnection()
    curtain.setComPort("COM2")  # Board #2 portu
    curtain.setBaudRate(9600)
    
    if not curtain.open():
        print("❌ Port açılamadı!")
        print_test_summary(results)
        return False
    
    try:
        # Test 2-7
        results["Sensör Okuma"] = test_read_sensors(curtain)
        results["Perde Pozisyonları"] = test_curtain_positions(curtain)
        results["Geçersiz Değer"] = test_invalid_curtain_values(curtain)
        results["Sensör Doğruluk"] = test_sensor_accuracy(curtain)
        results["Sürekli İzleme"] = test_continuous_monitoring(curtain)
        results["Perde Süpürme"] = test_curtain_sweep(curtain)
        
    finally:
        # Her durumda portu kapat
        print_subheader("Port Kapatılıyor")
        curtain.close()
    
    # Sonuç özeti
    print_test_summary(results)
    
    # Tüm testler başarılı mı?
    all_passed = all(results.values())
    return all_passed

def print_test_summary(results):
    """
    Test sonuçlarını özetle
    """
    print_header("TEST SONUÇLARI")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ BAŞARILI" if result else "✗ BAŞARISIZ"
        print(f"  {test_name:.<40} {status}")
    
    print("\n" + "="*60)
    print(f"  TOPLAM: {passed}/{total} test başarılı")
    
    if passed == total:
        print("  🎉 TÜM TESTLER BAŞARILI!")
    else:
        print(f"  ⚠ {total - passed} test başarısız!")
    
    print("="*60)
    print(f"Test bitiş: {time.strftime('%H:%M:%S')}\n")

if __name__ == "__main__":
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  BOARD #2 API TEST PROGRAMI".center(58) + "║")
    print("║" + "  (R2.3-2 Gereksinimi)".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    input("\n⏸  Devam etmek için ENTER'a bas... ")
    
    success = run_all_tests()
    
    if success:
        print("\n✅ TEST PAKETİ BAŞARIYLA TAMAMLANDI!\n")
        sys.exit(0)
    else:
        print("\n❌ BAZI TESTLER BAŞARISIZ OLDU!\n")
        sys.exit(1)
