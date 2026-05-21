#include "{{DEVICE_HEADER}}"
#include "{{CONF_HEADER}}"
#include "main.h"
#include "FreeRTOS.h"
#include "task.h"

void led_init(void)
{
    rcu_periph_clock_enable(RCU_GPIOA);
    gpio_mode_set(GPIOA, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, GPIO_PIN_0);
    gpio_output_options_set(GPIOA, GPIO_OTYPE_PP, GPIO_OSPEED_50MHZ, GPIO_PIN_0);
}

void led_task(void *pvParameters)
{
    while (1)
    {
        gpio_bit_set(GPIOA, GPIO_PIN_0);
        vTaskDelay(500);
        gpio_bit_reset(GPIOA, GPIO_PIN_0);
        vTaskDelay(500);
    }
}

int main(void)
{
    systick_config();
    nvic_config();
    led_init();

    xTaskCreate(led_task, "led_task", 128, NULL, 2, NULL);
    vTaskStartScheduler();

    while (1) {
    }
}
