#include "{{DEVICE_HEADER}}"
#include "{{CONF_HEADER}}"
#include "main.h"
#include <rtthread.h>

static void led_thread_entry(void *parameter)
{
    while (1)
    {
        /* TODO: toggle your LED pin here */
        rt_thread_mdelay(500);
    }
}

int led_init(void)
{
    /* TODO: initialize LED GPIO here */
    return 0;
}
INIT_APP_EXPORT(led_init);

int main(void)
{
    nvic_config();

    rt_thread_t tid = rt_thread_create(
        "led", led_thread_entry, RT_NULL, 512, 20, 10);
    if (tid != RT_NULL)
        rt_thread_startup(tid);

    return 0;
}
