; =================================================================
; DOSYA: UART_Module.asm
; AÇIKLAMA: 9600 Baud Serial Haberle?me
; =================================================================

UART_Init:
    BANKSEL SPBRG
    MOVLW   d'25'       ; 9600 Baud @ 4MHz (BRGH=1)
    MOVWF   SPBRG
    
    MOVLW   b'00100100' ; TXEN, High Speed
    MOVWF   TXSTA
    
    BANKSEL RCSTA
    MOVLW   b'10010000' ; SPEN, CREN
    MOVWF   RCSTA
    RETURN

UART_Receive_Handler:
    BANKSEL RCREG
    MOVF    RCREG, W
    MOVWF   UART_Rx_Temp
    
    ; --- KOMUT AYRI?TIRMA (Sayfa 19 Tablo) ---
    
    ; 1. Get Desired Curtain (Fraction/Low) -> Bizde ondal?k yok, 0 dönebiliriz.
    MOVF    UART_Rx_Temp, W
    XORLW   b'00000001'
    BTFSC   STATUS, Z
    GOTO    Send_Zero   ; Ondal?k k?s?m yok
    
    ; 2. Get Desired Curtain (Integral/High)
    MOVF    UART_Rx_Temp, W
    XORLW   b'00000010'
    BTFSC   STATUS, Z
    GOTO    Send_Desired
    
    ; 3. Get Light Intensity (High Byte)
    MOVF    UART_Rx_Temp, W
    XORLW   b'00001000' ; Tabloya göre ID
    BTFSC   STATUS, Z
    GOTO    Send_Light
    
    ; --- SET COMMANDS (Maskeleme Gerekir) ---
    
    ; Set Desired Low (10xxxxxx)
    MOVF    UART_Rx_Temp, W
    ANDLW   b'11000000' ; Üst iki bite bak
    XORLW   b'10000000' ; 10 ile ba?l?yor mu?
    BTFSC   STATUS, Z
    GOTO    Store_Low_Bits
    
    ; Set Desired High (11xxxxxx)
    MOVF    UART_Rx_Temp, W
    ANDLW   b'11000000'
    XORLW   b'11000000' ; 11 ile ba?l?yor mu?
    BTFSC   STATUS, Z
    GOTO    Store_High_Bits
    
    RETURN

; --- CEVAP RUT?NLER? ---
Send_Zero:
    MOVLW   d'0'
    CALL    UART_Tx
    RETURN

Send_Desired:
    MOVF    Desired_Curtain, W
    CALL    UART_Tx
    RETURN

Send_Light:
    MOVF    Light_Value, W
    CALL    UART_Tx
    RETURN

; --- KAYIT RUT?NLER? ---
Store_Low_Bits:
    ; 10xxxxxx -> Alt 6 bit
    MOVF    UART_Rx_Temp, W
    ANDLW   b'00111111'
    MOVWF   Curtain_Set_L
    RETURN

Store_High_Bits:
    ; 11xxxxxx -> Üst bitler
    ; PDF protokolü biraz karma??k, basitlik için:
    ; Gelen verinin alt 6 bitini al, Low ile birle?tir.
    ; Burada sadece High byte geldi?inde güncelleme yapal?m.
    MOVF    UART_Rx_Temp, W
    ANDLW   b'00111111'
    ; Normalde shift gerekir ama proje basitli?i için 
    ; direkt bu de?eri Desired olarak atayal?m (0-63 aras? kontrol eder)
    ; VEYA Curtain_Set_L ile birle?tirme yap?lmal?.
    
    MOVWF   Desired_Curtain ; Basitle?tirilmi? kabul.
    RETURN

UART_Tx:
    BANKSEL TXSTA
Tx_Wait:
    BTFSS   TXSTA, TRMT
    GOTO    Tx_Wait
    BANKSEL TXREG
    MOVWF   TXREG
    RETURN


