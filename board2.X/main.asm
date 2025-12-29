; =================================================================
; DOSYA: main.asm
; PROJE: Board #2 - Curtain Control System
; =================================================================

    LIST P=16F877A
    INCLUDE "P16F877A.INC"

    ; Sigorta Ayarlari: HS Osilator, WDT Kapali
    __CONFIG _FOSC_HS & _WDTE_OFF & _PWRTE_ON & _LVP_OFF & _CP_OFF

    ; Degiskenleri Dahil Et
    INCLUDE "variables.inc"

    ORG 0x00
    GOTO System_Init

    ORG 0x04
    GOTO ISR_Routine

; -----------------------------------------------------------------
; KESME SERVIS RUTINI
; -----------------------------------------------------------------
ISR_Routine:
    ; Context Saving
    MOVWF   w_temp
    SWAPF   STATUS, W
    MOVWF   status_temp

    ; UART Kesmesi Kontrolu
    BANKSEL PIR1
    BTFSC   PIR1, RCIF
    CALL    UART_Receive_Handler

    ; Context Restore
    SWAPF   status_temp, W
    MOVWF   STATUS
    SWAPF   w_temp, F
    SWAPF   w_temp, W
    RETFIE

; -----------------------------------------------------------------
; SISTEM KURULUMU
; -----------------------------------------------------------------
System_Init:
    ; --- Port Ayarlari ---
    BANKSEL TRISA
    MOVLW   b'11111111' ; PORTA Giris (LDR, Pot)
    MOVWF   TRISA
    CLRF    TRISB       ; PORTB Cikis (Step Motor)
    CLRF    TRISD       ; PORTD Cikis (LCD Data)
    CLRF    TRISE       ; PORTE Cikis (LCD Kontrol: RS, EN, RW)
    
    ; UART Pinleri (RC6 TX, RC7 RX)
    BSF     TRISC, 7    ; RX Giris
    BCF     TRISC, 6    ; TX Cikis

    ; ADC Ayarlari (Sola Dayali = Left Justified icin en bastaki bit 0 olmali)
    ; Eski hatali: b'10000010' -> Yeni dogru: b'00000010'
    MOVLW   b'00000010' 
    MOVWF   ADCON1
    
    ; --- RW PININI GND YAPMA (Yazilimsal) ---
    BANKSEL PORTE
    BCF     PORTE, 2    ; RE2 (RW) pinini 0 yap -> Yazma Modu Aktif
    
    ; --- Modulleri Baslat ---
    BANKSEL PORTA
    CALL    LCD_Init
    CALL    UART_Init
    
    ; --- Degisken Sifirlama ---
    CLRF    Current_Curtain
    CLRF    Desired_Curtain
    CLRF    Step_Phase
    CLRF    Current_Steps_L
    CLRF    Current_Steps_H
    
    ; LCD Arayuzunu Ciz
    CALL    LCD_Draw_Interface
    
    ; Kesmeleri Ac
    BANKSEL PIE1
    BSF     PIE1, RCIE
    BANKSEL INTCON
    BSF     INTCON, GIE
    BSF     INTCON, PEIE
; -----------------------------------------------------------------
; ANA DONGU
; -----------------------------------------------------------------
MainLoop:
    ; 1. Sensorleri Oku
    CALL    Read_LDR
    CALL    Read_Pot

    ; 2. Otomatik Kontrol (LDR Esik Kontrolu)
    ; Simülasyon LDR devresi: Karanlik = Yuksek Voltaj (ADC > Esik)
    ; Aydinlik = Dusuk Voltaj (ADC < Esik)
    
    MOVLW   LDR_THRESHOLD   ; Esik degeri (Orn: 50 veya 150 yapabilirsin)
    SUBWF   Light_Value, W  ; W = Light - Threshold
    
    ; Eger Light > Threshold (Karanlik) ise sonuc Pozitif, C=1 olur.
    ; Eger Light < Threshold (Aydinlik) ise sonuc Negatif, C=0 olur.
    
    BTFSC   STATUS, C       ; C=0 ise (Aydinlik) atla, Motor Kontrole git
    GOTO    Force_Close     ; C=1 ise (Karanlik), Zorla Kapat
    GOTO    Control_Motor   ; Aydinlik, normal pot kontrolune git

Force_Close:
    MOVLW   d'100'
    MOVWF   Desired_Curtain
    GOTO    Motor_Manager_Call ; Direkt motor surmeye git (Pot okumayi ez)

Control_Motor:
    ; Potansiyometre degeri zaten Read_Pot ile Desired_Curtain'e yazildi.
    ; Burada ekstra bir islem yapmaya gerek yok.

Motor_Manager_Call:
    ; 3. Motor Yonetimi
    CALL    Motor_Manager

    ; 4. Ekran Guncelleme
    CALL    LCD_Update_Values
    
    GOTO    MainLoop

; -----------------------------------------------------------------
; MODULLERIN DAHIL EDILMESI
; -----------------------------------------------------------------
    INCLUDE "lcd_module.asm"
    INCLUDE "stepmotor.asm"
    INCLUDE "sensors.asm"
    INCLUDE "uart.asm"

    END