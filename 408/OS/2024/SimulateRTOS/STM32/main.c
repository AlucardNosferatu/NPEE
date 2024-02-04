/*
*************************************************************************
*                             包含的头文件
*************************************************************************
*/
#include "stm32f10x.h"
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"        //消息队列
#include "semphr.h"       //信号量、互斥信号量
#include "event_groups.h" //事件
#include "timers.h"       //软件定时器
/*
*************************************************************************
*                             函数声明
*************************************************************************
*/
void delay_us(int time)
{
	int i=0;
	while(time--)
	{
		i=10;  //自己定义
		while(i--) ;
	}
}
void delay_ms(int time)
{
	int i=0;
	while(time--)
	{
		i=12000;  //自己定义
		while(i--) ;
	}
}
/***********************************************************************
  * @ 函数名  ： BSP_Init
  * @ 功能说明： 板级外设初始化，所有板子上的初始化均可放在这个函数里面
  * @ 参数    ：   
  * @ 返回值  ： 无
  *********************************************************************/
static void BSP_Init(void)
{
	/*
	* STM32中断优先级分组为4，即4bit都用来表示抢占优先级，范围为：0~15
	* 优先级分组只需要分组一次即可，以后如果有其他的任务需要用到中断，
	* 都统一用这个优先级分组，千万不要再分组，切忌。
	*/
	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_4);
	/* LED 初始化 */
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA,ENABLE);
	
	GPIO_InitTypeDef GPIO_InitStruct;
	GPIO_InitStruct.GPIO_Mode=GPIO_Mode_Out_PP;
	GPIO_InitStruct.GPIO_Speed=GPIO_Speed_2MHz;
	
	GPIO_InitStruct.GPIO_Pin=GPIO_Pin_0;
	GPIO_Init(GPIOA,&GPIO_InitStruct);
	GPIO_InitStruct.GPIO_Pin=GPIO_Pin_1;
	GPIO_Init(GPIOA,&GPIO_InitStruct);
	GPIO_InitStruct.GPIO_Pin=GPIO_Pin_2;
	GPIO_Init(GPIOA,&GPIO_InitStruct);
	GPIO_SetBits(GPIOA,GPIO_Pin_0);
	GPIO_SetBits(GPIOA,GPIO_Pin_1);
	GPIO_SetBits(GPIOA,GPIO_Pin_2);
}
/**********************************************************************
  * @ 函数名  ： LED_Task
  * @ 功能说明： LED_Task任务主体
  * @ 参数    ：   
  * @ 返回值  ： 无
  ********************************************************************/
static void LED_Task(void* parameter)
{
	while (1)
	{
		vTaskDelay(1000);   /* 延时500个tick */
		GPIO_SetBits(GPIOA,GPIO_Pin_0);
		vTaskDelay(1000);   /* 延时500个tick */
		GPIO_SetBits(GPIOA,GPIO_Pin_1);
		vTaskDelay(1000);   /* 延时500个tick */
		GPIO_SetBits(GPIOA,GPIO_Pin_2);
		
		vTaskDelay(1000);   /* 延时500个tick */
		GPIO_ResetBits(GPIOA,GPIO_Pin_0);
		vTaskDelay(1000);   /* 延时500个tick */
		GPIO_ResetBits(GPIOA,GPIO_Pin_1);
		vTaskDelay(1000);   /* 延时500个tick */
		GPIO_ResetBits(GPIOA,GPIO_Pin_2);
  }
}
static TaskHandle_t LED_Task_Handle = NULL;/* LED_Task任务句柄 */
/*****************************************************************
  * @brief  主函数
  * @param  无
  * @retval 无
  * @note   第一步：开发板硬件初始化 
            第二步：创建APP应用任务
            第三步：启动FreeRTOS，开始多任务调度
  ****************************************************************/
int main(void)
{  
	/* 开发板硬件初始化 */
	BSP_Init();
	BaseType_t xReturn = pdPASS;/* 定义一个创建信息返回值，默认为pdPASS */
	xReturn = xTaskCreate((TaskFunction_t )LED_Task, /* 任务入口函数 */
												(const char*    )"LED_Task",/* 任务名字 */
												(uint16_t       )256,   /* 任务栈大小 */
												(void*          )NULL,  /* 任务入口函数参数 */
												(UBaseType_t    )2,      /* 任务的优先级 */
												(TaskHandle_t*  )&LED_Task_Handle);/* 任务控制块指针 */	/* 启动任务调度 */           
	if(pdPASS == xReturn)
	{
		vTaskStartScheduler();   /* 启动任务，开启调度 */
	}
	else
	{
		return -1;
	}
	while(1)   /* 正常不会执行到这里 */
	{
//		delay_ms(1000);
//		GPIO_SetBits(GPIOA,GPIO_Pin_0);
//		delay_ms(1000);
//		GPIO_SetBits(GPIOA,GPIO_Pin_1);
//		delay_ms(1000);
//		GPIO_SetBits(GPIOA,GPIO_Pin_2);
//		delay_ms(1000);
//		GPIO_ResetBits(GPIOA,GPIO_Pin_0);
//		delay_ms(1000);
//		GPIO_ResetBits(GPIOA,GPIO_Pin_1);
//		delay_ms(1000);
//		GPIO_ResetBits(GPIOA,GPIO_Pin_2);
	}
}
/********************************END OF FILE****************************/
