; =================================================================
; DOSYA: stepmotor.asm
; AÇIKLAMA: Step Motor Surucusu (PORTB) - Gecikmeli ve Oranli
; =================================================================

Motor_Manager:
    ; Hedef ve Mevcut Perde Durumunu Karsilastir
    MOVF    Desired_Curtain, W
    SUBWF   Current_Curtain, W
    BTFSC   STATUS, Z
    RETURN              ; Esitse islem yapma, cik.

    ; Esit Degilse Yon Belirle
    ; Carry=0 ise (Current < Desired) -> Sonuc Negatif -> Perdeyi KAPAT (Arttir)
    ; Carry=1 ise (Current > Desired) -> Sonuc Pozitif -> Perdeyi AC (Azalt)
    
    BTFSS   STATUS, C   ; C=0 ise atlama yapma (Kapatmaya git)
    GOTO    Move_Close
    
Move_Open:
    ; Perde Aciliyor (Yuzde azalmali)
    ; %1 degisim icin 10 adim atmamiz gerekiyor (1000 adim = %100)
    CALL    Step_10_Times_CW
    DECF    Current_Curtain, F  ; Perde yuzdesini 1 azalt
    RETURN

Move_Close:
    ; Perde Kapaniyor (Yuzde artmali)
    CALL    Step_10_Times_CCW
    INCF    Current_Curtain, F  ; Perde yuzdesini 1 arttir
    RETURN

; --- 10 ADIM ATMA ALT PROGRAMLARI ---
Step_10_Times_CW:
    MOVLW   d'10'
    MOVWF   Math_Temp_L ; Sayac olarak kullanalim
Loop_CW:
    CALL    Step_One_CW
    DECFSZ  Math_Temp_L, F
    GOTO    Loop_CW
    RETURN

Step_10_Times_CCW:
    MOVLW   d'10'
    MOVWF   Math_Temp_L
Loop_CCW:
    CALL    Step_One_CCW
    DECFSZ  Math_Temp_L, F
    GOTO    Loop_CCW
    RETURN

; --- TEK ADIM RUTINLERI ---
Step_One_CW:
    INCF    Step_Phase, F
    MOVLW   b'00000011'
    ANDWF   Step_Phase, F ; 0-3 arasinda tut (Modulo 4)
    CALL    Activate_Coils
    CALL    Delay_Motor_Safe ; Yavaslatilmis gecikme
    RETURN

Step_One_CCW:
    DECF    Step_Phase, F
    MOVLW   b'00000011'
    ANDWF   Step_Phase, F
    CALL    Activate_Coils
    CALL    Delay_Motor_Safe
    RETURN

Activate_Coils:
    MOVF    Step_Phase, W
    CALL    Step_Table
    BANKSEL PORTB
    MOVWF   PORTB
    RETURN

Step_Table:
    ADDWF   PCL, F
    RETLW   b'00000001' ; Adim 1 (RB0)
    RETLW   b'00000010' ; Adim 2 (RB1)
    RETLW   b'00000100' ; Adim 3 (RB2)
    RETLW   b'00001000' ; Adim 4 (RB3)

; --- GECIKME (MOTORUN DONMESI ICIN KRITIK) ---
Delay_Motor_Safe:
    ; Yaklasik 3-5ms gecikme saglayalim.
    ; Icerideki dongu 255 tur, disaridaki 15 tur.
    MOVLW   d'15'
    MOVWF   Delay_2
Out_Loop:
    MOVLW   d'255'
    MOVWF   Delay_1
In_Loop:
    DECFSZ  Delay_1, F
    GOTO    In_Loop
    DECFSZ  Delay_2, F
    GOTO    Out_Loop
    RETURN