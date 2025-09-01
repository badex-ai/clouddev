"use client"
import React from 'react'
import { useState, useEffect} from 'react';
import { Task } from '@/lib/types';
import KanbanTable from '@/components/ui/kanbanTable';
import AddTaskModal from '@/components/ui/addTaskModal';
import { useAuthUser } from '@/contexts/userContext';
import { format, parseISO, formatISO,  } from 'date-fns';
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





function Dashboard() {

  const today  = format(new Date(),'yyyy-MM-dd'); 
  const { userData } = useAuthUser();
   const [selectedDate, setSelectedDate] = useState(today);
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  const  [tasks, setTasks] = useState <Task[] | null>([])
  // const  [tasks, setTasks] = useState <Task[] >([])

  //  const [tasks, setTasks] = useState<Task[]>([
  //   {
  //     id: '1',
  //     title: 'Design user interface mockups',
  //     description: 'Create wireframes and mockups for the new dashboard',
  //     assignee: 'John Doe',
  //     dueDate: '2024-03-15',
  //     status: 'initialized'
  //   },
  //   {
  //     id: '2',
  //     title: 'Implement authentication system',
  //     description: 'Set up user login, registration, and password reset functionality',
  //     assignee: 'Jane Smith',
  //     dueDate: '2024-03-20',
  //     status: 'in-progress',
  //     checkList: [
  //       { id: 'check1', title: 'Create login API', completed: false },
  //       { id: 'check2', title: 'Implement JWT authentication', completed: false },
  //       { id: 'check3', title: 'Set up user roles', completed: false }
  //       ]
  //   },
  //   {
  //     id: '3',
  //     title: 'Set up database schema',
  //     description: 'Design and implement the database structure for the application',
  //     assignee: 'Bob Johnson',
  //     status: 'completed'
  //   },
  //   {
  //     id: '4',
  //     title: 'Code review process',
  //     description: 'Establish code review guidelines and workflow',
  //     assignee: 'Alice Brown',
  //     dueDate: '2024-03-18',
  //     status: 'initialized',
  //     checkList: [
  //       { id: 'item1', title: 'Review PR #123', completed: false },
  //       { id: 'item2', title: 'Update documentation', completed: false }
  //     ]
  //   }
  // ]);
 const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [submitIsLoading, setSubmitIsLoading] = useState(false);
  
  

  // console.log('this is the userData oooooo', userData)
  useEffect(() => {

   let data;

   const fetchTasks = async () => {

      

    try {
          const family_id = userData?.family?.id
          if (!family_id) {
            return; // or handle error case
          }
          let res;
          
             res = await getTaskForDay(family_id, selectedDate)
          
          data = await res.json();
          // console.log('this is the data ***********', data)
          setTasks(data)
          return data
        } catch (error) {
          console.error("Failed to fetch tasks", error);

        }
    };

    fetchTasks()

  }, [selectedDate])
  


   const handleDateSelect = (date :Date ) => {
     let newdate = formatISO(date)
     newdate =format(newdate,'yyyy-MM-dd')
    setSelectedDate(newdate);
    setIsCalendarOpen(false);
  };

  const formatShownDay= (date : string) => {
    if (!date) return '';
    return format(date, 'MMM dd, yyyy');
  };

   const convertUTCToLocal = (utcDateString : string) => {
    return parseISO(utcDateString);
  };

  const getDate = () => {
   


    if (selectedDate === today) {
       return "Today's Tasks";
    }
    return `Tasks for ${formatShownDay(selectedDate)}`;
   
  };
 
   

  // const [showAddModal, setShowAddModal] = useState(false);
  // const [addModalStatus, setAddModalStatus] = useState<string>('initialized');

  const handleTaskMove = (taskId: string, newStatus: string) => {
    if(tasks)
    setTasks(tasks =>
      tasks.map(task =>
        task.public_id === taskId
          ? { ...task, status: newStatus as 'initialized' | 'in-progress' | 'completed' }
          : task
      )
    );
  };


 

   const  handleTaskDelete = async(taskId: string)=>{

       if (!tasks) {
    return; // exit early if null
  }
    
    try{
        const result = await deleteTask(taskId)

        if (result.ok ){
          
          setTasks(prevTasks => 
            prevTasks ? prevTasks.filter(task => task.public_id !== taskId) : prevTasks
          );
          
          toast("Task Deleted")
        }
    }catch{
        toast("Task", {
        description: "Task not deleted. Something went wrong when trying to delete the task.",
        action: {
          label: "Undo",
          onClick: () => {
            console.log("Undo delete clicked");
          },
        },
        duration: 4000, // in ms (default is 4000)
      });

      // toast('Task',{
      //   description:" Something went wrong while deleting the task"
      // })
    }

  
  }



  let taskTable;

 

 if(tasks === null){
  taskTable = null
 }else{

  if (tasks?.length === 0) {
    taskTable = 
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
  }else{
   taskTable = <div>
      <KanbanTable
        tasks={tasks}
        onTaskMove={handleTaskMove}
        onDeleteTask={handleTaskDelete}
       
      />

     
    </div>}

 }

 const {
       register,
       handleSubmit,
       formState: { errors },
       control,
     } = useForm<TaskFormData>({
       resolver: zodResolver(taskSchema),
       defaultValues: {
        assignee_id: '',}
     });

  const onFormSubmit = async (data: TaskFormData) => {
      
     
     const user = assignees?.find(user => 
      
        data.assignee_id === user.username

        
      );
        let taskData;
      if(user?.id && userData?.family?.id) {
        
           data.assignee_id = user?.id.toString()
           taskData = {
                title: data.title,
                description: data.description || undefined,
                creator_id: userData?.id,
                assignee_id: user?.id,
                due_date: localToUtc(data.due_date),
                family_id: userData?.family?.id
                
              }
        }
          
        
      try{
        setSubmitIsLoading(true);
        // console.log('data from the form', taskData)
        
          const result = await createTask(taskData)
          if(result.ok){
              toast('New task created')
              // task.push()

             const createdTask = await result.json()


            if (data.due_date === today && tasks) {
              setTasks(tasks => [...tasks, createdTask])
            }
      
           

              
          }

        

          
          
      }catch{
        toast('Something went wrong while creating the task')
        
      }finally{
          setSubmitIsLoading(false);
      }
  
      
    }
    


      // console.log('this is the userData oblee oblee:', userData)
  
 const assignees = userData?.family?.members
  
  
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
                className="w-10 h-10 rounded-full p-0 border  hover:bg-gray-100 transition-colors cursor-pointer"
                title="Filter by Date"
              >
                <Filter className="h-4 w-4 text-gray-600 " />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="end">
              <CalendarComponent
                mode="single"
                selected={new Date()}
                onSelect={handleDateSelect}
                className="border-0"
                required
              />
              <div className="p-3 border-t">
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => {
                    setSelectedDate(today);
                    setIsCalendarOpen(false);
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
      <Dialog>
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
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-4 pt-4">
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
            <SelectItem key={assignee.id} value={assignee.username}>
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

      </div>

      <div className="space-y-2">
        <Label htmlFor="task-due-date">Due Date *</Label>
        <div className="relative">
          <Input
            id="task-due-date"
            type="datetime-local"
            {...register("due_date")}
            min={new Date(Date.now() + 60 * 60 * 1000).toISOString().slice(0, 16)} // 1 hour from now
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
      
      {/* </div> */}
      {taskTable}
      
    
    </div>
    </div>
  )
}

export default Dashboard;