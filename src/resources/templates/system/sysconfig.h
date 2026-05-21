#ifndef __SYS_H
#define __SYS_H
#include "{{DEVICE_HEADER}}"

// SYSTEM_SUPPORT_OS: 系统文件是否支持 OS
// 0 = 裸机 (默认)
// 1 = UCOSII/UCOSIII
// 2 = FreeRTOS
#define SYSTEM_SUPPORT_OS	{{SYSTEM_SUPPORT_OS}}

/*
支持位带操作, 操作内存的范围是：
0x2000_0000\0x200F_FFFF：SRAM 区中的
0x4000_0000\0x400F_FFFF：片内外设区的最低 1MB。
 实现思路参考<<CM3权威指南>>第5章(87页~92页). M4同M3类似。
*/
//IO口操作宏定义
#define BITBAND(addr, bitnum) ((addr & 0xF0000000)+0x2000000+((addr &0xFFFFF)<<5)+(bitnum<<2))
#define MEM_ADDR(addr)  *((volatile unsigned long  *)(addr))
#define BIT_ADDR(addr, bitnum)   MEM_ADDR(BITBAND(addr, bitnum))
//IO口地址映射
#define GPIOA_ODR_Addr    (GPIOA+12) //0X4001080C=0x40010000U+0x00000800U+C
#define GPIOB_ODR_Addr    (GPIOB+12) //0X40010C0C =0x40010000U+0x00000800U+400
#define GPIOC_ODR_Addr    (GPIOC+12) //0x4001 100C
#define GPIOD_ODR_Addr    (GPIOD+12) //0x4001 140C
#define GPIOE_ODR_Addr    (GPIOE+12) //0x4001 180C
#define GPIOF_ODR_Addr    (GPIOF+12) //0x4001 1C0C
#define GPIOG_ODR_Addr    (GPIOG+12) //0x4001 200C

#define GPIOA_IDR_Addr    (GPIOA+8) //0X4001 0808
#define GPIOB_IDR_Addr    (GPIOB+8) //0X4001 0C08
#define GPIOC_IDR_Addr    (GPIOC+8) //0x4001 1008
#define GPIOD_IDR_Addr    (GPIOD+8) //0x4001 1408
#define GPIOE_IDR_Addr    (GPIOE+8) //0x4001 1408
#define GPIOF_IDR_Addr    (GPIOF+8) //0x4001 1C08
#define GPIOG_IDR_Addr    (GPIOG+8) //0x4001 2008

//IO口操作, 只对单个IO口!
//确保n的值小于16!
#define PAout(n)   BIT_ADDR(GPIOA_ODR_Addr,n)  //输出
#define PAin(n)    BIT_ADDR(GPIOA_IDR_Addr,n)  //输入

#define PBout(n)   BIT_ADDR(GPIOB_ODR_Addr,n)  //输出
#define PBin(n)    BIT_ADDR(GPIOB_IDR_Addr,n)  //输入

#define PCout(n)   BIT_ADDR(GPIOC_ODR_Addr,n)  //输出
#define PCin(n)    BIT_ADDR(GPIOC_IDR_Addr,n)  //输入

#define PDout(n)   BIT_ADDR(GPIOD_ODR_Addr,n)  //输出
#define PDin(n)    BIT_ADDR(GPIOD_IDR_Addr,n)  //输入

#define PEout(n)   BIT_ADDR(GPIOE_ODR_Addr,n)  //输出
#define PEin(n)    BIT_ADDR(GPIOE_IDR_Addr,n)  //输入

#define PFout(n)   BIT_ADDR(GPIOF_ODR_Addr,n)  //输出
#define PFin(n)    BIT_ADDR(GPIOF_IDR_Addr,n)  //输入

#define PGout(n)   BIT_ADDR(GPIOG_ODR_Addr,n)  //输出
#define PGin(n)    BIT_ADDR(GPIOG_IDR_Addr,n)  //输入

//以下为汇编函数
void WFI_SET(void);		//执行WFI指令
void INTX_DISABLE(void);//关闭所有中断
void INTX_ENABLE(void);	//开启所有中断
void MSR_MSP(uint32_t addr);	//设置堆栈地址

#endif
