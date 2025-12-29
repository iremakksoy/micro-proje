; =================================================================
; DOSYA: LCD_Module.asm
; AÇIKLAMA: LCD Sürücüsü (PORTD Data, RE0/RE1 Control)
; =================================================================

LCD_Init:
    ; 15ms Bekle
    CALL    Delay_Long
    
    MOVLW   b'00111000' ; Function Set: 8-bit, 2 Line, 5x7 Dots
    CALL    Send_Cmd
    
    MOVLW   b'00001100' ; Display On, Cursor Off
    CALL    Send_Cmd
    
    MOVLW   b'00000110' ; Entry Mode: Increment
    CALL    Send_Cmd
    
    MOVLW   b'00000001' ; Clear Display
    CALL    Send_Cmd
    RETURN

LCD_Draw_Interface:
    MOVLW   0x80        ; Sat?r 1
    CALL    Send_Cmd
    MOVLW   'C'
    CALL    Send_Data
    MOVLW   'u'
    CALL    Send_Data
    MOVLW   'r'
    CALL    Send_Data
    MOVLW   't'
    CALL    Send_Data
    MOVLW   ':'
    CALL    Send_Data
    
    MOVLW   0xC0        ; Sat?r 2
    CALL    Send_Cmd
    MOVLW   'L'
    CALL    Send_Data
    MOVLW   'i'
    CALL    Send_Data
    MOVLW   'g'
    CALL    Send_Data
    MOVLW   'h'
    CALL    Send_Data
    MOVLW   't'
    CALL    Send_Data
    MOVLW   ':'
    CALL    Send_Data
    RETURN

LCD_Update_Values:
    ; Perde De?erini Yaz (Sat?r 1, 8. karakter)
    MOVLW   0x87
    CALL    Send_Cmd
    MOVF    Current_Curtain, W
    CALL    BinToDec
    MOVLW   '%'
    CALL    Send_Data
    
    ; I??k De?erini Yaz (Sat?r 2, 7. karakter)
    MOVLW   0xC7
    CALL    Send_Cmd
    MOVF    Light_Value, W
    CALL    BinToDec
    RETURN

; --- YARDIMCI RUT?NLER ---
Send_Cmd:
    BANKSEL PORTD
    MOVWF   PORTD
    BCF     PORTE, 0    ; RS = 0 (Command)
    BSF     PORTE, 1    ; E = 1
    NOP
    BCF     PORTE, 1    ; E = 0
    CALL    Delay_Short
    RETURN

Send_Data:
    BANKSEL PORTD
    MOVWF   PORTD
    BSF     PORTE, 0    ; RS = 1 (Data)
    BSF     PORTE, 1    ; E = 1
    NOP
    BCF     PORTE, 1    ; E = 0
    CALL    Delay_Short
    RETURN

Delay_Short:
    MOVLW   d'50'
    MOVWF   Delay_1
Loop_S: DECFSZ Delay_1, F
    GOTO    Loop_S
    RETURN

Delay_Long:
    MOVLW   d'255'
    MOVWF   Delay_1
Loop_L: DECFSZ Delay_1, F
    GOTO    Loop_L
    RETURN

; --- BINARY TO DECIMAL DÖNÜ?ÜM VE YAZDIRMA ---
; W register'daki 0-255 aras? say?y? ekrana basar (3 hane)
BinToDec:
    MOVWF   w_temp      ; Say?y? sakla
    CLRF    BCD_Hundreds
    CLRF    BCD_Tens
    CLRF    BCD_Ones
    
    ; Yüzler Basama??
Calc_100:
    MOVLW   d'100'
    SUBWF   w_temp, W
    BTFSS   STATUS, C
    GOTO    Calc_10
    MOVWF   w_temp
    INCF    BCD_Hundreds, F
    GOTO    Calc_100
    
    ; Onlar Basama??
Calc_10:
    MOVLW   d'10'
    SUBWF   w_temp, W
    BTFSS   STATUS, C
    GOTO    Calc_1
    MOVWF   w_temp
    INCF    BCD_Tens, F
    GOTO    Calc_10
    
    ; Birler Basama??
Calc_1:
    MOVF    w_temp, W
    MOVWF   BCD_Ones
    
    ; Yazd?r (ASCII = Rakam + 0x30)
    MOVF    BCD_Hundreds, W
    ADDLW   0x30
    CALL    Send_Data
    
    MOVF    BCD_Tens, W
    ADDLW   0x30
    CALL    Send_Data
    
    MOVF    BCD_Ones, W
    ADDLW   0x30
    CALL    Send_Data
    RETURN


