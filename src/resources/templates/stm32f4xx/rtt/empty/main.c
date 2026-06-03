#include "{{DEVICE_HEADER}}"
#include "{{CONF_HEADER}}"
#include "main.h"
#include <rtthread.h>

int main(void)
{
    nvic_config();
    while (1) {
        rt_thread_mdelay(1000);
    }
}
