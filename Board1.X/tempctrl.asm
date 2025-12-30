;============================================================
; tempctrl.asm
; Bu modul:
;  - Timer1 ile 100ms tick uretir (ISR)
;  - 1 saniyede bir:
;      * fan_rps gunceller (TMR0 external counter)
;      * error_timer countdown
;      * display mode rotasyonu (2 saniyede bir)
;      * main loop icin F_DO_ADC flag set eder
;  - Temp_ReadAmbient: LM35 (AN0) ADC okur -> ambient_int/frac (xx.x)
;  - Temp_ControlUpdate: desired vs ambient karsilastirir -> RE0/RE1 surer
;============================================================

        #include "common.inc"

;------------------------------------------------------------
; Reload Timer1 for 100ms tick
; NOTE: This preload (0xCF2C) is correct for Fosc=4MHz, presc=1:8
; Timer tick = (Fosc/4)/8 = 125kHz => 8us
; 100ms / 8us = 12500 counts => preload = 65536-12500 = 0xCF2C
; Not: Fosc farkliysa preload tekrar hesaplanmalidir.
;------------------------------------------------------------
Temp_TMR1_Reload:
        BANKSEL TMR1H
        MOVLW   0xCF
        MOVWF   TMR1H
        MOVLW   0x2C
        MOVWF   TMR1L
        RETURN

;------------------------------------------------------------
; Girdiler : yok (ISR context)
; Ciktilar :
;  - tick100ms (0..9)
;  - fan_rps (1 saniyelik TMR0 sayimi)
;  - error_timer azalir (0 degilse)
;  - disp_mode 2 saniyede bir 0->1->2->0 (error yoksa)
;  - sys_flags: F_DO_ADC ve F_DISP_DIRTY set edilir
; Clobber : W/STATUS (ISR zaten save/restore yapiyor)
;------------------------------------------------------------
Temp_TMR1_ISR:
        BANKSEL PIR1
        BCF     PIR1, TMR1IF
        CALL    Temp_TMR1_Reload

        BANKSEL tick100ms
        INCF    tick100ms, F
        MOVLW   .10
        SUBWF   tick100ms, W
        BTFSS   STATUS, Z
        RETURN

        ; 1 second reached
        CLRF    tick100ms

        ; fan rps = TMR0 pulses in 1s
        BANKSEL TMR0
        MOVF    TMR0, W
        BANKSEL fan_rps
        MOVWF   fan_rps
        BANKSEL TMR0
        CLRF    TMR0

        ; error timer countdown
        BANKSEL error_timer
        MOVF    error_timer, F
        BTFSC   STATUS, Z
        GOTO    _no_err_dec
        DECF    error_timer, F
        BANKSEL sys_flags
        BSF     sys_flags, F_DISP_DIRTY
_no_err_dec:

        ; display mode change every 2 seconds (if not showing error)
        BANKSEL sec_counter
        INCF    sec_counter, F
        MOVLW   .2
        SUBWF   sec_counter, W
        BTFSS   STATUS, Z
        GOTO    _sec_done

        CLRF    sec_counter

        ; if error active, do not rotate
        BANKSEL error_timer
        MOVF    error_timer, F
        BTFSS   STATUS, Z
        GOTO    _sec_done

        BANKSEL disp_mode
        INCF    disp_mode, F
        MOVLW   .3
        SUBWF   disp_mode, W
        BTFSS   STATUS, Z
        GOTO    _mode_ok
        CLRF    disp_mode
_mode_ok:
        BANKSEL sys_flags
        BSF     sys_flags, F_DISP_DIRTY

_sec_done:
        ; request ADC update each second
        BANKSEL sys_flags
        BSF     sys_flags, F_DO_ADC
        BSF     sys_flags, F_DISP_DIRTY
        RETURN

;------------------------------------------------------------
; LM35: 10mV/°C.
; ADC LSB (5V ref, 10-bit) ~ 4.887mV.
; 1°C icin ~2.046 ADC count eder.
; Burada tam bolme yerine hizli yaklasim:
;  temp_x10 ? adc * (4 + 1/2 + 1/4 + 1/8 + 1/128)
; Bu carpani bit kaydirma + toplama ile elde ediyoruz.
; Sonra /10 ile (int, frac) ayiriyoruz:
;  ambient_int = temp_x10 / 10
;  ambient_frac = temp_x10 % 10   (0..9)
;------------------------------------------------------------
Temp_ReadAmbient:
        ; acquisition delay (~ küçük bekleme)
        BANKSEL tmp0
        MOVLW   .20
        MOVWF   tmp0
_acq:
        NOP
        DECFSZ  tmp0, F
        GOTO    _acq

        ; start ADC
        BANKSEL ADCON0
        BSF     ADCON0, GO_DONE
