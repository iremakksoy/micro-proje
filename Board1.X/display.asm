;============================================================
; display.asm
; 4-digit 7-seg multiplex gosterim
;
; Buffer:
;  disp0..disp3 = her hanenin segment pattern'i (RD0..RD7)
;  Bit7 genelde "dp" (decimal point) icin kullanilir.
;
; Display_Service:
;  - her cagrisinda tek bir digit yakar (disp_idx 0..3)
;  - hizli cagri -> stabil goruntu
;
; Display_Rebuild:
;  - error_timer !=0 ise "EROR"
;  - degilse disp_mode'a gore:
;     MODE_DESIRED:  xx.xC
;     MODE_AMBIENT:  xx.xA
;     MODE_FAN    :  xxxF
;============================================================

        #include "common.inc"

; Multiplex gecisi:
;  once tum digit enable kapatilir (ghosting engellemek icin),
;  sonra segment pattern RD'ye basilir,
;  en son ilgili digit enable acilir.


Display_Service:
        ; digits off
        BANKSEL PORTC
        BCF     PORTC,0
        BCF     PORTC,1
        BCF     PORTC,2
        BCF     PORTC,3

        ; W = disp byte
        BANKSEL disp_idx
        MOVF    disp_idx, W
        CALL    Display_GetByte

        BANKSEL PORTD
        MOVWF   PORTD

        ; enable digit
        BANKSEL disp_idx
        MOVF    disp_idx, W
        CALL    Display_EnableDigit

        ; next digit
        BANKSEL disp_idx
        INCF    disp_idx, F
        MOVLW   .4
        SUBWF   disp_idx, W
        BTFSS   STATUS, Z
        RETURN
        CLRF    disp_idx
        RETURN


; W=0..3 -> returns disp0..disp3 in W
Display_GetByte:
        MOVWF   tmp0
        MOVF    tmp0, F
        BTFSC   STATUS, Z
        GOTO    DGB0
        MOVLW   .1
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        GOTO    DGB1
        MOVLW   .2
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        GOTO    DGB2
        ; else 3
        GOTO    DGB3

DGB0:
        BANKSEL disp0
        MOVF    disp0, W
        RETURN
DGB1:
        BANKSEL disp1
        MOVF    disp1, W
        RETURN
DGB2:
        BANKSEL disp2
        MOVF    disp2, W
        RETURN
DGB3:
        BANKSEL disp3
        MOVF    disp3, W
        RETURN


; W=0..3 -> enable RC0..RC3
Display_EnableDigit:
        MOVWF   tmp0
        MOVF    tmp0, F
        BTFSC   STATUS, Z
        GOTO    ED0
        MOVLW   .1
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        GOTO    ED1
        MOVLW   .2
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        GOTO    ED2
        GOTO    ED3

ED0:
        BANKSEL PORTC
        BSF     PORTC,0
        RETURN
ED1:
        BANKSEL PORTC
        BSF     PORTC,1
        RETURN
ED2:
        BANKSEL PORTC
        BSF     PORTC,2
        RETURN
ED3:
        BANKSEL PORTC
        BSF     PORTC,3
        RETURN


Display_Rebuild:
        BANKSEL error_timer
        MOVF    error_timer, F
        BTFSC   STATUS, Z
        GOTO    NO_ERROR

        ; EROR
        BANKSEL disp0
        MOVLW   0x79        ; E
        MOVWF   disp0
        MOVLW   0x50        ; r approx
        MOVWF   disp1
        MOVLW   0x3F        ; O
        MOVWF   disp2
        MOVLW   0x50        ; r
        MOVWF   disp3
        RETURN

NO_ERROR:
        BANKSEL disp_mode
        MOVF    disp_mode, W
        BTFSC   STATUS, Z
        GOTO    BUILD_DES

        MOVLW   MODE_AMBIENT
        SUBWF   disp_mode, W
        BTFSC   STATUS, Z
        GOTO    BUILD_AMB

        GOTO    BUILD_FAN

BUILD_DES:
        CALL    BuildTempDesired
        RETURN
BUILD_AMB:
        CALL    BuildTempAmbient
        RETURN
BUILD_FAN:
        CALL    BuildFan
        RETURN


