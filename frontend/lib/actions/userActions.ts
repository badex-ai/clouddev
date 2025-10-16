'use server' 
import {CreateNewFamilyMember} from '@/lib/types';
import {getConfig} from "../config"



const {apiUrl, nextUrl} = getConfig()

export async function getUserData(user: any) {


  console.log(apiUrl, 'tis is te api url')
  

  console.log(nextUrl, 'tis is te nextUrl url')

      
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

export async function getFamilymembers(familyId: number){
  const userResponse = await fetch(`${apiUrl}/api/v1/families/${familyId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    
    }) 

    return userResponse.json()
}

export async function deleteFamilymember(userId: string){
  const result= await fetch(`${apiUrl}/api/v1/users/${userId}/deactivate`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      cache: "no-store",
    }) 
    return result
}
