
import { Auth0Client } from '@auth0/nextjs-auth0/server'

export async function getUserData() {


  
  const auth0 = new Auth0Client();
   const session = await auth0.getSession();

   if (!session?.user?.email) {
      return Response.json({ error: 'Not authenticated' }, { status: 401 });
    }

  try {
    // Fetch user data
    const userResponse = await fetch(`${process.env.API_URL}/api/v1/users/me`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_email: session?.user?.email })
    })

    if (!userResponse.ok) {
      throw new Error(`Failed to fetch user: ${userResponse.status}`)
    }

    const userData = await userResponse.json()

    const mergedData = {
      ...session.user,
      ...userData
    };

    return { 
      success: true, 
      data: mergedData, 
      status: 200 
    };
    
  } catch (error) {
    console.error('Error fetching user data:', error)
      return { 
      success: false, 
      error: 'Failed to fetch user data', 
      status: 500 
    };
  }
}
