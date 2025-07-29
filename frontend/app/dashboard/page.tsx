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




function Dashboard() {

  const today  = format(new Date(),'yyyy-MM-dd'); 
  const { userData } = useAuthUser();
   const [selectedDate, setSelectedDate] = useState(today);
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  // const  [tasks, setTasks] = useState <Task[] | null>(null)
   const [tasks, setTasks] = useState<Task[]>([
    {
      id: '1',
      title: 'Design user interface mockups',
      description: 'Create wireframes and mockups for the new dashboard',
      assignee: 'John Doe',
      dueDate: '2024-03-15',
      status: 'initialized'
    },
    {
      id: '2',
      title: 'Implement authentication system',
      description: 'Set up user login, registration, and password reset functionality',
      assignee: 'Jane Smith',
      dueDate: '2024-03-20',
      status: 'in-progress',
      checkList: [
        { id: 'check1', title: 'Create login API', completed: false },
        { id: 'check2', title: 'Implement JWT authentication', completed: false },
        { id: 'check3', title: 'Set up user roles', completed: false }
        ]
    },
    {
      id: '3',
      title: 'Set up database schema',
      description: 'Design and implement the database structure for the application',
      assignee: 'Bob Johnson',
      status: 'completed'
    },
    {
      id: '4',
      title: 'Code review process',
      description: 'Establish code review guidelines and workflow',
      assignee: 'Alice Brown',
      dueDate: '2024-03-18',
      status: 'initialized',
      checkList: [
        { id: 'item1', title: 'Review PR #123', completed: false },
        { id: 'item2', title: 'Update documentation', completed: false }
      ]
    }
  ]);

  useEffect(() => {
    
   
   let  data


   const fetchTasks = async () => {

  
    
    try {
       const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/tasks/date`, {
        method: 'POST', 
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          family_id: userData?.family?.id,
          date: selectedDate,
        }),
      });
      
      data = await response.json();
      console.log('this is the data', data)
      setTasks(data)
      return data
    } catch (error) {
      console.error("Failed to fetch tasks", error);

    }
    };


    fetchTasks()
    


  }, [selectedDate])
  


  
  console.log("this is the userdata",userData)


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
 
   

  const [showAddModal, setShowAddModal] = useState(false);
  const [addModalStatus, setAddModalStatus] = useState<string>('initialized');

  const handleTaskMove = (taskId: string, newStatus: string) => {
    setTasks(prevTasks =>
      prevTasks.map(task =>
        task.id === taskId
          ? { ...task, status: newStatus as 'initialized' | 'in-progress' | 'completed' }
          : task
      )
    );
  };

  const handleAddTask = (task: Omit<Task, 'id'>) => {
    const newTask: Task = {
      ...task,
      id: Date.now().toString()
    };
    setTasks(prev => [...prev, newTask]);
  };

  const handleAddTaskClick = (status: string) => {
    setAddModalStatus(status);
    setShowAddModal(true);
  };

  let taskTable;

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
  }else if (tasks == null) {
    taskTable = "loading"
  }else{
   taskTable = <div>
      <KanbanTable
        tasks={tasks}
        onTaskMove={handleTaskMove}
       
      />

     
    </div>}

  
 
  
  
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
                className="w-10 h-10 rounded-full p-0 border  hover:bg-gray-100 transition-colors"
                title="Filter by Date"
              >
                <Filter className="h-4 w-4 text-gray-600 " />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="end">
              <CalendarComponent
                mode="single"
                selected={selectedDate}
                onSelect={handleDateSelect}
                className="border-0"
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
      <div>
        
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleAddTaskClick('initialized')}
                  className="h-6 w-6 p-0 hover:bg-gray-100"
                >
                  <Plus className="w-4 h-4" />
                </Button>
             
      </div>
       <AddTaskModal
        
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onAdd={handleAddTask}
        initialStatus={addModalStatus}
        assignees={userData?.familyMembers}
        userData={userData}
      />
      {/* </div> */}
      {taskTable}
      
    
    </div>
    </div>
  )
}

export default Dashboard;