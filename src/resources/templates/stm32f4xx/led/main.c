#include "{{DEVICE_HEADER}}"
#include "stm32f4xx_conf.h"

static void delay(volatile uint32_t n)
{
    while (n--) {
        __NOP();
    }
}

void led_init(void)
{
    GPIO_InitTypeDef GPIO_InitStructure;

    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);

    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
}

int main(void)
{
    led_init();
    while (1) {
        GPIO_SetBits(GPIOA, GPIO_Pin_0);
        delay(1000000);
        GPIO_ResetBits(GPIOA, GPIO_Pin_0);
        delay(1000000);
    }
}
