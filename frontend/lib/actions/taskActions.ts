'use server';
import { CreateTask, Task, ChecklistItem } from '@/lib/types';
import { getConfig } from '../config';
import { AppError, ErrorMessages } from '../errors';
import { logger } from '../logger';

const { apiUrl } = getConfig();

export async function createTask(taskData: CreateTask) {
  const startTime = Date.now();
  try {
    const response = await fetch(`${apiUrl}/api/v1/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(taskData),
    });

    const responseData = await response.json();

    if (!response.ok) {
      const technicalMessage = responseData.message || responseData.detail || 'Failed to create task';
      logger.error('api_call_failed', {
        action: 'createTask',
        status: response.status,
        error: technicalMessage,
        duration_ms: Date.now() - startTime,
      });
      throw new AppError({
        title: 'Task Error',
        userMessage: responseData.message || ErrorMessages.TASK_CREATE_FAILED,
        technicalMessage,
      });
    }

    logger.info('api_call_success', {
      action: 'createTask',
      duration_ms: Date.now() - startTime,
    });
    return responseData;
  } catch (error) {
    if (error instanceof AppError) {
      throw error;
    }
    logger.error('api_call_failed', {
      action: 'createTask',
      error: 'network_error',
      duration_ms: Date.now() - startTime,
    });
    throw new AppError({
      title: 'Connection Error',
      userMessage: ErrorMessages.NETWORK_ERROR,
      technicalMessage: error instanceof Error ? error.message : 'Network error',
    });
  }
}

export async function getTaskForDay(family_id: string, selectedDate: string) {
  const startTime = Date.now();
  try {
    const response = await fetch(
      `${apiUrl}/api/v1/families/${family_id}/tasks?date=${selectedDate}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    const responseData = await response.json();

    if (!response.ok) {
      const technicalMessage = responseData.message || responseData.detail || 'Failed to fetch tasks';
      logger.error('api_call_failed', {
        action: 'getTaskForDay',
        status: response.status,
        error: technicalMessage,
      });
      throw new AppError({
        title: 'Task Error',
        userMessage: responseData.message || ErrorMessages.GENERIC_ERROR,
        technicalMessage,
      });
    }

    return responseData;
  } catch (error) {
    if (error instanceof AppError) {
      throw error;
    }
    logger.error('api_call_failed', {
      action: 'getTaskForDay',
      error: 'network_error',
      duration_ms: Date.now() - startTime,
    });
    throw new AppError({
      title: 'Connection Error',
      userMessage: ErrorMessages.NETWORK_ERROR,
      technicalMessage: error instanceof Error ? error.message : 'Network error',
    });
  }
}

export async function deleteTask(taskId: string) {
  const startTime = Date.now();
  try {
    const response = await fetch(`${apiUrl}/api/v1/tasks/${taskId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      let errorMessage = 'Failed to delete task';

      try {
        const errorData = await response.json();
        errorMessage = errorData.message || errorData.detail || errorMessage;
      } catch {
        errorMessage = response.statusText || errorMessage;
      }

      logger.error('api_call_failed', {
        action: 'deleteTask',
        status: response.status,
        error: errorMessage,
      });
      throw new AppError({
        title: 'Task Deletion Error',
        userMessage: ErrorMessages.TASK_DELETE_FAILED,
        technicalMessage: errorMessage,
      });
    }

    logger.info('api_call_success', {
      action: 'deleteTask',
      duration_ms: Date.now() - startTime,
    });
    return;
  } catch (error) {
    if (error instanceof AppError) {
      throw error;
    }
    logger.error('api_call_failed', {
      action: 'deleteTask',
      error: 'network_error',
      duration_ms: Date.now() - startTime,
    });
    throw new AppError({
      title: 'Connection Error',
      userMessage: ErrorMessages.NETWORK_ERROR,
      technicalMessage: error instanceof Error ? error.message : 'Network error',
    });
  }
}

export async function addCheckListItem(taskId: string, checkListItem: Omit<ChecklistItem, 'id'>) {
  const startTime = Date.now();
  try {
    const response = await fetch(`${apiUrl}/api/v1/tasks/${taskId}/checklist`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(checkListItem),
    });

    const responseData = await response.json();

    if (!response.ok) {
      const technicalMessage =
        responseData.message || responseData.detail || 'Failed to add checklist item';
      logger.error('api_call_failed', {
        action: 'addCheckListItem',
        status: response.status,
        error: technicalMessage,
      });
      throw new AppError({
        title: 'Task Error',
        userMessage: responseData.message || ErrorMessages.TASK_UPDATE_FAILED,
        technicalMessage,
      });
    }

    return responseData;
  } catch (error) {
    if (error instanceof AppError) {
      throw error;
    }
    logger.error('api_call_failed', {
      action: 'addCheckListItem',
      error: 'network_error',
      duration_ms: Date.now() - startTime,
    });
    throw new AppError({
      title: 'Connection Error',
      userMessage: ErrorMessages.NETWORK_ERROR,
      technicalMessage: error instanceof Error ? error.message : 'Network error',
    });
  }
}

export async function deleteCheckListItem(taskId: string, checkListItemId: number) {
  const startTime = Date.now();
  try {
    const response = await fetch(`${apiUrl}/api/v1/tasks/${taskId}/checklist/${checkListItemId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    const responseData = await response.json();

    if (!response.ok) {
      const technicalMessage =
        responseData.message || responseData.detail || 'Failed to delete checklist item';
      logger.error('api_call_failed', {
        action: 'deleteCheckListItem',
        status: response.status,
        error: technicalMessage,
      });
      throw new AppError({
        title: 'Task Error',
        userMessage: responseData.message || ErrorMessages.TASK_UPDATE_FAILED,
        technicalMessage,
      });
    }
    return responseData;
  } catch (error) {
    if (error instanceof AppError) {
      throw error;
    }
    logger.error('api_call_failed', {
      action: 'deleteCheckListItem',
      error: 'network_error',
      duration_ms: Date.now() - startTime,
    });
    throw new AppError({
      title: 'Connection Error',
      userMessage: ErrorMessages.NETWORK_ERROR,
      technicalMessage: error instanceof Error ? error.message : 'Network error',
    });
  }
}
