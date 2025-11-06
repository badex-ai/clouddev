'use server';
import { CreateNewFamilyMember } from '@/lib/types';
import { type SignupFormData } from '@/lib/validations/auth';
import { getConfig } from '../config';
import { ApiException , NetworkError} from '../utils';

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
      // console.log(responseData, 'full error from api')
      const errorMessage =
        responseData.message || responseData.detail || 'Failed to create family member';
      // const
      const error = new ApiException('User Profile', errorMessage);

      throw error;
    }

    const mergedData = {
      ...user,
      ...responseData,
    };

    return mergedData;
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

export async function createNewFamilyMember(userInfo: CreateNewFamilyMember) {
  try {
    const response = await fetch(`${apiUrl}/api/v1/users/new`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userInfo),
    });

    const responseData = await response.json();
    // console.log(responseData, 'error from response')

    if (!response.ok) {
      const errorMessage =
        responseData.message || responseData.detail || 'Failed to create family member';
     
      const error = new ApiException('Family member Creation Error', errorMessage);

      throw error;
    }

    return responseData;
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

export async function getFamilymembers(familyId: string) {
  try {
    const response = await fetch(`${apiUrl}/api/v1/families/${familyId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    const responseData = await response.json();

     if (!response.ok) {
    
      const errorMessage =
        responseData.message || responseData.detail || 'Failed to fetch family member';
     
      const error = new ApiException('Family fetch Error', errorMessage);

      throw error;
    }

    return responseData;
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

export async function deactivateFamilymember(userId: string) {
  console.log('Deactivating family member:', userId);

  try {
    const response = await fetch(`${apiUrl}/api/v1/users/${userId}/deactivate`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
    });

    const responseData = await response.json();

     if (!response.ok) {
    
      const errorMessage =
        responseData.message || responseData.detail || 'Failed to deactivate family member';
     
      const error = new ApiException('Family member deactivation Error', errorMessage);

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
    );;
  }
}

export async function reactivateFamilymember(userId: string) {
  try {
    const response = await fetch(`${apiUrl}/api/v1/users/${userId}/activate`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
    });

    const responseData = await response.json();

    if (!response.ok) {
    
      const errorMessage =
        responseData.message || responseData.detail || 'Failed to deactivate family member';
     
      const error = new ApiException('Family member deactivation Error', errorMessage);

      throw error;
    }

   
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

// export async function deleteFamilymember(userId: string){
//   const result= await fetch(`${apiUrl}/api/v1/users/${userId}`, {
//       method: 'DELETE',
//       headers: { 'Content-Type': 'application/json' },
//     })
//     return result.json()
// }

export async function createNewUser(data: SignupFormData, idempotencyKey: string) {
  console.log(apiUrl, 'apiurl');
  console.log('sendin te new user profile', data);
  try {
    const response = await fetch(`${apiUrl}/api/v1/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey },
      body: JSON.stringify(data),
    });

    const responseData = await response.json();


    if (!response.ok) {
    
      const errorMessage =
        responseData.message || responseData.detail || 'Failed to create new user';
     
      const error = new ApiException('Signup Error', errorMessage);

      throw error;
    }
  } catch (error) {
     if (error instanceof ApiException) {
      throw error;
    }

    throw new Error(
     NetworkError
    );
  }
}
