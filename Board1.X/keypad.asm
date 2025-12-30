;========================
; keypad.asm (REWRITE - stable)
; PIC16F877A - 4x4 keypad
; Rows: RB4..RB7 (inputs with pull-ups)
; Cols: RB0..RB3 (outputs)
; Layout:
;   1 2 3 A
;   4 5 6 B
;   7 8 9 C
;   * 0 # D
;
; Giri? Formati:  A  X  X  *  X  #
; Uygun aralik: 10.0 .. 50.0   (50.x INVALID)
; Invalid -> error_timer -> Display "EROR"
; Keypad tarama prensibi:
;  - RB0..RB3 kolon output: tek tek LOW yapilir (aktif kolon)
;  - RB4..RB7 satir input + pull-up: basilan tus satiri LOW okutur
;  - row/col -> index (0..15) -> ASCII map
;
; Debounce:
;  key_lock=1 iken yeni tusa izin verilmez.
;  Tus birakilinca (NO_KEY) key_lock temizlenir.
;========================
        #include "common.inc"

;------------------------------------------------------------
; Optional RB-change ISR handler
; (RBIE kapal?ysa zaten ça?r?lmaz, sorun de?il)
;------------------------------------------------------------
Keypad_RB_ISR:
        BANKSEL PORTB
        MOVF    PORTB, W          ; clear mismatch
        BANKSEL INTCON
        BCF     INTCON, RBIF
        RETURN

;------------------------------------------------------------
; IN : yok
; OUT:
;   key_ready=1 ise main loop Keypad_Process yapmali
;   key_last  = kabul edilen tus (ASCII)
;------------------------------------------------------------
Keypad_Poll:
        ; if a key is already pending, do nothing
        BANKSEL key_ready
        MOVF    key_ready, F
        BTFSS   STATUS, Z
        RETURN

        CALL    Keypad_Scan        ; W = ASCII or NO_KEY
        BANKSEL tmp0
        MOVWF   tmp0

        ; NO_KEY ?
        MOVF    tmp0, W
        XORLW   NO_KEY
        BTFSC   STATUS, Z
        GOTO    _kp_rel

        ; pressed -> if locked ignore
        BANKSEL key_lock
        MOVF    key_lock, F
        BTFSS   STATUS, Z
        RETURN

        ; accept new key
        MOVLW   0x01
        MOVWF   key_lock

        BANKSEL key_last
        MOVF    tmp0, W
        MOVWF   key_last

        BANKSEL key_ready
        MOVLW   0x01
        MOVWF   key_ready
        RETURN

_kp_rel:
        ; released -> unlock
        BANKSEL key_lock
        CLRF    key_lock
        RETURN

;------------------------------------------------------------
; Keypad_Scan
; Returns W = ASCII key, or NO_KEY (0xFF)
; Leaves idle with ALL columns LOW (RB0..RB3=0)
;------------------------------------------------------------
Keypad_Scan:
        ; COL0 low (RB0=0, RB1..RB3=1) => 1110b = 0x0E
        BANKSEL PORTB
        MOVLW   0x0E
        MOVWF   PORTB
        CALL    _ReadRow
        BTFSS   STATUS, Z
        GOTO    _c0

        ; COL1 low => 1101b = 0x0D
        MOVLW   0x0D
        MOVWF   PORTB
        CALL    _ReadRow
        BTFSS   STATUS, Z
        GOTO    _c1

        ; COL2 low => 1011b = 0x0B
        MOVLW   0x0B
        MOVWF   PORTB
        CALL    _ReadRow
        BTFSS   STATUS, Z
        GOTO    _c2

        ; COL3 low => 0111b = 0x07
        MOVLW   0x07
        MOVWF   PORTB
        CALL    _ReadRow
        BTFSS   STATUS, Z
        GOTO    _c3

        ; none
        BANKSEL PORTB
        CLRF    PORTB              ; idle = columns LOW
        MOVLW   NO_KEY
        RETURN

_c0:
        MOVF    tmp1, W
        CALL    _RowMul4
        ; +0
        CALL    _KeyMap
        GOTO    _scan_done
_c1:
        MOVF    tmp1, W
        CALL    _RowMul4
        ADDLW   .1
        CALL    _KeyMap
        GOTO    _scan_done
_c2:
        MOVF    tmp1, W
        CALL    _RowMul4
        ADDLW   .2
        CALL    _KeyMap
        GOTO    _scan_done
_c3:
        MOVF    tmp1, W
        CALL    _RowMul4
        ADDLW   .3
        CALL    _KeyMap
        GOTO    _scan_done

_scan_done:
        BANKSEL tmp2
        MOVWF   tmp2               ; save ASCII
        BANKSEL PORTB
        CLRF    PORTB              ; idle = columns LOW
        BANKSEL tmp2
        MOVF    tmp2, W
        RETURN

