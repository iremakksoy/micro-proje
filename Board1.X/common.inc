;============================================================
; common.inc
; Target  : PIC16F877A
; Project : Temperature System (Term Project)
;
; Bu dosya:
;  - Konfig bitlerini (tek yerde) tanimlar
;  - Tum moduller icin ortak sabitleri (MODE_*, NO_KEY, vb.)
;  - sys_flags bit anlamlarini
;  - RAM'deki global degiskenleri (CBLOCK 0x20) toplar
;
; Not:
;  - CBLOCK degiskenleri tum .asm modullerinde ortak kullanilir.
;  - BANKSEL kullanimi ile dogru bank secimi kritik.
;============================================================

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

; sys_flags bitleri (bit=1 iken isaretli/durum aktif):
F_DO_ADC        EQU     0 ; F_DO_ADC      : 1 saniyelik zamanlayici ADC okumasi istiyor (main loop okur)
F_DISP_DIRTY    EQU     1 ; F_DISP_DIRTY  : Ekran icerigi degisti -> Display_Rebuild cagirilacak
F_UART_GOT_FR   EQU     2 ; F_UART_GOT_FR : UART tarafindan yeni fraction (ondalik) geldi
F_UART_GOT_IN   EQU     3 ; F_UART_GOT_IN : UART tarafindan yeni integer geldi
   
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
; desired_int/frac  : kullanici hedefi (xx.x)
; ambient_int/frac  : LM35'ten okunan ortam (xx.x)
; fan_rps           : 1 saniyede TMR0 sayimi (yaklasik rps)

tick100ms
sec_counter
disp_mode
error_timer
sys_flags
; tick100ms   : Timer1 ile 100ms sayaci (0..9)
; sec_counter : display mode rotasyonu icin (2 saniyede bir)
; disp_mode   : 0=desired,1=ambient,2=fan
; error_timer : 0 degilse Display "EROR"
; sys_flags   : bayraklar

disp_idx
disp0
disp1
disp2
disp3
; disp_idx : multiplex sira (0..3)
; disp0..3 : RD portuna basilan segment pattern'leri

key_last
key_ready
key_lock
entry_state
in_d1
in_d2
in_frac
; key_last   : son kabul edilen tus (ASCII)
; key_ready  : 1 ise main loop Keypad_Process yapar
; key_lock   : debounce (1 tus/press)
; entry_state: A XX*X# state machine
; in_d1/in_d2/in_frac : girilen rakamlar (binary 0..9)

uart_new_int
uart_new_frac
; uart_new_int/frac : UART'tan gelen yeni hedef deger (xx.x)
; tmp0..tmp3        : ortak scratch register'lar

tmp0
tmp1
tmp2
tmp3
        ENDC

ENDIF