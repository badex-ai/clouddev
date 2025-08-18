

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
