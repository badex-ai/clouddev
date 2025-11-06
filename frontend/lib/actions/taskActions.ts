'use server' 
import  {CreateTask,Task,ChecklistItem} from '@/lib/types';
import {getConfig} from "../config"

  const {apiUrl} = getConfig()




export async  function createTask(taskData: CreateTask ){
    // console.log('this is the taskdata my mann',taskData)

     const response = await fetch(`${apiUrl}/api/v1/tasks`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(taskData)
      });

      return response.json()
}

export async function getTaskForDay(family_id : string, selectedDate : string)
{

   
    const res = await fetch(
    `${apiUrl}/api/v1/families/${family_id}/tasks?date=${selectedDate}`, 
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );


  return res.json()
}


export async function deleteTask(taskId:string)
{

 
    const res = await fetch(
    `${apiUrl}/api/v1/tasks/${taskId}`, 
    {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  return res.json()
}

export async function addCheckListItem(taskId: string,checkListItem : ChecklistItem){
   const res = await fetch(
    `${apiUrl}/api/v1/tasks/${taskId}/checklist`, 
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        
      },
      body: JSON.stringify(checkListItem)
    }
  );

  return res.json()
}


export async function deleteCheckListItem(taskId: string,checkListItemId : number){
   const res = await fetch(
    `${apiUrl}/api/v1/tasks/${taskId}/checklist/${checkListItemId}`, 
    {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json' 
      },  
    }
  );
  return res.json()
}
