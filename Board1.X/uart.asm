;========================
; uart.asm
;========================
        #include "common.inc"

UART_Init:
        ; 9600 @ 4MHz, BRGH=1 => SPBRG=25  (20MHz ise 129)
        BANKSEL SPBRG
        MOVLW   .25
        MOVWF   SPBRG

        BANKSEL TXSTA
        MOVLW   b'00100100'     ; BRGH=1, TXEN=1
        MOVWF   TXSTA

        BANKSEL RCSTA
        MOVLW   b'10010000'     ; SPEN=1, CREN=1
        MOVWF   RCSTA
        RETURN

UART_Service:
        BANKSEL RCSTA
        BTFSC   RCSTA, OERR
        GOTO    UART_CLR_OERR

        BANKSEL PIR1
        BTFSS   PIR1, RCIF
        RETURN

        BANKSEL RCREG
        MOVF    RCREG, W
        CALL    UART_ProcessByte
        RETURN

UART_CLR_OERR:
        BANKSEL RCSTA
        BCF     RCSTA, CREN
        BSF     RCSTA, CREN
        RETURN


UART_ProcessByte:
        BANKSEL tmp0
        MOVWF   tmp0

        ; GET
        MOVF    tmp0, W
        XORLW   0x01
        BTFSC   STATUS, Z
        GOTO    UART_TX_DES_FR

        MOVF    tmp0, W
        XORLW   0x02
        BTFSC   STATUS, Z
        GOTO    UART_TX_DES_IN

        MOVF    tmp0, W
        XORLW   0x03
        BTFSC   STATUS, Z
        GOTO    UART_TX_AMB_FR

        MOVF    tmp0, W
        XORLW   0x04
        BTFSC   STATUS, Z
        GOTO    UART_TX_AMB_IN

        MOVF    tmp0, W
        XORLW   0x05
        BTFSC   STATUS, Z
        GOTO    UART_TX_FAN

        ; SET? bit7=1
        BTFSS   tmp0, 7
        RETURN

        ; payload (0..63)
        MOVF    tmp0, W
        ANDLW   b'00111111'
        BANKSEL tmp1
        MOVWF   tmp1

        ; bit6=1 -> INT, bit6=0 -> FRAC
        BTFSC   tmp0, 6
        GOTO    UART_SET_INT

UART_SET_FRAC:
        BANKSEL tmp1
        MOVF    tmp1, W
        BANKSEL uart_new_frac
        MOVWF   uart_new_frac

        BANKSEL sys_flags
        BSF     sys_flags, F_UART_GOT_FR
        CALL    UART_TRY_COMMIT
        RETURN

UART_SET_INT:
        BANKSEL tmp1
        MOVF    tmp1, W
        BANKSEL uart_new_int
        MOVWF   uart_new_int

        BANKSEL sys_flags
        BSF     sys_flags, F_UART_GOT_IN
        CALL    UART_TRY_COMMIT
        RETURN


UART_TRY_COMMIT:
        BANKSEL sys_flags
        BTFSS   sys_flags, F_UART_GOT_FR
        RETURN
        BTFSS   sys_flags, F_UART_GOT_IN
        RETURN

        ; consume pair
        BCF     sys_flags, F_UART_GOT_FR
        BCF     sys_flags, F_UART_GOT_IN

        ; frac <= 9 ?
        BANKSEL uart_new_frac
        MOVLW   .10
        SUBWF   uart_new_frac, W
        BTFSC   STATUS, C
        GOTO    UART_INVALID

        ; int >= 10 ?
        BANKSEL uart_new_int
        MOVLW   .10
        SUBWF   uart_new_int, W
        BTFSS   STATUS, C
        GOTO    UART_INVALID

        ; int < 50 OR (int==50 and frac==0)
        MOVLW   .50
        SUBWF   uart_new_int, W
        BTFSC   STATUS, C
        GOTO    UART_CHECK50X
        GOTO    UART_ACCEPT

UART_CHECK50X:
        ; int > 50 ?
        BANKSEL uart_new_int
        MOVF    uart_new_int, W
        XORLW   .50
        BTFSS   STATUS, Z
        GOTO    UART_INVALID

        ; int==50 => frac must be 0
        BANKSEL uart_new_frac
        MOVF    uart_new_frac, F
        BTFSS   STATUS, Z
        GOTO    UART_INVALID

UART_ACCEPT:
        BANKSEL uart_new_int
        MOVF    uart_new_int, W
        BANKSEL desired_int
        MOVWF   desired_int

        BANKSEL uart_new_frac
        MOVF    uart_new_frac, W
        BANKSEL desired_frac
        MOVWF   desired_frac

        BANKSEL sys_flags
        BSF     sys_flags, F_DISP_DIRTY
        RETURN

UART_INVALID:
        BANKSEL error_timer
        MOVLW   .2
        MOVWF   error_timer
        BANKSEL sys_flags
        BSF     sys_flags, F_DISP_DIRTY
        RETURN


UART_SendByte:
UART_TX_WAIT:
        BANKSEL PIR1
        BTFSS   PIR1, TXIF
        GOTO    UART_TX_WAIT
        BANKSEL TXREG
        MOVWF   TXREG
        RETURN

UART_TX_DES_FR:
        BANKSEL desired_frac
        MOVF    desired_frac, W
        CALL    UART_SendByte
        RETURN
UART_TX_DES_IN:
        BANKSEL desired_int
        MOVF    desired_int, W
        CALL    UART_SendByte
        RETURN
UART_TX_AMB_FR:
        BANKSEL ambient_frac
        MOVF    ambient_frac, W
        CALL    UART_SendByte
        RETURN
UART_TX_AMB_IN:
        BANKSEL ambient_int
        MOVF    ambient_int, W
        CALL    UART_SendByte
        RETURN
UART_TX_FAN:
        BANKSEL fan_rps
        MOVF    fan_rps, W
        CALL    UART_SendByte
        RETURN
