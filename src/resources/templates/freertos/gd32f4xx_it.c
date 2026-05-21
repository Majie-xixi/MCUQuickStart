#include "gd32f4xx_it.h"
#include "main.h"
#include "systick.h"
#include "sysconfig.h"

#if SYSTEM_SUPPORT_OS == 2
#include "FreeRTOS.h"
#include "task.h"
extern void xPortSysTickHandler(void);
#endif

void nvic_config(void)
{
    nvic_priority_group_set(NVIC_PRIGROUP_PRE4_SUB0);
}

void NMI_Handler(void)
{
    while (1) {
    }
}

void HardFault_Handler(void)
{
    while (1) {
    }
}

void MemManage_Handler(void)
{
    while (1) {
    }
}

void BusFault_Handler(void)
{
    while (1) {
    }
}

void UsageFault_Handler(void)
{
    while (1) {
    }
}

void DebugMon_Handler(void)
{
    while (1) {
    }
}

#if SYSTEM_SUPPORT_OS == 2

void SysTick_Handler(void)
{
    if (xTaskGetSchedulerState() != taskSCHEDULER_NOT_STARTED)
    {
        xPortSysTickHandler();
    }
}

#endif
