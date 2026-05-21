#include "{{DEVICE_HEADER}}"
#include "{{CONF_HEADER}}"
#include "main.h"
#include "debug_print.h"
#include "FreeRTOS.h"
#include "task.h"
#include <stdio.h>

void uart_init(void)
{
    GPIO_InitTypeDef GPIO_InitStructure;

    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA | RCC_APB2Periph_{{DEBUG_USART}}, ENABLE);

    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_9;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_10;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    USART_InitTypeDef USART_InitStructure;
    USART_InitStructure.USART_BaudRate = 115200;
    USART_InitStructure.USART_WordLength = USART_WordLength_8b;
    USART_InitStructure.USART_StopBits = USART_StopBits_1;
    USART_InitStructure.USART_Parity = USART_Parity_No;
    USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
    USART_InitStructure.USART_Mode = USART_Mode_Tx | USART_Mode_Rx;
    USART_Init({{DEBUG_USART}}, &USART_InitStructure);
    USART_Cmd({{DEBUG_USART}}, ENABLE);
}

int fputc(int ch, FILE *f)
{
    USART_SendData({{DEBUG_USART}}, (uint8_t)ch);
    while (USART_GetFlagStatus({{DEBUG_USART}}, USART_FLAG_TC) == RESET);
    return ch;
}

void uart_task(void *pvParameters)
{
    printf("Hello from FreeRTOS on {{DEVICE_HEADER}}\r\n");
    while (1)
    {
        vTaskDelay(1000);
        printf("tick\r\n");
    }
}

int main(void)
{
    nvic_config();
    uart_init();

    xTaskCreate(uart_task, "uart_task", 256, NULL, 2, NULL);
    vTaskStartScheduler();

    while (1) {
    }
}
