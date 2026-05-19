#include "{{DEVICE_HEADER}}"
#include <stdio.h>


#pragma import(__use_no_semihosting)
              
struct __FILE {
    int handle;
};

FILE __stdout;

void _sys_exit(int x)
{
    x = x;
}


#ifdef __GNUC__
int _write(int file, char *ptr, int len)
{
    for (int i = 0; i < len; i++)
    {
        usart_data_transmit(USART2, (uint8_t)ptr[i]);
        while (RESET == usart_flag_get(USART2, USART_FLAG_TBE));
    }
    return len;
}
#else
int fputc(int ch, FILE *f)
{
    usart_data_transmit(USART2, (uint8_t)ch);
    while (RESET == usart_flag_get(USART2, USART_FLAG_TBE));
    return ch;
}
#endif
