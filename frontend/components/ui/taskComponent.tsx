"use client";
import React ,{useState}from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { GripVertical, User, Calendar, Delete } from 'lucide-react';
import { Checkbox } from "@/components/ui/checkbox"
import { Task } from '@/lib/types';
import {utcToLocal} from  '@/lib/utils'
import { Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuthUser } from '@/contexts/userContext'
import { Plus } from 'lucide-react';
import { Input } from "@/components/ui/input"
import {addCheckListItem} from "@/lib/actions/taskActions"
import {ChecklistItemForm, ChecklistSchema} from "@/lib/validations/task"
import { useForm,Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod"




interface DraggableTaskProps {
  task: Task;
  onDragStart: (e: React.DragEvent, task: Task) => void;
  isDragging: boolean;
  onDeleteTask: (taskId: string)=>void
}


const DraggableTask: React.FC<DraggableTaskProps> = ({ task, onDragStart, isDragging,onDeleteTask }) => {

   const { userData } = useAuthUser();
   const [openAddChecklistItem, setOpenAddChecklistItem] = useState(false)

   const assingedUser = userData?.family?.members.filter((member)=>{
    return member.id == task.assignee_id
   })[0]
  const [checkedItems, setCheckedItems] = React.useState<string[]>(
    task.checkList?.filter(item => item.completed).map(item => item.id) || []
  );


    const {
      register,
      handleSubmit,
      formState: { errors },
      reset 
    } = useForm<ChecklistItemForm>({
      resolver: zodResolver(ChecklistSchema),
    })

  const handleCheck = (itemId: string, checked: boolean) => {
    setCheckedItems(prev =>
      checked ? [...prev, itemId] : prev.filter((value: string) => value !== itemId)
    );
  };

  const handleAddChecklist=()=>{
    console.log('clicked dawg')
    setOpenAddChecklistItem(true)
  }

    const handleDelectChecklistItem=()=>{
    console.log('checklist ietem deleted')
  }

  

    // const  handleKeyPress=async(e,)=>{

      
    //   if(e.keyCode == 13){
    //     console.log('Enter key pressed, submitting checklist')

    //    const response =  await addCheckListItem(task.public_id, )
    //     // console.log(e)

    //   }
    // }

    const onSubmitChecklist = async (data: ChecklistItemForm ) => {
  console.log('Form submitted with data:', data);
  try {
   


    const subtask = {
      id: task.checkList ?    task.checkList.length + 1 : 1,
      title: data.subtask,
      completed : false

    }


    const result = await addCheckListItem(task.public_id,subtask)
    // Handle successful submission
    if (result.ok){
    reset(); // Reset the form after successful submission
    setOpenAddChecklistItem(false)

    }
   
  } catch (error) {
    
    console.error('Error adding checklist item:', error);
   
  }
};

// This function handles Enter key press to trigger form submission
const handleKeyPress = (e) => {
  if (e.key === 'Enter') {
    e.preventDefault(); // Prevent default to avoid any unwanted behavior
    handleSubmit(onSubmitChecklist)(); // Manually trigger form submission
  }
};
  
 

  return (
    <div className='relative'>
      <Card 
      draggable
      onDragStart={(e) => onDragStart(e, task)}
      className={`cursor-move transition-all duration-200 hover:shadow-md mb-3 ${
        isDragging ? 'opacity-50 transform rotate-1' : ''
      }`}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <CardTitle className="text-sm font-medium line-clamp-2 flex-1">
            {task.title}
          </CardTitle>
          <GripVertical className="w-4 h-4 text-gray-400 flex-shrink-0 ml-2" />
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        {task.description && (
          <p className="text-xs text-gray-600 mb-3 line-clamp-2">
            {task.description}
          </p>
        )}
        <div className="flex flex-wrap gap-1 mb-2">
          {task.assignee_id && (
            <Badge variant="secondary" className="text-xs">
              <User className="w-3 h-3 mr-1" />
              {assingedUser?.username}
            </Badge>
          )}
          {task.due_date && (
            <Badge variant="outline" className="text-xs">
              <Calendar className="w-3 h-3 mr-1" />
              {`${utcToLocal(task.due_date)}`}
            </Badge>
          )}
        </div>
        <Badge 
          variant={
            task.status === 'completed' ? 'default' : 
            task.status === 'in-progress' ? 'secondary' : 'outline'
          }
          className="text-xs"
        >
          {task.status.replace('-', ' ')}
        </Badge>

        <div className="mt-4 relative">
          <div>
            
             <Button 
                variant="ghost" 
                size="sm"
                title="Add checklist"
                onClick={()=>handleAddChecklist()}
              >
                <Plus className="h-4 w-4 text-gray-600 " />
              </Button>

            <span>checklist</span>
              {openAddChecklistItem && <div className='border  z-4 w-[14rem] bg-gray py-1 px-2 absolute top-[16] left-[100] rounded-sm'>
               <form onSubmit={handleSubmit(onSubmitChecklist)}>
      <Input 
        {...register("subtask")} 
        onKeyDown={handleKeyPress}
        className='h-7' 
        placeholder='add new check item'
        autoFocus
      />
      {errors.subtask && (
        <p className="text-red-500 text-xs mt-1">{errors.subtask.message}</p>
      )}
    </form>
             </div>}
             
          </div>
          {task.checkList && task.checkList.length > 0 && (
            <>
              <div className="mb-1 font-semibold text-xs text-gray-500">Checklist</div>
              <form>
            {task.checkList.map((item) => (
              <div key={item.id} className="flex items-center mb-1">
                <Checkbox
                  name={`checkList.${item.id}`}
                  checked={checkedItems.includes(item.id)}
                  onCheckedChange={(checked: boolean) => handleCheck(item.id, checked)}
                />
                <label className="ml-2 text-xs text-gray-700">
                  {item.title}
                </label>
                <Button 
                variant="ghost" 
                size="sm"
                title="Delete task"
                onClick={()=>handleDelectChecklistItem()}
              >
                <Trash2 className="h-4 w-4 text-gray-600 " />
              </Button>
              </div>
            ))}
              </form>
            </>
          )}
        </div>
       
      </CardContent>
    </Card>
    <div className='absolute top-4 right-15'>
          <Button 
                variant="ghost" 
                size="sm"
                title="Delete task"
                onClick={()=>onDeleteTask(task.public_id)}
              >
                <Trash2 className="h-4 w-4 text-gray-600 " />
              </Button>
          
    </div>
    </div>
    
   
  );
};

export default DraggableTask;