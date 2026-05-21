#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H

#include <stdint.h>
#include <stdio.h>
extern uint32_t SystemCoreClock;

#define configASSERT(x) if((x)==0) { printf("FreeRTOS Assert:%s,%d\r\n",__FILE__,__LINE__); while(1); }

/* Hardware configuration */
#define configCPU_CLOCK_HZ                       (SystemCoreClock)
{{SYSTICK_CLOCK_HZ_DEFINE}}

/* Kernel configuration */
#define configUSE_PREEMPTION                     1
#define configUSE_TIME_SLICING                   1
#define configUSE_PORT_OPTIMISED_TASK_SELECTION  1
#define configUSE_TICKLESS_IDLE                  0
#define configUSE_QUEUE_SETS                     1
#define configTICK_RATE_HZ                       (1000)
#define configMAX_PRIORITIES                     (32)
#define configMINIMAL_STACK_SIZE                 ((unsigned short)128)
#define configMAX_TASK_NAME_LEN                  (16)

#define configUSE_16_BIT_TICKS                   0
#define configIDLE_SHOULD_YIELD                  1
#define configUSE_TASK_NOTIFICATIONS             1
#define configUSE_MUTEXES                        1
#define configQUEUE_REGISTRY_SIZE                8
#define configCHECK_FOR_STACK_OVERFLOW           0
#define configUSE_RECURSIVE_MUTEXES              1
#define configUSE_MALLOC_FAILED_HOOK             0
#define configUSE_APPLICATION_TASK_TAG           0
#define configUSE_COUNTING_SEMAPHORES            1

/* Memory allocation */
#define configSUPPORT_DYNAMIC_ALLOCATION         1
#define configTOTAL_HEAP_SIZE                    ((size_t)(15 * 1024))

/* Hook functions */
#define configUSE_IDLE_HOOK                      0
#define configUSE_TICK_HOOK                      0

/* Runtime stats */
#define configGENERATE_RUN_TIME_STATS            0
#define configUSE_TRACE_FACILITY                 1
#define configUSE_STATS_FORMATTING_FUNCTIONS     1

/* Co-routines */
#define configUSE_CO_ROUTINES                    0
#define configMAX_CO_ROUTINE_PRIORITIES          (2)

/* Software timers */
#define configUSE_TIMERS                         1
#define configTIMER_TASK_PRIORITY                (configMAX_PRIORITIES - 1)
#define configTIMER_QUEUE_LENGTH                 5
#define configTIMER_TASK_STACK_DEPTH             (configMINIMAL_STACK_SIZE * 2)

/* Optional API functions */
#define INCLUDE_xTaskGetSchedulerState           1
#define INCLUDE_vTaskPrioritySet                 1
#define INCLUDE_uxTaskPriorityGet                1
#define INCLUDE_vTaskDelete                      1
#define INCLUDE_vTaskCleanUpResources            1
#define INCLUDE_vTaskSuspend                     1
#define INCLUDE_vTaskDelayUntil                  1
#define INCLUDE_vTaskDelay                       1
#define INCLUDE_eTaskGetState                    1
#define INCLUDE_xTimerPendFunctionCall           1
#define INCLUDE_uxTaskGetStackHighWaterMark      1

/* Interrupt priority configuration */
#ifdef __NVIC_PRIO_BITS
    #define configPRIO_BITS                      __NVIC_PRIO_BITS
#else
    #define configPRIO_BITS                      4
#endif

#define configLIBRARY_LOWEST_INTERRUPT_PRIORITY          15
#define configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY     5
#define configKERNEL_INTERRUPT_PRIORITY          (configLIBRARY_LOWEST_INTERRUPT_PRIORITY << (8 - configPRIO_BITS))
#define configMAX_SYSCALL_INTERRUPT_PRIORITY     (configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY << (8 - configPRIO_BITS))

/* Exception handlers mapping */
#define xPortPendSVHandler  PendSV_Handler
#define vPortSVCHandler     SVC_Handler

#endif /* FREERTOS_CONFIG_H */
