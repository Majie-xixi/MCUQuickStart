#include <rthw.h>
#include <rtthread.h>
#include "{{DEVICE_HEADER}}"
#include "main.h"

#if defined(RT_USING_USER_MAIN) && defined(RT_USING_HEAP)
#define RT_HEAP_SIZE (15 * 1024)
static rt_uint8_t rt_heap[RT_HEAP_SIZE];

RT_WEAK void *rt_heap_begin_get(void)
{
    return rt_heap;
}

RT_WEAK void *rt_heap_end_get(void)
{
    return rt_heap + RT_HEAP_SIZE;
}
#endif

void rt_hw_board_init(void)
{
    SystemCoreClockUpdate();
    SysTick_Config(SystemCoreClock / RT_TICK_PER_SECOND);

#ifdef RT_USING_COMPONENTS_INIT
    rt_components_board_init();
#endif

#if defined(RT_USING_USER_MAIN) && defined(RT_USING_HEAP)
    rt_system_heap_init(rt_heap_begin_get(), rt_heap_end_get());
#endif
}

#ifdef RT_USING_CONSOLE

static void console_uart_init(void)
{
    rcu_periph_clock_enable(RCU_GPIOA);
    rcu_periph_clock_enable(RCU_{{DEBUG_USART}});

    /* TX pin */
    gpio_init(GPIOA, GPIO_MODE_AF_PP, GPIO_OSPEED_50MHZ, GPIO_PIN_9);
    /* RX pin */
    gpio_init(GPIOA, GPIO_MODE_IN_FLOATING, GPIO_OSPEED_50MHZ, GPIO_PIN_10);

    usart_deinit({{DEBUG_USART}});
    usart_baudrate_set({{DEBUG_USART}}, 115200U);
    usart_word_length_set({{DEBUG_USART}}, USART_WL_8BIT);
    usart_stop_bit_set({{DEBUG_USART}}, USART_STB_1BIT);
    usart_parity_config({{DEBUG_USART}}, USART_PM_NONE);
    usart_hardware_flow_rts_config({{DEBUG_USART}}, USART_RTS_DISABLE);
    usart_hardware_flow_cts_config({{DEBUG_USART}}, USART_CTS_DISABLE);
    usart_receive_config({{DEBUG_USART}}, USART_RECEIVE_ENABLE);
    usart_transmit_config({{DEBUG_USART}}, USART_TRANSMIT_ENABLE);
    usart_enable({{DEBUG_USART}});
}
INIT_BOARD_EXPORT(console_uart_init);

void rt_hw_console_output(const char *str)
{
    rt_size_t i = 0, size = rt_strlen(str);
    for (i = 0; i < size; i++)
    {
        if (*(str + i) == '\n')
        {
            usart_data_transmit({{DEBUG_USART}}, '\r');
            while (usart_flag_get({{DEBUG_USART}}, USART_FLAG_TBE) == RESET);
        }
        usart_data_transmit({{DEBUG_USART}}, (uint8_t)*(str + i));
        while (usart_flag_get({{DEBUG_USART}}, USART_FLAG_TBE) == RESET);
    }
}

#ifdef RT_USING_FINSH
char rt_hw_console_getchar(void)
{
    int ch = -1;
    if (usart_flag_get({{DEBUG_USART}}, USART_FLAG_RBNE) != RESET)
    {
        ch = usart_data_receive({{DEBUG_USART}}) & 0xFF;
    }
    else
    {
        rt_thread_mdelay(10);
    }
    return ch;
}
#endif /* RT_USING_FINSH */

#endif /* RT_USING_CONSOLE */
