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
//设置栈顶地址（CMSIS内联汇编，GCC/ARMCC/IAR通用）
void MSR_MSP(uint32_t addr)
{
    __ASM volatile("MSR msp, %0" : : "r" (addr));
}
