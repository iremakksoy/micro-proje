; =================================================================
; DOSYA: variables.inc
; AÇIKLAMA: RAM Degiskenleri ve Sabit Tanimlari
; =================================================================

    CBLOCK 0x20 ; Genel Amacli Registerlar
        ; --- Gecici Degiskenler ---
        w_temp          ; W saklayici (Kesme icin)
        status_temp     ; STATUS saklayici (Kesme icin)
        Math_Temp_H     ; Carpma/Bolme icin Yuksek byte
        Math_Temp_L     ; Carpma/Bolme icin Dusuk byte
        Delay_1         ; Gecikme sayaci 1
        Delay_2         ; Gecikme sayaci 2
        
        ; --- Sistem Durumu ---
        Desired_Curtain ; Istenen Perde Yuzdesi (0-100)
        Current_Curtain ; Mevcut Perde Yuzdesi (0-100)
        
        ; --- Step Motor Kontrolu ---
        Target_Steps_H  ; Hedeflenen Adim (High Byte)
        Target_Steps_L  ; Hedeflenen Adim (Low Byte)
        Current_Steps_H ; O anki Adim Pozisyonu (High)
        Current_Steps_L ; O anki Adim Pozisyonu (Low)
        Step_Phase      ; Motor adim sirasi (0-3)
        
        ; --- Sensorler ---
        Light_Value     ; LDR Degeri (0-255 ADC)
        Pot_Value       ; Potansiyometre Ham Degeri
        
        ; --- UART Tamponu ---
        UART_Rx_Temp    ; Gelen veri gecici
        Curtain_Set_L   ; PC'den gelen ayar (Alt 6 bit)
        Curtain_Set_H   ; PC'den gelen ayar (Ust bitler)
        
        ; --- LCD Cevrimi ---
        BCD_Hundreds    ; Yuzler basamagi
        BCD_Tens        ; Onlar basamagi
        BCD_Ones        ; Birler basamagi
    ENDC

; --- Sabitler ---
STEPS_PER_PERCENT EQU d'10' ; Her yuzde 1 icin 10 adim
LDR_THRESHOLD     EQU d'150' ; LDR Esik Degeri