IFNDEF COMMON_INC_LOADED
COMMON_INC_LOADED   EQU     1

        LIST    P=16F877A
        #include <P16F877A.INC>

;------------ Config (SADECE 1 KERE) ------------
        __CONFIG _WDT_OFF & _PWRTE_ON & _CP_OFF & _LVP_OFF & _BODEN_OFF & _HS_OSC

;------------ Constants ------------
MODE_DESIRED    EQU     0
MODE_AMBIENT    EQU     1
MODE_FAN        EQU     2

NO_KEY          EQU     0xFF

; sys_flags bits
F_DO_ADC        EQU     0
F_DISP_DIRTY    EQU     1
F_UART_GOT_FR   EQU     2
F_UART_GOT_IN   EQU     3

; keypad entry_state
ENT_IDLE        EQU     0
ENT_D1          EQU     1
ENT_D2          EQU     2
ENT_STAR        EQU     3
ENT_FRAC        EQU     4
ENT_HASH        EQU     5

;------------ RAM ------------
        CBLOCK  0x20
W_TEMP
STATUS_TEMP
PCLATH_TEMP

desired_int
desired_frac
ambient_int
ambient_frac
fan_rps

tick100ms
sec_counter
disp_mode
error_timer
sys_flags

disp_idx
disp0
disp1
disp2
disp3

key_last
key_ready
key_lock
entry_state
in_d1
in_d2
in_frac

uart_new_int
uart_new_frac

tmp0
tmp1
tmp2
tmp3
        ENDC

ENDIF