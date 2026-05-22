#include "sysconfig.h"

//********************************************************************************
//THUMB指令不支持汇编
//关闭中断时无法响应中断
void WFI_SET(void)
{
    __ASM volatile("wfi");
}

//关闭所有中断
void INTX_DISABLE(void)
{
    __ASM volatile("cpsid i");
}

//开启所有中断
void INTX_ENABLE(void)
{
    __ASM volatile("cpsie i");
}
//设置栈顶地址
//addr:栈顶地址
#if defined(__CC_ARM) || defined(__ICCARM__) || defined(__ARMCC_VERSION)
// ARMCC V5/V6, IAR
__asm void MSR_MSP(uint32_t addr)
{
    MSR MSP, r0
    BX r14
}
#elif defined(__GNUC__)
// GCC
__attribute__((naked)) void MSR_MSP(uint32_t addr)
{
    __asm volatile (
        "MSR MSP, r0\n\t"
        "BX LR"
    );
}
#else
#error "Unsupported compiler"
#endif
