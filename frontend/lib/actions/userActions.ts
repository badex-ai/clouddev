'use server' 
import {CreateNewFamilyMember} from '@/lib/types';
import {type SignupFormData } from "@/lib/validations/auth"
import {getConfig} from "../config"



const {apiUrl, nextUrl} = getConfig()

export async function getUserData(user: any) {


      
    // Fetch user data
    const userResponse = await fetch(`${apiUrl}/api/v1/users/me`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_email: user.email })
    })

    if (!userResponse.ok) {
      throw new Error(`Failed to fetch user: ${userResponse.status}`)
    }

    const userData = await userResponse.json()


    const mergedData = {
      ...user,
      ...userData
    };

    return { 
      success: true, 
      data: mergedData, 
      status: 200 
    };
    
  
}


export async function createNewFamilyMember(userInfo: CreateNewFamilyMember){
   const userResponse = await fetch(`${apiUrl}/api/v1/users/new`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify( userInfo)
    }) 

    return userResponse.json()
}

export async function getFamilymembers(familyId: string){
  const userResponse = await fetch(`${apiUrl}/api/v1/families/${familyId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    
    }) 

    return userResponse.json()
}

export async function deactivateFamilymember(userId: string){
  const result= await fetch(`${apiUrl}/api/v1/users/${userId}/deactivate`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
    }) 
    return result.json()
}

export async function reactivateFamilymember(userId: string){
  const result= await fetch(`${apiUrl}/api/v1/users/${userId}/activate`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
    }) 
    return result.json()
}

// export async function deleteFamilymember(userId: string){
//   const result= await fetch(`${apiUrl}/api/v1/users/${userId}`, {
//       method: 'DELETE',
//       headers: { 'Content-Type': 'application/json' },
//     }) 
//     return result.json()
// }


export async function createNewUser(data:SignupFormData ){
  console.log(apiUrl, 'apiurl')
  console.log('sendin te new user profile', data)

 const result = await fetch(`${apiUrl}/api/v1/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

 return result.json()

}