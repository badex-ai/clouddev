'use server';
import { CreateNewFamilyMember } from '@/lib/types';
import { type SignupFormData } from '@/lib/validations/auth';
import { getConfig } from '../config';
import { AppError, ErrorMessages } from '../errors';
import { logger } from '../logger';

const { apiUrl, nextUrl } = getConfig();

export async function getUserData(user: any) {
  try {
    const response = await fetch(`${apiUrl}/api/v1/users/me`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_email: user.email }),
    });

    const responseData = await response.json();

    if (!response.ok) {
      const technicalMessage =
        responseData.message || responseData.detail || 'Failed to fetch user data';
      throw new AppError({
        title: 'User Profile Error',
        userMessage: responseData.message || ErrorMessages.GENERIC_ERROR,
        technicalMessage,
      });
    }

    const mergedData = {
      ...user,
      ...responseData,
    };

    return mergedData;
  } catch (error) {
    if (error instanceof AppError) {
      throw error;
    }
    throw new AppError({
      title: 'Connection Error',
      userMessage: ErrorMessages.NETWORK_ERROR,
      technicalMessage: error instanceof Error ? error.message : 'Network error',
    });
  }
}

export async function createNewFamilyMember(userInfo: CreateNewFamilyMember) {
  const startTime = Date.now();
  try {
    const response = await fetch(`${apiUrl}/api/v1/users/new`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userInfo),
    });

    const responseData = await response.json();

    if (!response.ok) {
      const technicalMessage =
        responseData.message || responseData.detail || 'Failed to create family member';
      logger.error('api_call_failed', {
        action: 'createNewFamilyMember',
        status: response.status,
        error: technicalMessage,
      });
      throw new AppError({
        title: 'Family Member Error',
        userMessage: responseData.message || ErrorMessages.MEMBER_CREATE_FAILED,
        technicalMessage,
      });
    }

    logger.info('api_call_success', {
      action: 'createNewFamilyMember',
      duration_ms: Date.now() - startTime,
    });
    return responseData;
  } catch (error) {
    if (error instanceof AppError) {
      throw error;
    }
    logger.error('api_call_failed', {
      action: 'createNewFamilyMember',
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

export async function getFamilymembers(familyId: string) {
  try {
    const response = await fetch(`${apiUrl}/api/v1/families/${familyId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    const responseData = await response.json();

    if (!response.ok) {
      const technicalMessage =
        responseData.message || responseData.detail || 'Failed to fetch family members';
      throw new AppError({
        title: 'Family Error',
        userMessage: responseData.message || ErrorMessages.GENERIC_ERROR,
        technicalMessage,
      });
    }

    return responseData;
  } catch (error) {
    if (error instanceof AppError) {
      throw error;
    }
    throw new AppError({
      title: 'Connection Error',
      userMessage: ErrorMessages.NETWORK_ERROR,
      technicalMessage: error instanceof Error ? error.message : 'Network error',
    });
  }
}

export async function deactivateFamilymember(userId: string) {
  try {
    const response = await fetch(`${apiUrl}/api/v1/users/${userId}/deactivate`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      let technicalMessage = 'Failed to deactivate family member';

      try {
        const errorData = await response.json();
        technicalMessage = errorData.message || errorData.detail || technicalMessage;
      } catch {
        technicalMessage = response.statusText || technicalMessage;
      }

      throw new AppError({
        title: 'Deactivation Error',
        userMessage: ErrorMessages.MEMBER_DEACTIVATE_FAILED,
        technicalMessage,
      });
    }

    return;
  } catch (error) {
    if (error instanceof AppError) {
      throw error;
    }
    throw new AppError({
      title: 'Connection Error',
      userMessage: ErrorMessages.NETWORK_ERROR,
      technicalMessage: error instanceof Error ? error.message : 'Network error',
    });
  }
}

export async function reactivateFamilymember(userId: string) {
  try {
    const response = await fetch(`${apiUrl}/api/v1/users/${userId}/activate`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      let technicalMessage = 'Failed to reactivate family member';

      try {
        const errorData = await response.json();
        technicalMessage = errorData.message || errorData.detail || technicalMessage;
      } catch {
        technicalMessage = response.statusText || technicalMessage;
      }

      throw new AppError({
        title: 'Reactivation Error',
        userMessage: ErrorMessages.MEMBER_REACTIVATE_FAILED,
        technicalMessage,
      });
    }

    return;
  } catch (error) {
    if (error instanceof AppError) {
      throw error;
    }
    throw new AppError({
      title: 'Connection Error',
      userMessage: ErrorMessages.NETWORK_ERROR,
      technicalMessage: error instanceof Error ? error.message : 'Network error',
    });
  }
}

// export async function deleteFamilymember(userId: string){
//   const result= await fetch(`${apiUrl}/api/v1/users/${userId}`, {
//       method: 'DELETE',
//       headers: { 'Content-Type': 'application/json' },
//     })
//     return result.json()
// }

export async function createNewUser(data: SignupFormData, idempotencyKey: string) {
  const startTime = Date.now();
  try {
    const response = await fetch(`${apiUrl}/api/v1/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey },
      body: JSON.stringify(data),
    });

    const responseData = await response.json();

    if (!response.ok) {
      const technicalMessage =
        responseData.message || responseData.detail || 'Failed to create new user';
      logger.error('api_call_failed', {
        action: 'createNewUser',
        status: response.status,
        error: technicalMessage,
      });
      throw new AppError({
        title: 'Signup Error',
        userMessage: responseData.message || 'Unable to create account. Please try again.',
        technicalMessage,
      });
    }

    logger.info('user_signup_success', {
      duration_ms: Date.now() - startTime,
    });
  } catch (error) {
    if (error instanceof AppError) {
      throw error;
    }
    logger.error('api_call_failed', {
      action: 'createNewUser',
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
