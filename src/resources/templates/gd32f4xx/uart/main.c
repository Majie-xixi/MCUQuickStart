#include "{{DEVICE_HEADER}}"
#include "{{CONF_HEADER}}"
#include "main.h"
#include "systick.h"
#include "debug_print.h"
#include <stdio.h>

void uart_init(void)
{
    rcu_periph_clock_enable(RCU_GPIOA);
    rcu_periph_clock_enable(RCU_{{DEBUG_USART}});

    gpio_mode_set(GPIOA, GPIO_MODE_AF, GPIO_PUPD_PULLUP, GPIO_PIN_9);
    gpio_output_options_set(GPIOA, GPIO_OTYPE_PP, GPIO_OSPEED_50MHZ, GPIO_PIN_9);
    gpio_af_set(GPIOA, GPIO_AF_7, GPIO_PIN_9);

    gpio_mode_set(GPIOA, GPIO_MODE_AF, GPIO_PUPD_PULLUP, GPIO_PIN_10);
    gpio_af_set(GPIOA, GPIO_AF_7, GPIO_PIN_10);

    usart_deinit({{DEBUG_USART}});
    usart_baudrate_set({{DEBUG_USART}}, 115200U);
    usart_word_length_set({{DEBUG_USART}}, USART_WL_8BIT);
    usart_stop_bit_set({{DEBUG_USART}}, USART_STB_1BIT);
    usart_parity_config({{DEBUG_USART}}, USART_PM_NONE);
    usart_hardware_flow_rts_config({{DEBUG_USART}}, USART_RTS_DISABLE);
    usart_hardware_flow_cts_config({{DEBUG_USART}}, USART_CTS_DISABLE);
    usart_transmit_config({{DEBUG_USART}}, USART_TRANSMIT_ENABLE);
    usart_receive_config({{DEBUG_USART}}, USART_RECEIVE_ENABLE);
    usart_enable({{DEBUG_USART}});
}

int main(void)
{
    systick_config();
    uart_init();
    printf("Hello from {{DEVICE_HEADER}}\r\n");
    while (1) {
        delay_1ms(1000);
        printf("tick\r\n");
    }
}
