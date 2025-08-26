import {CreateNewFamilyMember} from '@/lib/types';



export async function getUserData(user: any) {



 
    // Fetch user data
    const userResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/me`, {
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
   const userResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/new`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify( userInfo)
    }) 

    return userResponse.json()
}

export async function getFamilymembers(familyId: number){
  const userResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/family/${familyId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    
    }) 

    return userResponse.json()
}

export async function deleteFamilymember(userId: string){
  const result= await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/${userId}/deactivate`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      cache: "no-store",
    }) 
    return result
}
