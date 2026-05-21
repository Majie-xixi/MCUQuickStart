#include "{{DEVICE_HEADER}}"
#include "{{CONF_HEADER}}"
#include "main.h"
#include "systick.h"
#include "FreeRTOS.h"
#include "task.h"

void start_task(void *pvParameters)
{
    while (1)
    {
        vTaskDelay(1000);
    }
}

int main(void)
{
    systick_config();
    nvic_config();

    xTaskCreate(start_task, "start_task", 128, NULL, 1, NULL);
    vTaskStartScheduler();

    while (1) {
    }
}
