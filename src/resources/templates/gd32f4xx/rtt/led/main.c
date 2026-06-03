#include "{{DEVICE_HEADER}}"
#include "{{CONF_HEADER}}"
#include "main.h"
#include <rtthread.h>

static struct rt_thread led_thread;
static rt_uint8_t led_thread_stack[512];

static void led_thread_entry(void *parameter)
{
    while (1) {
        /* TODO: toggle your LED pin here */
        rt_thread_mdelay(500);
    }
}

int main(void)
{
    nvic_config();
    /* TODO: initialize LED GPIO here */
    rt_thread_init(&led_thread, "led", led_thread_entry, RT_NULL,
                   led_thread_stack, sizeof(led_thread_stack), 20, 10);
    rt_thread_startup(&led_thread);
    return 0;
}
