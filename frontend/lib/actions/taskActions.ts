import  {CreateTask,Task} from '@/lib/types';




export async  function createTask(taskData: CreateTask ){
    // console.log('this is the taskdata my mann',taskData)

     const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/tasks`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(taskData)
      });

      return response
}

export async function getTaskForDay(family_id : string, selectedDate : string)
{

    console.log(family_id, 'this is the familyid ullllllllaalalalalalal')
    const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/v1/families/${family_id}/tasks?date=${selectedDate}`, 
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  return res
}
