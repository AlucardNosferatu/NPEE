/**
  ******************************************************************************
  * @file    main.c
  * @author  Sumjess
  * @version V1.0
  * @date    2019-09-xx
  * @brief   MDK5.27
  ******************************************************************************
  * @attention
  *
  * 实验平台   :STM32 F429 
  * CSDN Blog  :https://blog.csdn.net/qq_38351824
  * 微信公众号 :Tech云
  *
  ******************************************************************************
  */
  
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
//毫秒级的延时
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
}
/**********************************************************************
  * @ 函数名  ： LED_Task
  * @ 功能说明： LED_Task任务主体
  * @ 参数    ：   
  * @ 返回值  ： 无
  ********************************************************************/
static void LED_Task(void* parameter)
{
	const int interval = 1000; //任务周期时间 --- 定义延时时间 ---  pdMS_TO_TICKS毫秒转tick
	while (1)
	{
		vTaskDelay(interval);   /* 延时500个tick */
		GPIO_SetBits(GPIOA,GPIO_Pin_0);
		vTaskDelay(interval);   /* 延时500个tick */
		GPIO_SetBits(GPIOA,GPIO_Pin_1);
		vTaskDelay(interval);   /* 延时500个tick */
		GPIO_SetBits(GPIOA,GPIO_Pin_2);
		
		vTaskDelay(interval);   /* 延时500个tick */
		GPIO_ResetBits(GPIOA,GPIO_Pin_0);
		vTaskDelay(interval);   /* 延时500个tick */
		GPIO_ResetBits(GPIOA,GPIO_Pin_1);
		vTaskDelay(interval);   /* 延时500个tick */
		GPIO_ResetBits(GPIOA,GPIO_Pin_2);
  }
}
static TaskHandle_t AppTaskCreate_Handle = NULL;/* 创建任务句柄 */
static TaskHandle_t LED_Task_Handle = NULL;/* LED_Task任务句柄 */
/***********************************************************************
  * @ 函数名  ： AppTaskCreate
  * @ 功能说明： 为了方便管理，所有的任务创建函数都放在这个函数里面
  * @ 参数    ： 无  
  * @ 返回值  ： 无
  **********************************************************************/
static void AppTaskCreate(void)
{
	BaseType_t xReturn = pdPASS;/* 定义一个创建信息返回值，默认为pdPASS */
	GPIO_SetBits(GPIOA,GPIO_Pin_0);
	GPIO_ResetBits(GPIOA,GPIO_Pin_1);
	GPIO_ResetBits(GPIOA,GPIO_Pin_2);
	taskENTER_CRITICAL();           //进入临界区
	/* 创建LED_Task任务 */
	xReturn = xTaskCreate((TaskFunction_t )LED_Task, /* 任务入口函数 */
												(const char*    )"LED_Task",/* 任务名字 */
												(uint16_t       )512,   /* 任务栈大小 */
												(void*          )NULL,  /* 任务入口函数参数 */
												(UBaseType_t    )2,      /* 任务的优先级 */
												(TaskHandle_t*  )&LED_Task_Handle);/* 任务控制块指针 */
	if(pdPASS == xReturn)
	{
		GPIO_SetBits(GPIOA,GPIO_Pin_0);
		GPIO_SetBits(GPIOA,GPIO_Pin_1);
		GPIO_ResetBits(GPIOA,GPIO_Pin_2);
	}
	else
	{
		GPIO_SetBits(GPIOA,GPIO_Pin_0);
		GPIO_ResetBits(GPIOA,GPIO_Pin_1);
		GPIO_ResetBits(GPIOA,GPIO_Pin_2);
	}
	vTaskDelete(AppTaskCreate_Handle); //删除AppTaskCreate任务
	taskEXIT_CRITICAL();            //退出临界区
}

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
	GPIO_SetBits(GPIOA,GPIO_Pin_0);
	GPIO_ResetBits(GPIOA,GPIO_Pin_1);
	GPIO_ResetBits(GPIOA,GPIO_Pin_2);
	xReturn = xTaskCreate((TaskFunction_t )AppTaskCreate,  /* 任务入口函数---即任务函数的名称，需要我们自己定义并且实现。*/
												(const char*    )"AppTaskCreate",/* 任务名字---字符串形式， 最大长度由 FreeRTOSConfig.h 中定义的configMAX_TASK_NAME_LEN 宏指定，多余部分会被自动截掉，这里任务名字最好要与任务函数入口名字一致，方便进行调试。*/
												(uint16_t       )512,  /* 任务栈大小---字符串形式， 最大长度由 FreeRTOSConfig.h 中定义的configMAX_TASK_NAME_LEN 宏指定，多余部分会被自动截掉，这里任务名字最好要与任务函数入口名字一致，方便进行调试。*/
												(void*          )NULL,/* 任务入口函数参数---字符串形式， 最大长度由 FreeRTOSConfig.h 中定义的configMAX_TASK_NAME_LEN 宏指定，多余部分会被自动截掉，这里任务名字最好要与任务函数入口名字一致，方便进行调试。*/
												(UBaseType_t    )1, /* 任务的优先级---优先级范围根据 FreeRTOSConfig.h 中的宏configMAX_PRIORITIES 决定， 如果使能 configUSE_PORT_OPTIMISED_TASK_SELECTION，这个宏定义，则最多支持 32 个优先级；如果不用特殊方法查找下一个运行的任务，那么则不强制要求限制最大可用优先级数目。在 FreeRTOS 中， 数值越大优先级越高， 0 代表最低优先级。*/
												(TaskHandle_t*  )&AppTaskCreate_Handle);/* 任务控制块指针---在使用内存的时候，需要给任务初始化函数xTaskCreateStatic()传递预先定义好的任务控制块的指针。在使用动态内存的时候，任务创建函数 xTaskCreate()会返回一个指针指向任务控制块，该任务控制块是 xTaskCreate()函数里面动态分配的一块内存。*/ 
	/* 启动任务调度 */           
	if(pdPASS == xReturn)
	{
		GPIO_SetBits(GPIOA,GPIO_Pin_0);
		GPIO_SetBits(GPIOA,GPIO_Pin_1);
		GPIO_ResetBits(GPIOA,GPIO_Pin_2);
		vTaskStartScheduler();   /* 启动任务，开启调度 */
	}
	else
	{
		GPIO_SetBits(GPIOA,GPIO_Pin_0);
		GPIO_ResetBits(GPIOA,GPIO_Pin_1);
		GPIO_ResetBits(GPIOA,GPIO_Pin_2);
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
