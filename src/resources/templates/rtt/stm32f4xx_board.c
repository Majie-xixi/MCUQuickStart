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
    GPIO_InitTypeDef GPIO_InitStructure;
    USART_InitTypeDef USART_InitStructure;

    RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_{{DEBUG_USART}}, ENABLE);

    /* TX pin — F4 needs AF config */
    GPIO_PinAFConfig(GPIOA, GPIO_PinSource9, GPIO_AF_{{DEBUG_USART}});
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_9;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF;
    GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_UP;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    /* RX pin */
    GPIO_PinAFConfig(GPIOA, GPIO_PinSource10, GPIO_AF_{{DEBUG_USART}});
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_10;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF;
    GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_UP;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    USART_InitStructure.USART_BaudRate = 115200;
    USART_InitStructure.USART_WordLength = USART_WordLength_8b;
    USART_InitStructure.USART_StopBits = USART_StopBits_1;
    USART_InitStructure.USART_Parity = USART_Parity_No;
    USART_InitStructure.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;
    USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
    USART_Init({{DEBUG_USART}}, &USART_InitStructure);
    USART_Cmd({{DEBUG_USART}}, ENABLE);
}
INIT_BOARD_EXPORT(console_uart_init);

void rt_hw_console_output(const char *str)
{
    rt_size_t i = 0, size = rt_strlen(str);
    for (i = 0; i < size; i++)
    {
        if (*(str + i) == '\n')
        {
            USART_SendData({{DEBUG_USART}}, '\r');
            while (USART_GetFlagStatus({{DEBUG_USART}}, USART_FLAG_TC) == RESET);
        }
        USART_SendData({{DEBUG_USART}}, (uint8_t)*(str + i));
        while (USART_GetFlagStatus({{DEBUG_USART}}, USART_FLAG_TC) == RESET);
    }
}

#ifdef RT_USING_FINSH
char rt_hw_console_getchar(void)
{
    int ch = -1;
    if (USART_GetFlagStatus({{DEBUG_USART}}, USART_FLAG_RXNE) != RESET)
    {
        ch = USART_ReceiveData({{DEBUG_USART}}) & 0xFF;
    }
    else
    {
        rt_thread_mdelay(10);
    }
    return ch;
}
#endif /* RT_USING_FINSH */

#endif /* RT_USING_CONSOLE */
