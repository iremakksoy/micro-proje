;========================
; main.asm
;========================
        LIST    P=16F877A
        #include <P16F877A.INC>
        #include "common.inc"

        ORG     0x0000
        GOTO    Init

ORG     0x0004
ISR:
        MOVWF   W_TEMP
        SWAPF   STATUS, W
        MOVWF   STATUS_TEMP
        MOVF    PCLATH, W
        MOVWF   PCLATH_TEMP

        ; --- FORCE BANK0 for correct SFR access (PIR1/INTCON etc.) ---
        BCF     STATUS, RP0
        BCF     STATUS, RP1

        ; Timer1 interrupt?
        BANKSEL PIR1
        BTFSC   PIR1, TMR1IF
        CALL    Temp_TMR1_ISR

        ; PORTB change interrupt (optional)
        BANKSEL INTCON
        BTFSC   INTCON, RBIF
        CALL    Keypad_RB_ISR

        MOVF    PCLATH_TEMP, W
        MOVWF   PCLATH
        SWAPF   STATUS_TEMP, W
        MOVWF   STATUS
        SWAPF   W_TEMP, F
        SWAPF   W_TEMP, W
        RETFIE

;------------------------------------------------------------
Init:
        ; --- Ports default ---
        BANKSEL PORTA
        CLRF    PORTA
        CLRF    PORTB
        CLRF    PORTC
        CLRF    PORTD
        CLRF    PORTE

        ; RA0=AN0 input, RA4=T0CKI input
        BANKSEL TRISA
        MOVLW   b'00010001'
        MOVWF   TRISA

        ; Keypad: RB7..RB4 input, RB3..RB0 output
        MOVLW   b'11110000'
        MOVWF   TRISB

        ; 7seg digits on RC0..RC3 output, UART RX on RC7 input
        MOVLW   b'10000000'
        MOVWF   TRISC

        ; 7seg segments on PORTD output
        CLRF    TRISD

        ; Heater/Cooler on RE0/RE1 output
        CLRF    TRISE

	; ADC: sadece AN0 analog, geri kalan dijital (RE0/RE1 dijital kalmal?!)
	BANKSEL ADCON1
	MOVLW   0x8E        ; ADFM=1, PCFG=1110 -> AN0 analog, Vref=Vdd/Vss
	MOVWF   ADCON1

	; ADC clock: FRC (simde en sorunsuz)
	BANKSEL ADCON0
	MOVLW   0xC1        ; ADCS=11 (FRC), CH0, ADON=1
	MOVWF   ADCON0


        ; OPTION_REG: enable RB pullups, TMR0 external on RA4, no prescaler
        BANKSEL OPTION_REG
        MOVLW   0x68        ; RBPU=0 INTEDG=1 T0CS=1 T0SE=0 PSA=1
        MOVWF   OPTION_REG

        ; --- Keypad idle: columns LOW (RB0..RB3=0) + mismatch clear ---
        BANKSEL PORTB
        CLRF    PORTB
        MOVF    PORTB, W            ; clear mismatch

        ; Timer1: internal clock, presc 1:8, enable
        BANKSEL T1CON
        MOVLW   0x31
        MOVWF   T1CON

        ; preload TMR1 for 100ms @ Fosc=4MHz, presc=8 => 0xCF2C
        CALL    Temp_TMR1_Reload

        ; enable Timer1 interrupt
        BANKSEL PIR1
        BCF     PIR1, TMR1IF
        BANKSEL PIE1
        BSF     PIE1, TMR1IE

        ; keypad: we POLL in main loop -> RBIE OFF
        BANKSEL INTCON
        BCF     INTCON, RBIF
        BCF     INTCON, RBIE
        BSF     INTCON, PEIE
        BSF     INTCON, GIE

        ; init variables
        BANKSEL desired_int
        MOVLW   .25
        MOVWF   desired_int
        CLRF    desired_frac

        CLRF    ambient_int
        CLRF    ambient_frac
        CLRF    fan_rps

        CLRF    tick100ms
        CLRF    sec_counter
        CLRF    sys_flags

        MOVLW   MODE_DESIRED
        MOVWF   disp_mode
        CLRF    disp_idx
        CLRF    error_timer

        CLRF    key_ready
        CLRF    key_lock
        CLRF    entry_state

        ; init modules
        CALL    Display_Rebuild
        CALL    UART_Init
        CALL    Temp_ControlUpdate

MainLoop:
        ; display refresh (multiplex)
        CALL    Display_Service

        ; UART service (non-blocking)
        CALL    UART_Service

        ; keypad poll
        CALL    Keypad_Poll

        ; keypad event?
        BANKSEL key_ready
        MOVF    key_ready, F
        BTFSC   STATUS, Z
        GOTO    _no_key
        CLRF    key_ready
        CALL    Keypad_Process
_no_key:

        ; periodic ADC read requested?
        BANKSEL sys_flags
        BTFSS   sys_flags, F_DO_ADC
        GOTO    _no_adc
        BCF     sys_flags, F_DO_ADC
        CALL    Temp_ReadAmbient
        CALL    Temp_ControlUpdate
_no_adc:

        ; display dirty?
        BANKSEL sys_flags
        BTFSS   sys_flags, F_DISP_DIRTY
        GOTO    _no_disp
        BCF     sys_flags, F_DISP_DIRTY
        CALL    Display_Rebuild
_no_disp:

        GOTO    MainLoop



;========================
; Include code blocks
; (Bu dosyalar "Exclude from Build" olmal?)
;========================
        #include "tempctrl.asm"
        #include "keypad.asm"
        #include "display.asm"
        #include "uart.asm"

        END
