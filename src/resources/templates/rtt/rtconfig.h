/* RT-Thread Nano config file — matches official stm32f407-msh example */

#ifndef __RTTHREAD_CFG_H__
#define __RTTHREAD_CFG_H__

/* ARMCC V5 compatibility: enables standard C library headers in rtdef.h */
#define RT_USING_LIBC

/* Basic Configuration */
#define RT_THREAD_PRIORITY_MAX       32
#define RT_TICK_PER_SECOND           1000
#define RT_ALIGN_SIZE                4
#define RT_NAME_MAX                  8

#define RT_USING_COMPONENTS_INIT
#define RT_USING_USER_MAIN
#define RT_MAIN_THREAD_STACK_SIZE    1024

/* Debug */
#define RT_DEBUG_INIT                0

/* IPC */
#define RT_USING_SEMAPHORE
/* #define RT_USING_MUTEX */
/* #define RT_USING_EVENT */
#define RT_USING_MAILBOX
/* #define RT_USING_MESSAGEQUEUE */

/* Memory Management — heap disabled (matches official example).
   User threads use static stacks via rt_thread_init(). */
/* #define RT_USING_HEAP */
/* #define RT_USING_SMALL_MEM */

/* Software Timer — disabled (matches official example) */
/* #define RT_USING_TIMER_SOFT */

/* Console */
#define RT_USING_CONSOLE
#define RT_CONSOLEBUF_SIZE           128

/* FinSH — disabled (ARMCC V5 C90 incompatible) */
/* #define RT_USING_FINSH */

#endif /* __RTTHREAD_CFG_H__ */
