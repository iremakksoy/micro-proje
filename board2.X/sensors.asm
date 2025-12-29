; =================================================================
; DOSYA: sensors.asm
; AÇIKLAMA: ADC Okuma Rutinleri (Guvenli Beklemeli)
; =================================================================

; --- LDR OKUMA (Kanal 0) ---
Read_LDR:
    BANKSEL ADCON0
    MOVLW   b'10000001' ; Fosc/32, Kanal 0 (AN0), ADC On
    MOVWF   ADCON0
    
    CALL    ADC_Safe_Wait ; KANAL DEGISTIKTEN SONRA BEKLE!
    
    BSF     ADCON0, GO  ; Cevirimi baslat
Wait_LDR_Done:
    BTFSC   ADCON0, GO
    GOTO    Wait_LDR_Done
    
    BANKSEL ADRESH
    MOVF    ADRESH, W
    BANKSEL Light_Value
    MOVWF   Light_Value
    RETURN

; --- POTANSIYOMETRE OKUMA (Kanal 1) ---
Read_Pot:
    BANKSEL ADCON0
    MOVLW   b'10001001' ; Fosc/32, Kanal 1 (AN1), ADC On
    MOVWF   ADCON0
    
    CALL    ADC_Safe_Wait ; KONDANSATORUN SARJ OLMASI ICIN BEKLE!
    
    BSF     ADCON0, GO  ; Cevirimi baslat
Wait_Pot_Done:
    BTFSC   ADCON0, GO
    GOTO    Wait_Pot_Done
    
    BANKSEL ADRESH
    MOVF    ADRESH, W
    BANKSEL Pot_Value
    MOVWF   Pot_Value
    
    ; --- OLCEKLEME (0-255 -> 0-100) ---
    ; Basit yontem: Degeri 2'ye bol ve 100'e sinirla
    BCF     STATUS, C
    RRF     Pot_Value, W ; W = Pot / 2
    MOVWF   Desired_Curtain
    
    ; Eger sonuc > 100 ise, 100 yap
    MOVLW   d'100'
    SUBWF   Desired_Curtain, W
    BTFSC   STATUS, C    ; Desired >= 100 ise C=1 olur
    GOTO    Fix_100
    RETURN

Fix_100:
    MOVLW   d'100'
    MOVWF   Desired_Curtain
    RETURN

; --- GUVENLI BEKLEME RUTINI ---
; ADC kanal gecislerinde kapasitorun sarj olmasi icin
; mutlaka yeterli sure (yaklasik 20-50us) beklenmelidir.
ADC_Safe_Wait:
    MOVLW   d'50'       ; Biraz uzun tutalim ki garanti olsun
    MOVWF   w_temp      ; Gecici sayac olarak w_temp kullanalim
ADC_Loop:
    DECFSZ  w_temp, F
    GOTO    ADC_Loop
    RETURN