#include "{{DEVICE_HEADER}}"
#include "{{CONF_HEADER}}"
#include "main.h"
#include "FreeRTOS.h"
#include "task.h"

void led_init(void)
{
    GPIO_InitTypeDef GPIO_InitStructure;
    RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_OUT;
    GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_UP;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
}

void led_task(void *pvParameters)
{
    while (1)
    {
        GPIO_SetBits(GPIOA, GPIO_Pin_0);
        vTaskDelay(500);
        GPIO_ResetBits(GPIOA, GPIO_Pin_0);
        vTaskDelay(500);
    }
}

int main(void)
{
    nvic_config();
    led_init();

    xTaskCreate(led_task, "led_task", 128, NULL, 2, NULL);
    vTaskStartScheduler();

    while (1) {
    }
}