_wait_adc:
        BTFSC   ADCON0, GO_DONE
        GOTO    _wait_adc

        ; read 10-bit right-justified: ADRESH:ADRESL -> tmp1:tmp0
        BANKSEL ADRESL
        MOVF    ADRESL, W
        BANKSEL tmp0
        MOVWF   tmp0            ; adcL

        BANKSEL ADRESH
        MOVF    ADRESH, W
        BANKSEL tmp1
        MOVWF   tmp1            ; adcH

        ; accumulator tmp3:tmp2 = adc << 2  (LOGICAL shift, carry cleared each step)
        BANKSEL tmp2
        MOVF    tmp0, W
        MOVWF   tmp2            ; accL
        MOVF    tmp1, W
        MOVWF   tmp3            ; accH

        BCF     STATUS, C
        RLF     tmp2, F
        RLF     tmp3, F
        BCF     STATUS, C
        RLF     tmp2, F
        RLF     tmp3, F

        ; scratch = adc (ambient_frac:ambient_int used as scratch pair)
        BANKSEL ambient_int
        MOVF    tmp0, W
        MOVWF   ambient_int     ; scratch L
        MOVF    tmp1, W
        MOVWF   ambient_frac    ; scratch H

        ; add adc>>1
        BCF     STATUS, C
        RRF     ambient_frac, F
        RRF     ambient_int, F
        CALL    _ADD_ACC

        ; add adc>>2  (shift one more, clear C!)
        BCF     STATUS, C
        RRF     ambient_frac, F
        RRF     ambient_int, F
        CALL    _ADD_ACC

        ; add adc>>3  (shift one more, clear C!)
        BCF     STATUS, C
        RRF     ambient_frac, F
        RRF     ambient_int, F
        CALL    _ADD_ACC

        ; add adc>>7 (rebuild scratch=adc then shift 7 times logically)
        BANKSEL ambient_int
        MOVF    tmp0, W
        MOVWF   ambient_int
        MOVF    tmp1, W
        MOVWF   ambient_frac

        MOVLW   .7
        BANKSEL tmp0
        MOVWF   tmp0
_sh7:
        BCF     STATUS, C
        BANKSEL ambient_int
        RRF     ambient_frac, F
        RRF     ambient_int, F
        BANKSEL tmp0
        DECFSZ  tmp0, F
        GOTO    _sh7
        CALL    _ADD_ACC

; _div10:
;  tmp3:tmp2  -> kalan (temp_x10)
;  tmp1       -> bolum (ambient_int)
; Her adimda 10 cikartip bolumu artiriyoruz (kucuk sayilar icin yeterli).

        BANKSEL tmp1
        CLRF    tmp1         ; quotient
_div10:
        ; if tmp3:tmp2 < 10 stop
        BANKSEL tmp3
        MOVF    tmp3, W
        BTFSS   STATUS, Z
        GOTO    _ge10
        MOVLW   .10
        BANKSEL tmp2
        SUBWF   tmp2, W
        BTFSS   STATUS, C
        GOTO    _div_done
_ge10:
        ; subtract 10 from tmp3:tmp2
        MOVLW   .10
        BANKSEL tmp2
        SUBWF   tmp2, F
        BTFSS   STATUS, C
        BANKSEL tmp3
        BTFSS   STATUS, C
        DECF    tmp3, F
        BANKSEL tmp1
        INCF    tmp1, F
        GOTO    _div10

_div_done:
        BANKSEL ambient_int
        MOVF    tmp1, W
        MOVWF   ambient_int
        BANKSEL tmp2
        MOVF    tmp2, W
        BANKSEL ambient_frac
        MOVWF   ambient_frac

        BANKSEL sys_flags
        BSF     sys_flags, F_DISP_DIRTY
        RETURN

; helper: acc(tmp3:tmp2) += scratch(ambient_frac:ambient_int)
_ADD_ACC:
        BANKSEL ambient_int
        MOVF    ambient_int, W
        BANKSEL tmp2
        ADDWF   tmp2, F
        BTFSC   STATUS, C
        INCF    tmp3, F
        BANKSEL ambient_frac
        MOVF    ambient_frac, W
        BANKSEL tmp3
        ADDWF   tmp3, F
        RETURN

;------------------------------------------------------------
; Temp_ControlUpdate
; Amaç:
;  desired (hedef) ile ambient (ortam) karsilastirilir.
;  - hedef > ortam  => Heater ON, Cooler OFF
;  - hedef < ortam  => Cooler ON, Heater OFF
;  - esit / cok yakin => ikisi de OFF (veya kodun yaptigi durum)
; Not:
;  Karsilastirma once integer, sonra fraction ile yapilir.
;------------------------------------------------------------
Temp_ControlUpdate:
        ; compare desired vs ambient using int then frac
        BANKSEL desired_int
        MOVF    ambient_int, W
        SUBWF   desired_int, W     ; W = desired_int - ambient_int
        BTFSS   STATUS, Z
        GOTO    _int_diff

        ; int equal -> compare frac
        BANKSEL desired_frac
        MOVF    ambient_frac, W
        SUBWF   desired_frac, W
        BTFSS   STATUS, Z
        GOTO    _frac_diff

        ; equal -> both off
        BANKSEL PORTE
        BCF     PORTE, 0
        BCF     PORTE, 1
        RETURN

_int_diff:
        ; if desired - ambient >= 0 => desired > ambient
        BTFSS   STATUS, C
        GOTO    _desired_lt
        GOTO    _desired_gt

_frac_diff:
        BTFSS   STATUS, C
        GOTO    _desired_lt
        GOTO    _desired_gt

_desired_gt:
        ; desired > ambient -> HEATER ON, COOLER OFF
        BANKSEL PORTE
        BSF     PORTE, 0
        BCF     PORTE, 1
        RETURN

_desired_lt:
        ; desired < ambient -> HEATER OFF, COOLER ON
        BANKSEL PORTE
        BCF     PORTE, 0
        BSF     PORTE, 1
        RETURN

