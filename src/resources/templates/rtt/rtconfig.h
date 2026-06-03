/* RT-Thread Nano config file */

#ifndef __RTTHREAD_CFG_H__
#define __RTTHREAD_CFG_H__

/* ARMCC V5 C90 compatibility: enables standard C library headers in rtdef.h */
#define RT_USING_LIBC

/* Basic Configuration */
#define RT_THREAD_PRIORITY_MAX       32
#define RT_TICK_PER_SECOND           1000
#define RT_ALIGN_SIZE                4
#define RT_NAME_MAX                  8

#define RT_USING_COMPONENTS_INIT
#define RT_USING_USER_MAIN
#define RT_MAIN_THREAD_STACK_SIZE    1024

/* Debug Configuration */
#define RT_DEBUG_INIT                0

/* IPC Configuration */
#define RT_USING_SEMAPHORE
#define RT_USING_MUTEX
#define RT_USING_EVENT
#define RT_USING_MAILBOX
#define RT_USING_MESSAGEQUEUE

/* Memory Management */
#define RT_USING_HEAP
#define RT_USING_SMALL_MEM

/* Software Timer */
#define RT_USING_TIMER_SOFT
#define RT_TIMER_THREAD_PRIO         4
#define RT_TIMER_THREAD_STACK_SIZE   512

/* Console Configuration */
#define RT_USING_CONSOLE
#define RT_CONSOLEBUF_SIZE           128

/*
 * FinSH Shell — disabled by default due to ARMCC V5 C90 limitations.
 * MSH_CMD_EXPORT macros with multi-word descriptions are not C90 compatible.
 * Enable only if using ARMCC V6 or GCC.
 */
/* #define RT_USING_FINSH */

#endif /* __RTTHREAD_CFG_H__ */
