#ifndef __DELAY_H
#define __DELAY_H 			   

#include "{{DEVICE_HEADER}}"

/* Compatibility for old CMSIS (e.g. STM32F10x SPL v1.30 lacks DWT_Type struct) */
#if !defined(DWT)
typedef struct {
    volatile uint32_t CTRL;
    volatile uint32_t CYCCNT;
    volatile uint32_t CPICNT;
    volatile uint32_t EXCCNT;
    volatile uint32_t SLEEPCNT;
    volatile uint32_t LSUCNT;
    volatile uint32_t FOLDCNT;
    volatile uint32_t PCSR;
} DWT_Type;
#define DWT_BASE  0xE0001000UL
#define DWT       ((DWT_Type *) DWT_BASE)
#ifndef DWT_CTRL_CYCCNTENA_Msk
#define DWT_CTRL_CYCCNTENA_Msk  (1UL << 0)
#endif
#endif

void delay_init(uint16_t sysclk);   /* ��ʼ���ӳٺ��� */
void delay_ms(uint16_t nms);        /* ��ʱnms */
void delay_us(uint32_t nus);        /* ��ʱnus */

#endif





























