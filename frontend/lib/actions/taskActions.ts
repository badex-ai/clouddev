'use server';
import { CreateTask, Task, ChecklistItem } from '@/lib/types';
import { getConfig } from '../config';
import { ApiException , NetworkError} from '../utils';

const { apiUrl } = getConfig();

export async function createTask(taskData: CreateTask) {
  try {
    const response = await fetch(`${apiUrl}/api/v1/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(taskData),
  });

   const responseData = await response.json();
      // console.log(responseData, 'error from response')
  
      if (!response.ok) {
        const errorMessage =
          responseData.message || responseData.detail || 'Failed to create task';
       
        const error = new ApiException('Task Error', errorMessage);
  
        throw error;
      }

      return responseData
  } catch (error) {
    if (error instanceof ApiException) {
      throw error;
    }

    // Handle network errors (fetch failures)
    throw new Error(
      NetworkError
    );
  }
    
}

export async function getTaskForDay(family_id: string, selectedDate: string) {
  try {
      const response = await fetch(`${apiUrl}/api/v1/families/${family_id}/tasks?date=${selectedDate}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

   const responseData = await response.json();
      // console.log(responseData, 'error from response')
  
      if (!response.ok) {
        const errorMessage =
          responseData.message || responseData.detail || 'Failed to fetch task';
       
        const error = new ApiException('Task Error', errorMessage);
  
        throw error;
      }

      return responseData


  } catch (error) {
       if (error instanceof ApiException) {
      throw error;
    }

    // Handle network errors (fetch failures)
    throw new Error(
      NetworkError
    );
  }

}

export async function deleteTask(taskId: string) {
  try {
    const response = await fetch(`${apiUrl}/api/v1/tasks/${taskId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const responseData = await response.json();
      // console.log(responseData, 'error from response')
  
    if (!response.ok) {
      const errorMessage =
        responseData.message || responseData.detail || 'Failed to delete task';
      
      const error = new ApiException('Task Error', errorMessage);

      throw error;
    }

    return responseData

  } catch (error) {
    if (error instanceof ApiException) {
      throw error;
    }

    // Handle network errors (fetch failures)
    throw new Error(
      NetworkError
    );
  }

}

export async function addCheckListItem(taskId: string, checkListItem: ChecklistItem) {

  try {
     const response = await fetch(`${apiUrl}/api/v1/tasks/${taskId}/checklist`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(checkListItem),
  });

  const responseData = await response.json();
      // console.log(responseData, 'error from response')
  
    if (!response.ok) {
      const errorMessage =
        responseData.message || responseData.detail || 'Failed to add checklist to item';
      
      const error = new ApiException('Task Error', errorMessage);

      throw error;
    }

    return responseData
  } catch (error) {
    if (error instanceof ApiException) {
      throw error;
    }

    // Handle network errors (fetch failures)
    throw new Error(
      NetworkError
    );
  }
 
}

export async function deleteCheckListItem(taskId: string, checkListItemId: number) {
  try {
      const response = await fetch(`${apiUrl}/api/v1/tasks/${taskId}/checklist/${checkListItemId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const responseData = await response.json();
    
      if (!response.ok) {
        const errorMessage = responseData.message || responseData.detail || 'Failed to delete checklist item';
        const error = new ApiException('Task Error', errorMessage);
        throw error;
      }
      return responseData
    } catch (error) {
      if (error instanceof ApiException) {
        throw error;
      }
      throw new Error(
        NetworkError
      );
  }
 
}
