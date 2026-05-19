#include "{{DEVICE_HEADER}}"
#include "main.h"
#include "systick.h"

void led_init(void)
{
    rcu_periph_clock_enable(RCU_GPIOA);
    gpio_mode_set(GPIOA, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, GPIO_PIN_0);
    gpio_output_options_set(GPIOA, GPIO_OTYPE_PP, GPIO_OSPEED_50MHZ, GPIO_PIN_0);
}

int main(void)
{
    systick_config();
    led_init();
    while (1) {
        gpio_bit_set(GPIOA, GPIO_PIN_0);
        delay_1ms(500);
        gpio_bit_reset(GPIOA, GPIO_PIN_0);
        delay_1ms(500);
    }
}
