#include "gd32f4xx_it.h"
#include "main.h"
#include "sysconfig.h"

#if SYSTEM_SUPPORT_OS == 3
#include <rtthread.h>
#include <rthw.h>
#endif

void nvic_config(void)
{
    nvic_priority_group_set(NVIC_PRIGROUP_PRE4_SUB0);
}

void NMI_Handler(void) { while (1) {} }
void HardFault_Handler(void) { while (1) {} }
void MemManage_Handler(void) { while (1) {} }
void BusFault_Handler(void) { while (1) {} }
void UsageFault_Handler(void) { while (1) {} }
void DebugMon_Handler(void) { while (1) {} }

#if SYSTEM_SUPPORT_OS == 3

void SysTick_Handler(void)
{
    rt_interrupt_enter();
    rt_tick_increase();
    rt_interrupt_leave();
}

/*
 * PendSV_Handler and SVC_Handler are implemented in context_rvds.S
 * (assembled from RT-Thread_PORT group). Do NOT redefine here.
 */

#endif
