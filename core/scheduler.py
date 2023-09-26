from pathlib import Path
import win32com.client


def getWindowScheduler():
    scheduler = win32com.client.Dispatch('Schedule.Service')
    return scheduler.Connect()


def getWindowTasks():
    scheduler = getWindowScheduler()
    tasks = scheduler.GetFolder('\\').GetTasks(1)
    return tasks


def getWindowTask(name: str):
    tasks = getWindowTasks()
    for task in tasks:
        if name is tasks.Name:
            return task


def createWindowTask(name: str, script_path: Path, *args, **kwargs):
    scheduler = getWindowScheduler()
    tasks = getWindowTasks()
    new_task = scheduler.NewTask(0)
    new_task.Name = name
    new_task.Path = script_path
    new_task.Args = args

    trigger = new_task.Triggers.Create(9)
    trigger.StartBoundary = 'OnStartup'
    tasks.AddTask(new_task)


def removeWindowTask(name: str):
    tasks = getWindowTasks()
