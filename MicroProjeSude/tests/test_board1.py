
"""
Board #1 (Klima Sistemi) Test Programı
EEM Projesi - BM-2 Görevi
R2.3-2: API test gereksinimine uygun

Bu test programı AirConditionerSystemConnection sınıfının
tüm fonksiyonlarını test eder.

Yazan: [SENIN ADIN SOYADIN]
Tarih: 11 Aralık 2025
"""

import sys
import os

# Üst dizini (MicroProje) path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.air_conditioner import AirConditionerSystemConnection
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
    
    ac = AirConditionerSystemConnection()
    
    # COM port ayarla
    ac.setComPort("COM14")  # PICSimLab'deki porta göre değiştir
    ac.setBaudRate(9600)
    
    # Port aç
    if ac.open():
        print("✓ Port başarıyla açıldı")
        ac.close()
        return True
    else:
        print("✗ Port açılamadı!")
        print("\n⚠ KONTROL ET:")
        print("  1. PICSimLab çalışıyor mu?")
        print("  2. Virtual Serial Port kurulu mu? (com0com)")
        print("  3. COM port numarası doğru mu?")
        print("  4. PICSimLab'da UART IO modülü ekli mi?")
        return False

def test_read_data(ac):
    """
    Test 2: Veri okuma testi
    """
    print_subheader("TEST 2: Veri Okuma")
    
    try:
        ac.update()
        
        print(f"\n📊 Okunan Değerler:")
        print(f"  • Ortam Sıcaklığı    : {ac.getAmbientTemp():.1f}°C")
        print(f"  • İstenen Sıcaklık   : {ac.getDesiredTemp():.1f}°C")
        print(f"  • Fan Hızı           : {ac.getFanSpeed()} rps")
        
        return True
    except Exception as e:
        print(f"✗ Veri okuma hatası: {e}")
        return False

def test_set_temperature(ac):
    """
    Test 3: Sıcaklık ayarlama testi
    """
    print_subheader("TEST 3: Sıcaklık Ayarlama")
    
    test_temps = [20.0, 24.5, 28.0, 22.5]
    success_count = 0
    
    for temp in test_temps:
        print(f"\n  → {temp:.1f}°C ayarlanıyor...")
        
        if ac.setDesiredTemp(temp):
            time.sleep(1)  # PIC'in işlemesi için bekle
            ac.update()
            
            actual = ac.getDesiredTemp()
            diff = abs(actual - temp)
            
            if diff < 0.2:  # 0.2°C tolerans
                print(f"  ✓ Başarılı! (Beklenen: {temp:.1f}, Okunan: {actual:.1f})")
                success_count += 1
            else:
                print(f"  ⚠ Uyarı: Fark var (Beklenen: {temp:.1f}, Okunan: {actual:.1f})")
        else:
            print(f"  ✗ Ayarlama başarısız!")
    
    print(f"\n  Başarı oranı: {success_count}/{len(test_temps)}")
    return success_count == len(test_temps)

def test_invalid_values(ac):
    """
    Test 4: Geçersiz değer testi
    """
    print_subheader("TEST 4: Geçersiz Değer Kontrolü")
    
    invalid_temps = [
        (5.0, "çok düşük (<10°C)"),
        (55.0, "çok yüksek (>50°C)"),
        (-10.0, "negatif değer"),
        (100.0, "aralık dışı")
    ]
    
    success_count = 0
    
    for temp, reason in invalid_temps:
        print(f"\n  → {temp:.1f}°C ({reason}) deneniyor...")
        
        if not ac.setDesiredTemp(temp):
            print(f"  ✓ Doğru şekilde reddedildi!")
            success_count += 1
        else:
            print(f"  ✗ Hata: Geçersiz değer kabul edildi!")
    
    print(f"\n  Başarı oranı: {success_count}/{len(invalid_temps)}")
    return success_count == len(invalid_temps)

def test_continuous_read(ac):
    """
    Test 5: Sürekli okuma testi
    """
    print_subheader("TEST 5: Sürekli Okuma (5 saniye)")
    
    try:
        for i in range(5):
            time.sleep(1)
            ac.update()
            print(f"  {i+1}/5 - Ortam: {ac.getAmbientTemp():.1f}°C, "
                  f"İstenen: {ac.getDesiredTemp():.1f}°C, "
                  f"Fan: {ac.getFanSpeed()} rps")
        
        return True
    except Exception as e:
        print(f"✗ Hata: {e}")
        return False

def test_stress(ac):
    """
    Test 6: Stres testi (hızlı okuma/yazma)
    """
    print_subheader("TEST 6: Stres Testi")
    
    try:
        print("\n  → 10 kez hızlı sıcaklık değiştirme...")
        
        for i in range(10):
            temp = 20.0 + (i % 5) * 2  # 20, 22, 24, 26, 28, 20...
            ac.setDesiredTemp(temp)
            time.sleep(0.5)
            ac.update()
            print(f"  {i+1}/10 - Ayarlanan: {temp:.1f}°C")
        
        print("  ✓ Stres testi tamamlandı!")
        return True
        
    except Exception as e:
        print(f"  ✗ Hata: {e}")
        return False

def run_all_tests():
    """
    Tüm testleri sırayla çalıştır
    """
    print_header("BOARD #1 - KLIMA SİSTEMİ TEST PROGRAMI")
    print("EEM Projesi - BM-2 Görevi")
    print("Test başlangıç: " + time.strftime("%H:%M:%S"))
    
    # Test sonuçları
    results = {
        "Bağlantı": False,
        "Veri Okuma": False,
        "Sıcaklık Ayarlama": False,
        "Geçersiz Değer": False,
        "Sürekli Okuma": False,
        "Stres Testi": False
    }
    
    # Test 1: Bağlantı
    results["Bağlantı"] = test_connection()
    
    if not results["Bağlantı"]:
        print("\n❌ BAĞLANTI HATASI - TESTLER DURDURULUYOR")
        print_test_summary(results)
        return False
    
    # Bağlantıyı aç
    ac = AirConditionerSystemConnection()
    ac.setComPort("COM1")
    ac.setBaudRate(9600)
    
    if not ac.open():
        print("❌ Port açılamadı!")
        print_test_summary(results)
        return False
    
    try:
        # Test 2-6
        results["Veri Okuma"] = test_read_data(ac)
        results["Sıcaklık Ayarlama"] = test_set_temperature(ac)
        results["Geçersiz Değer"] = test_invalid_values(ac)
        results["Sürekli Okuma"] = test_continuous_read(ac)
        results["Stres Testi"] = test_stress(ac)
        
    finally:
        # Her durumda portu kapat
        print_subheader("Port Kapatılıyor")
        ac.close()
    
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
    print("║" + "  BOARD #1 API TEST PROGRAMI".center(58) + "║")
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