;------------------------------------------------------------
; _ReadRow
; OUT:
;   - NO press: returns with Z=1
;   - press   : tmp1 = row index (0..3), returns with Z=0
;------------------------------------------------------------
_ReadRow:
        NOP
        NOP
        BANKSEL PORTB
        MOVF    PORTB, W
        ANDLW   0xF0
        XORLW   0xF0
        BTFSC   STATUS, Z
        RETURN                    ; Z=1 (no press)

        ; find which row is LOW
        BANKSEL PORTB
        BTFSS   PORTB, 4
        GOTO    _r0
        BTFSS   PORTB, 5
        GOTO    _r1
        BTFSS   PORTB, 6
        GOTO    _r2
        ; else row3
        BANKSEL tmp1
        MOVLW   .3
        MOVWF   tmp1
        GOTO    _pressed
_r0:
        BANKSEL tmp1
        CLRF    tmp1
        GOTO    _pressed
_r1:
        BANKSEL tmp1
        MOVLW   .1
        MOVWF   tmp1
        GOTO    _pressed
_r2:
        BANKSEL tmp1
        MOVLW   .2
        MOVWF   tmp1
_pressed:
        ; force Z=0 before returning (W don't care)
        MOVLW   0x01
        IORLW   0x00
        RETURN

; W=row -> W=row*4
_RowMul4:
        BANKSEL tmp2
        MOVWF   tmp2
        BCF     STATUS, C
        RLF     tmp2, F
        BCF     STATUS, C
        RLF     tmp2, F
        MOVF    tmp2, W
        RETURN

;------------------------------------------------------------
; _KeyMap (no jump-table -> PCLATH safe)
; IN:  W=index 0..15
; OUT: W=ASCII
;------------------------------------------------------------
_KeyMap:
        BANKSEL tmp0
        MOVWF   tmp0

        MOVLW   .0
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   '1'
        MOVLW   .1
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   '2'
        MOVLW   .2
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   '3'
        MOVLW   .3
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   'A'

        MOVLW   .4
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   '4'
        MOVLW   .5
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   '5'
        MOVLW   .6
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   '6'
        MOVLW   .7
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   'B'

        MOVLW   .8
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   '7'
        MOVLW   .9
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   '8'
        MOVLW   .10
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   '9'
        MOVLW   .11
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   'C'

        MOVLW   .12
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   '*'
        MOVLW   .13
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   '0'
        MOVLW   .14
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   '#'
        MOVLW   .15
        XORWF   tmp0, W
        BTFSC   STATUS, Z
        RETLW   'D'

        RETLW   NO_KEY

;------------------------------------------------------------
; Keypad_Process (A XX*X #)
;------------------------------------------------------------
Keypad_Process:
        BANKSEL key_last
        MOVF    key_last, W

        ; 'A' always starts entry
        XORLW   'A'
        BTFSC   STATUS, Z
        GOTO    _start_entry

        ; if idle -> ignore
        BANKSEL entry_state
        MOVF    entry_state, F
        BTFSC   STATUS, Z
        RETURN

        ; dispatch by entry_state
        MOVF    entry_state, W
        XORLW   .1
        BTFSC   STATUS, Z
        GOTO    _digit1

        MOVF    entry_state, W
        XORLW   .2
        BTFSC   STATUS, Z
        GOTO    _digit2

        MOVF    entry_state, W
        XORLW   .3
        BTFSC   STATUS, Z
        GOTO    _expect_star

        MOVF    entry_state, W
        XORLW   .4
        BTFSC   STATUS, Z
        GOTO    _frac

        MOVF    entry_state, W
        XORLW   .5
        BTFSC   STATUS, Z
        GOTO    _expect_hash

        RETURN

_start_entry:
        BANKSEL entry_state
        MOVLW   .1
        MOVWF   entry_state
        BANKSEL in_d1
        CLRF    in_d1
        CLRF    in_d2
        CLRF    in_frac
        RETURN

_digit1:
        BANKSEL key_last
        MOVF    key_last, W
        CALL    _AsciiDigitToBin
        BTFSC   STATUS, C
        RETURN
        BANKSEL in_d1
        MOVWF   in_d1
        BANKSEL entry_state
        MOVLW   .2
        MOVWF   entry_state
        RETURN

_digit2:
        BANKSEL key_last
        MOVF    key_last, W
        CALL    _AsciiDigitToBin
        BTFSC   STATUS, C
        RETURN
        BANKSEL in_d2
        MOVWF   in_d2
        BANKSEL entry_state
        MOVLW   .3
        MOVWF   entry_state
        RETURN

_expect_star:
        BANKSEL key_last
        MOVF    key_last, W
        XORLW   '*'
        BTFSS   STATUS, Z
        RETURN
        BANKSEL entry_state
        MOVLW   .4
        MOVWF   entry_state
        RETURN

_frac:
        BANKSEL key_last
        MOVF    key_last, W
        CALL    _AsciiDigitToBin
        BTFSC   STATUS, C
        RETURN
        BANKSEL in_frac
        MOVWF   in_frac
        BANKSEL entry_state
        MOVLW   .5
        MOVWF   entry_state
        RETURN

_expect_hash:
        BANKSEL key_last
        MOVF    key_last, W
        XORLW   '#'
        BTFSS   STATUS, Z
        RETURN

        CALL    _CommitDesiredIfValid

        BANKSEL entry_state
        CLRF    entry_state
        RETURN

;------------------------------------------------------------
; _AsciiDigitToBin
; IN:  W=ASCII
; OUT: W=0..9, C=0 ok / C=1 bad
;------------------------------------------------------------
_AsciiDigitToBin:
        BANKSEL tmp0
        MOVWF   tmp0

        MOVLW   '0'
        SUBWF   tmp0, W            ; W = tmp0 - '0'
        BTFSS   STATUS, C
        GOTO    _bad_digit
        MOVLW   '9'+1
        SUBWF   tmp0, W            ; W = tmp0 - ('9'+1)
        BTFSC   STATUS, C
        GOTO    _bad_digit

        BANKSEL tmp0
        MOVF    tmp0, W
        ADDLW   -'0'
        BCF     STATUS, C
        RETURN

_bad_digit:
        BSF     STATUS, C
        RETURN

;------------------------------------------------------------
; _CommitDesiredIfValid
; int = 10*in_d1 + in_d2
; frac = in_frac
; valid: 10.0 .. 50.0 (50.x invalid)
; Kabul edilirse:
;  desired_int/desired_frac yazilir,
;  disp_mode = MODE_DESIRED yapilip hemen gosterilir,
;  Display_Rebuild icin F_DISP_DIRTY set edilir,
;  Temp_ControlUpdate cagrilir (cikislar aninda guncellensin diye).
;------------------------------------------------------------
_CommitDesiredIfValid:

        ; tmp0 = 10*in_d1 + in_d2
        ; tmp0 = (in_d1*8) + (in_d1*2) + in_d2
        BANKSEL in_d1
        MOVF    in_d1, W
        MOVWF   tmp1            ; tmp1 = d1

        ; tmp2 = d1*8
        MOVF    tmp1, W
        MOVWF   tmp2
        BCF     STATUS, C
        RLF     tmp2, F         ; *2
        BCF     STATUS, C
        RLF     tmp2, F         ; *4
        BCF     STATUS, C
        RLF     tmp2, F         ; *8

        ; tmp0 = d1*2
        MOVF    tmp1, W
        MOVWF   tmp0
        BCF     STATUS, C
        RLF     tmp0, F         ; *2

        ; tmp0 = d1*10
        MOVF    tmp2, W
        ADDWF   tmp0, F

        ; tmp0 = d1*10 + d2
        BANKSEL in_d2
        MOVF    in_d2, W
        ADDWF   tmp0, F

        ; ----- Range checks -----
        ; int >= 10 ?
        MOVLW   .10
        SUBWF   tmp0, W          ; W = int - 10
        BTFSS   STATUS, C
        GOTO    _kp_invalid

        ; int <= 50 ?  (invalid if int >= 51)
        MOVLW   .51
        SUBWF   tmp0, W          ; W = int - 51
        BTFSC   STATUS, C
        GOTO    _kp_invalid

        ; if int==50 then frac must be 0
        MOVF    tmp0, W
        XORLW   .50
        BTFSS   STATUS, Z
        GOTO    _kp_accept
        BANKSEL in_frac
        MOVF    in_frac, F
        BTFSS   STATUS, Z
        GOTO    _kp_invalid

_kp_accept:
        BANKSEL desired_int
        MOVF    tmp0, W
        MOVWF   desired_int

        BANKSEL in_frac
        MOVF    in_frac, W
        BANKSEL desired_frac
        MOVWF   desired_frac

        ; show desired immediately
        BANKSEL disp_mode
        MOVLW   MODE_DESIRED
        MOVWF   disp_mode
        BANKSEL disp_idx
        CLRF    disp_idx

        BANKSEL sys_flags
        BSF     sys_flags, F_DISP_DIRTY

        CALL    Temp_ControlUpdate
        RETURN

_kp_invalid:
        BANKSEL error_timer
        MOVLW   .2               ; 2 seconds
        MOVWF   error_timer
        BANKSEL sys_flags
        BSF     sys_flags, F_DISP_DIRTY
        RETURN
