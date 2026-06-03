#include "stm32f4xx_it.h"
#include "main.h"
#include "sysconfig.h"

#if SYSTEM_SUPPORT_OS == 3
#include <rtthread.h>
#include <rthw.h>
#endif

void nvic_config(void)
{
    NVIC_PriorityGroupConfig(NVIC_PriorityGroup_4);
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

void PendSV_Handler(void)
{
    rt_hw_context_switch_interrupt();
}

void SVC_Handler(void)
{
    rt_hw_context_switch_to();
}

#endif
