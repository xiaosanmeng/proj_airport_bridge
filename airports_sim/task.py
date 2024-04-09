class Task():
    def __init__(self) -> None:
        ''' 
        Task: 单次航班需要执行的任务

        location: 执行位置
        time: 执行时间
        taskList: 子任务分解 list
        '''
        self.terminals = None # 机位
        self.location = None
        self.time = None
        self.taskList = []
    
    def get_task_description(self):
        return f'Location: {self.location}, Time: {self.time}, TaskList: {self.taskList}'

class TaskSet:
    def __init__(self) -> None:
        ''' 
        TaskSet: 任务集合, 用于存储所有的任务

        tasks: 存储所有的任务
        '''
        self.tasks = []
    
    def add_task(self,task):
        self.tasks.append(task)
    
    def get_tasks(self):
        return self.tasks