#include "{{DEVICE_HEADER}}"
#include "{{CONF_HEADER}}"
#include "main.h"
#include <rtthread.h>

int main(void)
{
    nvic_config();
    rt_kprintf("=== RT-Thread Nano on {{CHIP_FAMILY}} ===\n");
    rt_kprintf("SystemCoreClock: %d Hz\n", SystemCoreClock);
    while (1) {
        rt_kprintf("Hello RT-Thread!\n");
        rt_thread_mdelay(1000);
    }
}
