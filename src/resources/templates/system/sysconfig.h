#ifndef __SYS_H
#define __SYS_H	
#include "{{DEVICE_HEADER}}"
//////////////////////////////////////////////////////////////////////////////////	 
//������ֻ��ѧϰʹ�ã�δ���������ɣ��������������κ���;
//ALIENTEK STM32������		   
//����ԭ��@ALIENTEK
//������̳:www.openedv.com
//�޸�����:2012/8/18
//�汾��V1.7
//��Ȩ���У�����ؾ���
//Copyright(C) �������������ӿƼ����޹�˾ 2009-2019
//All rights reserved
////////////////////////////////////////////////////////////////////////////////// 	 

//0,��֧��ucos
//1,֧��ucos
#define SYSTEM_SUPPORT_OS		0		//����ϵͳ�ļ����Ƿ�֧��UCOS
																	    
	 
/*
֧��λ�������������ڴ����ķ�Χ�ǣ�
0x2000_0000�\0x200F_FFFF��SRAM ���е�
0x4000_0000�\0x400F_FFFF��Ƭ���������е���� 1MB��
 ����ʵ��˼��,�ο�<<CM3Ȩ��ָ��>>������(87ҳ~92ҳ).M4ͬM3����,ֻ�ǼĴ�����ַ����.
*/	
//IO�ڲ����궨��
#define BITBAND(addr, bitnum) ((addr & 0xF0000000)+0x2000000+((addr &0xFFFFF)<<5)+(bitnum<<2)) 
#define MEM_ADDR(addr)  *((volatile unsigned long  *)(addr)) 
#define BIT_ADDR(addr, bitnum)   MEM_ADDR(BITBAND(addr, bitnum)) 
//IO�ڵ�ַӳ��
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

//IO�ڲ���,ֻ�Ե�һ��IO��!
//ȷ��n��ֵС��16!
#define PAout(n)   BIT_ADDR(GPIOA_ODR_Addr,n)  //��� 
#define PAin(n)    BIT_ADDR(GPIOA_IDR_Addr,n)  //���� 

#define PBout(n)   BIT_ADDR(GPIOB_ODR_Addr,n)  //��� 
#define PBin(n)    BIT_ADDR(GPIOB_IDR_Addr,n)  //���� 

#define PCout(n)   BIT_ADDR(GPIOC_ODR_Addr,n)  //��� 
#define PCin(n)    BIT_ADDR(GPIOC_IDR_Addr,n)  //���� 

#define PDout(n)   BIT_ADDR(GPIOD_ODR_Addr,n)  //��� 
#define PDin(n)    BIT_ADDR(GPIOD_IDR_Addr,n)  //���� 

#define PEout(n)   BIT_ADDR(GPIOE_ODR_Addr,n)  //��� 
#define PEin(n)    BIT_ADDR(GPIOE_IDR_Addr,n)  //����

#define PFout(n)   BIT_ADDR(GPIOF_ODR_Addr,n)  //��� 
#define PFin(n)    BIT_ADDR(GPIOF_IDR_Addr,n)  //����

#define PGout(n)   BIT_ADDR(GPIOG_ODR_Addr,n)  //��� 
#define PGin(n)    BIT_ADDR(GPIOG_IDR_Addr,n)  //����

//����Ϊ��ຯ��
void WFI_SET(void);		//ִ��WFIָ��
void INTX_DISABLE(void);//�ر������ж�
void INTX_ENABLE(void);	//���������ж�
void MSR_MSP(uint32_t addr);	//���ö�ջ��ַ

#endif