BuildTempDesired:
        BANKSEL desired_int
        MOVF    desired_int, W
        CALL    BinTo2Digits

        MOVF    tmp0, W
        CALL    DigitToSeg
        BANKSEL disp0
        MOVWF   disp0

        MOVF    tmp1, W
        CALL    DigitToSeg
        IORLW   0x80               ; dp ON
        BANKSEL disp1
        MOVWF   disp1

        BANKSEL desired_frac
        MOVF    desired_frac, W
        CALL    DigitToSeg
        BANKSEL disp2
        MOVWF   disp2

        MOVLW   0x39               ; C
        BANKSEL disp3
        MOVWF   disp3
        RETURN


BuildTempAmbient:
        BANKSEL ambient_int
        MOVF    ambient_int, W
        CALL    BinTo2Digits

        MOVF    tmp0, W
        CALL    DigitToSeg
        BANKSEL disp0
        MOVWF   disp0

        MOVF    tmp1, W
        CALL    DigitToSeg
        IORLW   0x80               ; dp ON
        BANKSEL disp1
        MOVWF   disp1

        BANKSEL ambient_frac
        MOVF    ambient_frac, W
        CALL    DigitToSeg
        BANKSEL disp2
        MOVWF   disp2

        MOVLW   0x77               ; A
        BANKSEL disp3
        MOVWF   disp3
        RETURN


BuildFan:
        BANKSEL fan_rps
        MOVF    fan_rps, W
        CALL    BinTo3Digits

        MOVF    tmp0, W
        CALL    DigitToSeg
        BANKSEL disp0
        MOVWF   disp0

        MOVF    tmp1, W
        CALL    DigitToSeg
        BANKSEL disp1
        MOVWF   disp1

        MOVF    tmp2, W
        CALL    DigitToSeg
        BANKSEL disp2
        MOVWF   disp2

        MOVLW   0x71               ; F
        BANKSEL disp3
        MOVWF   disp3
        RETURN


; W=0..99 -> tmp0 tens, tmp1 ones
BinTo2Digits:
        MOVWF   tmp2
        CLRF    tmp0
B2_LOOP:
        MOVLW   .10
        SUBWF   tmp2, W
        BTFSS   STATUS, C
        GOTO    B2_DONE
        MOVLW   .10
        SUBWF   tmp2, F
        INCF    tmp0, F
        GOTO    B2_LOOP
B2_DONE:
        MOVF    tmp2, W
        MOVWF   tmp1
        RETURN


; W=0..255 -> tmp0 hundreds, tmp1 tens, tmp2 ones
BinTo3Digits:
        MOVWF   tmp3
        CLRF    tmp0
        CLRF    tmp1
B3_H:
        MOVLW   .100
        SUBWF   tmp3, W
        BTFSS   STATUS, C
        GOTO    B3_T
        MOVLW   .100
        SUBWF   tmp3, F
        INCF    tmp0, F
        GOTO    B3_H
B3_T:
        MOVLW   .10
        SUBWF   tmp3, W
        BTFSS   STATUS, C
        GOTO    B3_DONE
        MOVLW   .10
        SUBWF   tmp3, F
        INCF    tmp1, F
        GOTO    B3_T
B3_DONE:
        MOVF    tmp3, W
        MOVWF   tmp2
        RETURN


; DigitToSeg:
; IN : W = 0..9
; OUT: W = 7-seg pattern (common cathode varsayimi)
; Not: Donen pattern'lerin dp biti (bit7) burada kapali gelir,
;dp istendigi yerde IORLW 0x80 ile acilir.

DigitToSeg:
        BANKSEL tmp0
        MOVWF   tmp0

        MOVF    tmp0, F
        BTFSC   STATUS, Z
        RETLW   0x3F    ;0

        MOVLW   .1
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   0x06    ;1

        MOVLW   .2
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   0x5B    ;2

        MOVLW   .3
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   0x4F    ;3

        MOVLW   .4
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   0x66    ;4

        MOVLW   .5
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   0x6D    ;5

        MOVLW   .6
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   0x7D    ;6

        MOVLW   .7
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   0x07    ;7

        MOVLW   .8
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   0x7F    ;8

        MOVLW   .9
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   0x6F    ;9

        RETLW   0x00    ; invalid -> blank
