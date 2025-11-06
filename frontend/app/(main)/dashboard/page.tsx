"use client"
import React from 'react'
import { useState, useEffect} from 'react';
import { CreateTask, Task } from '@/lib/types';
import KanbanTable from '@/components/ui/kanbanTable';
import AddTaskModal from '@/components/ui/addTaskModal';
import { useAuthUser } from '@/contexts/userContext';
import { format, parseISO, formatISO,parse  } from 'date-fns';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { Calendar as CalendarComponent } from '@/components/ui/calendar';
import { Filter , Package} from 'lucide-react';
import { Plus } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { useForm,Controller } from "react-hook-form";
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { zodResolver } from "@hookform/resolvers/zod"
import {createTask} from '@/lib/actions/taskActions'
import { taskSchema,TaskFormData } from '@/lib/validations/task';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {localToUtc} from'@/lib/utils'
import { toast } from 'sonner';
import { getTaskForDay } from '@/lib/actions/taskActions';
import {deleteTask}from '@/lib/actions/taskActions'
import  CircleIcon from '../../../components/icons/circleIcon'
import { useRouter, useSearchParams } from 'next/navigation';







function Dashboard() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const today = format(new Date(), 'yyyy-MM-dd');
  const dasboardDate = searchParams.get('d') || today;
  const { userData } = useAuthUser();
  
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [taskIsLoading, setTasksIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [submitIsLoading, setSubmitIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    control,
    reset
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      assignee_id: '',
    }
  });

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const family_id = userData?.family?.id;
        if (!family_id) {
          return;
        }

        const res = await getTaskForDay(family_id, dasboardDate);

          const data =  res
          setTasks(data);
        
      } catch (error) {
        console.error("Failed to fetch tasks", error);
      } finally {
        setTasksIsLoading(false);
      }
    };

    fetchTasks();
  }, [dasboardDate, userData?.family?.id]);

  const handleDateSelect = (date: Date | undefined) => {
    if (!date) return;
    
    // Use date-fns format to respect local timezone
    const newdate = format(date, 'yyyy-MM-dd');
    
    // Close calendar immediately for instant feedback
    setIsCalendarOpen(false);
    
    // Update URL - this will trigger useEffect automatically
    router.replace(`/dashboard?d=${newdate}`, { scroll: false });
  };

  const updateTaskInList = (updatedTask: Task) => {
    setTasks(prevTasks =>
      prevTasks.map(task =>
        task.public_id === updatedTask.public_id ? updatedTask : task
      )
    );
  };

  const formatShownDay = (date: string) => {
    if (!date) return '';
    return format(date, 'MMM dd, yyyy');
  };

  const convertUTCToLocal = (utcDateString: string) => {
    return parseISO(utcDateString);
  };

  const getDate = () => {
    if (dasboardDate === today) {
      return "Today's Tasks";
    }
    return `Tasks for ${formatShownDay(dasboardDate)}`;
  };

  const handleTaskMove = (taskId: string, newStatus: string) => {
    if (tasks)
      setTasks(tasks =>
        tasks.map(task =>
          task.public_id === taskId
            ? { ...task, status: newStatus as 'initialised' | 'in-progress' | 'completed' }
            : task
        )
      );
  };

  const handleTaskDelete = async (taskId: string) => {
    if (!tasks) {
      return;
    }

    try {
      await deleteTask(taskId);

      setTasks(prevTasks =>
        prevTasks ? prevTasks.filter(task => task.public_id !== taskId) : prevTasks
      );

      toast("Task Deleted");
    } catch {
      toast("Task", {
        description: "Task not deleted. Something went wrong when trying to delete the task.",
        action: {
          label: "Undo",
          onClick: () => {
            console.log("Undo delete clicked");
          },
        },
        duration: 4000,
      });
    }
  };

  let taskTable = null;

  if (taskIsLoading === false) {
    if (tasks?.length === 0) {
      taskTable = (
        <div className="w-full border rounded-sm border-[#888888] p-8 flex flex-col items-center justify-center ">
          <Package
            size={48}
            className="text-gray-400 mb-4"
            strokeWidth={1.5}
          />
          <p className="text-gray-600 text-lg font-medium">
            You don't have any tasks
          </p>
        </div>
      );
    } else {
      taskTable = (
        <div>
          <KanbanTable
            tasks={tasks}
            onTaskMove={handleTaskMove}
            onDeleteTask={handleTaskDelete}
            onTaskUpdate={updateTaskInList}
          />
        </div>
      );
    }
  }

  const onFormSubmit = async (data: TaskFormData) => {
    if (!userData?.family?.id || !data || !data.due_date) {
      toast('Missing required information');
      return;
    }

    const taskData = {
      title: data.title,
      description: data.description || undefined,
      creator_id: userData.id,
      assignee_id: data.assignee_id,
      due_date: localToUtc(data.due_date),
      family_id: userData.family.id
    };

    try {
      setSubmitIsLoading(true);

      const result = await createTask(taskData);

      reset();
      
      setIsDialogOpen(false);
        

      toast('New task created');

      const createdTask = result;
      console.log(createdTask,'bake beans')

     

      // if (format(data.due_date, 'yyyy-MM-dd') === dasboardDate && tasks) {
        setTasks(tasks => [...tasks, createdTask]);
      // }

       console.log(format(data.due_date, 'yyyy-MM-dd') , 'data date' )
      console.log(dasboardDate, 'dasboard date')
      console.log(tasks, 'tasks')

      

       
      //
     
    } catch {
      toast('Something went wrong while creating the task');
    } finally {
      setSubmitIsLoading(false);
      
    }
  };

  const assignees = userData?.family?.members;
  const completedTasks = tasks.filter(task => task.status === 'completed').length;
  const percentage = tasks.length > 0 ? Math.round((completedTasks / tasks.length) * 100) : 0;

  // Parse dasboardDate for calendar selected prop
  const calendarSelectedDate = parse(dasboardDate, 'yyyy-MM-dd', new Date());

  return (
    <div className="w-full h-screen bg-gray-50 p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-800">{userData?.family?.name}'s Family Board</h1>
            <p className="text-gray-600 mt-1">Manage your tasks across different stages</p>
          </div>

          <div className="flex items-center gap-3">
            <div className="bg-blue-100 px-4 py-2 rounded-lg border border-blue-200">
              <h2 className="text-xl font-semibold text-blue-800">
                {getDate()}
              </h2>
            </div>

            <Popover open={isCalendarOpen} onOpenChange={setIsCalendarOpen}>
              <PopoverTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-10 h-10 rounded-full p-0 border hover:bg-gray-100 transition-colors cursor-pointer"
                  title="Filter by Date"
                >
                  <Filter className="h-4 w-4 text-gray-600" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="end">
                <CalendarComponent
                  mode="single"
                  selected={calendarSelectedDate}
                  onSelect={handleDateSelect}
                  className="border-0"
                  required
                />
                <div className="p-3 border-t">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setIsCalendarOpen(false);
                      router.replace(`/dashboard?d=${today}`, { scroll: false });
                    }}
                    className="w-full text-sm"
                  >
                    Clear Filter (Show Today's Tasks)
                  </Button>
                </div>
              </PopoverContent>
            </Popover>
          </div>
        </div>

        <div className='flex'>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="flex items-center gap-2 mb-10 cursor-pointer">
                <Plus className="h-4 w-4" />
                Add New Task
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Add New Task</DialogTitle>
                <DialogDescription>
                  Add new task, assign to a family member or self and set a due date.
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit(onFormSubmit)}  className="space-y-4 pt-4">
                <div className="space-y-2">
                  <Label htmlFor="task-title">Title *</Label>
                  <Input
                    id="task-title"
                    placeholder="Enter task title"
                    {...register("title")}
                  />
                  {errors.title && (
                    <p className="text-sm font-medium text-destructive">{errors.title.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="task-description">Description</Label>
                  <Input
                    id="task-description"
                    placeholder="Enter task description"
                    {...register("description")}
                  />
                  {errors.description && (
                    <p className="text-sm font-medium text-destructive">{errors.description.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="task-assignee">Assign To *</Label>
                  <Controller
                    control={control}
                    name="assignee_id"
                    render={({ field }) => (
                      <Select onValueChange={field.onChange} value={field.value}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select an assignee" />
                        </SelectTrigger>
                        <SelectContent>
                          {assignees?.map((assignee) => (
                            <SelectItem key={assignee.id} value={assignee.id}>
                              {assignee.username}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}
                  />
                  {errors.assignee_id && (
                    <p className="text-sm font-medium text-destructive">{errors.assignee_id.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="task-due-date">Due Date *</Label>
                  <div className="relative">
                    <Input
                      id="task-due-date"
                      type="datetime-local"
                      {...register("due_date")}
                      min={new Date(Date.now() + 60 * 60 * 1000).toISOString().slice(0, 16)}
                    />
                  </div>
                </div>
                {errors.due_date && (
                  <p className="text-sm font-medium text-destructive">{errors.due_date.message}</p>
                )}

                <div className="flex justify-end gap-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setIsDialogOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" disabled={submitIsLoading}>
                    {submitIsLoading ? '...loading' : "Add Task"}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
          <div className='ml-auto w-10 h-10'>
            {tasks.length > 0 &&
              <CircleIcon
                percentage={percentage}
                size={50}
                strokeWidth={6}
                color="#DD2E44"
              />
            }
          </div>
        </div>
        {taskTable}
      </div>
    </div>
  );
}

export default Dashboard;