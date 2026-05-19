#ifndef DEBUG_PRINT_H
#define DEBUG_PRINT_H

#include <stdio.h>
#include <stdarg.h>

#define DEBUG_PRINTF  // 注释掉即关闭所有调试打印

#ifdef DEBUG_PRINTF
static inline void LogPrintf(const char *fmt, ...)
{
    va_list args;
    va_start(args, fmt);
    vprintf(fmt, args);
    va_end(args);
}
#else
static inline void LogPrintf(const char *fmt, ...) { (void)fmt; }
#endif

#endif /* DEBUG_PRINT_H */
