#include "delay.h"
#include "sysconfig.h"

static uint16_t g_fac_us = 72 * 5;

#if SYSTEM_SUPPORT_OS == 2  /* FreeRTOS */
#include "FreeRTOS.h"
#include "task.h"
#endif

#if SYSTEM_SUPPORT_OS == 1  /* UCOS */
#include "includes.h"
static uint16_t g_fac_ms = 0;

#ifdef OS_CRITICAL_METHOD
#define delay_osrunning     OSRunning
#define delay_ostickspersec OS_TICKS_PER_SEC
#define delay_osintnesting  OSIntNesting
#endif

#ifdef CPU_CFG_CRITICAL_METHOD
#define delay_osrunning     OSRunning
#define delay_ostickspersec OSCfg_TickRate_Hz
#define delay_osintnesting  OSIntNestingCtr
#endif

static void delay_osschedlock(void)
{
#ifdef CPU_CFG_CRITICAL_METHOD
    OS_ERR err;
    OSSchedLock(&err);
#else
    OSSchedLock();
#endif
}

static void delay_osschedunlock(void)
{
#ifdef CPU_CFG_CRITICAL_METHOD
    OS_ERR err;
    OSSchedUnlock(&err);
#else
    OSSchedUnlock();
#endif
}

static void delay_ostimedly(uint32_t ticks)
{
#ifdef CPU_CFG_CRITICAL_METHOD
    OS_ERR err;
    OSTimeDly(ticks, OS_OPT_TIME_PERIODIC, &err);
#else
    OSTimeDly(ticks);
#endif
}

void SysTick_Handler(void)
{
    if (delay_osrunning == 1)
    {
        OSIntEnter();
        OSTimeTick();
        OSIntExit();
    }
}
#endif  /* SYSTEM_SUPPORT_OS == 1 */

void delay_init(uint16_t sysclk)
{
    SysTick->CTRL |= (1 << 2);
    g_fac_us = sysclk;

#if SYSTEM_SUPPORT_OS == 2  /* FreeRTOS: use DWT for us delays */
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
#elif SYSTEM_SUPPORT_OS == 1  /* UCOS */
    uint32_t reload;
    reload = sysclk / 8;
    reload *= 1000000 / delay_ostickspersec;
    g_fac_ms = 1000 / delay_ostickspersec;
    SysTick->CTRL |= 1 << 1;
    SysTick->LOAD = reload;
    SysTick->CTRL |= 1 << 0;
#endif
}

#if SYSTEM_SUPPORT_OS == 2  /* FreeRTOS delay implementations */

void delay_us(uint32_t nus)
{
    uint32_t start = DWT->CYCCNT;
    uint32_t ticks = nus * g_fac_us;
    while ((uint32_t)(DWT->CYCCNT - start) < ticks);
}

void delay_ms(uint16_t nms)
{
    if (xTaskGetSchedulerState() != taskSCHEDULER_NOT_STARTED)
    {
        if (nms > 0)
        {
            vTaskDelay(pdMS_TO_TICKS(nms));
        }
    }
    else
    {
        uint32_t i;
        for (i = 0; i < nms; i++)
        {
            delay_us(1000);
        }
    }
}

#elif SYSTEM_SUPPORT_OS == 1  /* UCOS delay implementations */

void delay_us(uint32_t nus)
{
    uint32_t ticks;
    uint32_t told, tnow, tcnt = 0;
    uint32_t reload;
    reload = SysTick->LOAD;
    ticks = nus * g_fac_us;
    delay_osschedlock();
    told = SysTick->VAL;

    while (1)
    {
        tnow = SysTick->VAL;

        if (tnow != told)
        {
            if (tnow < told)
            {
                tcnt += told - tnow;
            }
            else
            {
                tcnt += reload - tnow + told;
            }

            told = tnow;

            if (tcnt >= ticks) break;
        }
    };

    delay_osschedunlock();
}

void delay_ms(uint16_t nms)
{
    if (delay_osrunning && delay_osintnesting == 0)
    {
        if (nms >= g_fac_ms)
        {
            delay_ostimedly(nms / g_fac_ms);
        }

        nms %= g_fac_ms;
    }

    delay_us((uint32_t)(nms * 1000));
}

#else  /* Bare-metal delay implementations */

void delay_us(uint32_t nus)
{
    uint32_t temp;
    SysTick->CTRL = (1 << 2);
    SysTick->LOAD = nus * g_fac_us;
    SysTick->VAL  = 0x00;
    SysTick->CTRL = (1 << 2) | (1 << 0);

    do
    {
        temp = SysTick->CTRL;
    } while ((temp & 0x01) && !(temp & (1 << 16)));

    SysTick->CTRL = (1 << 2);
    SysTick->VAL  = 0x00;
}

void delay_ms(uint16_t nms)
{
    uint32_t repeat = nms / 1000;
    uint32_t remain = nms % 1000;

    while (repeat)
    {
        delay_us(1000 * 1000);
        repeat--;
    }

    if (remain)
    {
        delay_us(remain * 1000);
    }
}
#endif
