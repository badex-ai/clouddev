'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { useUser } from '@auth0/nextjs-auth0';
import { UserProfile, ExtendedUserProfile } from "@/lib/types";





const UserContext = createContext<UserDataContextType>({
  isUserDataLoading: true,
  userData: undefined,
  authIsLoading:true,
  userDataError: null,
  fetchUserData: () => {}
});

  interface UserDataContextType {
  userData: ExtendedUserProfile | null | undefined;
  isUserDataLoading: boolean;
  userDataError: string | null;
  authIsLoading: boolean;
  fetchUserData: () => void;

}



export const AuthUserProvider = ({ children }: { children: React.ReactNode }) => {
  let { user, isLoading } = useUser();
    const [userData, setUserData] = useState<UserProfile | null>(null);
    const [isUserDataLoading, setIsUserDataLoading] = useState(false);
  const [userDataError, setUserDataError] = useState<string | null>(null);

  const authIsLoading = isLoading;


   useEffect(() => {
    if (user && !userData) {
      fetchUserData(user);
      console.log("User is authenticated, fetching user data:", user);
    }
  }, [user, userData]);


  const fetchUserData = async (userProfile: UserProfile) => {
    setIsUserDataLoading(true);
    setUserDataError(null);

   

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/me`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_email: userProfile.email })
      });

    

     
      if (!response.ok) {
        throw new Error(`Failed to fetch user data: ${response.status}`);
      }

    

      const data = await response.json();

      const familyRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/family`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ family_id: data?.family.id })
      });

      const family = await familyRes.json();

      console.log('family',family);

      const apiUserData = { ...data, ...family };
              


    
      
      // Merge Auth0 user data with API data
      const mergedUserData: ExtendedUserProfile = {
        ...userProfile,
        ...apiUserData
      };

    

      setUserData(mergedUserData);
      console.log("User profile fetched successfully:", mergedUserData);

    } catch (error) {
      console.error("Error fetching user data:", error);
      setUserDataError(error instanceof Error ? error.message : 'Failed to fetch user data');
    } finally {
      setIsUserDataLoading(false);
    }
  };

   user;

  return (
    <UserContext.Provider value={{ 
        isUserDataLoading,
        userData,
        authIsLoading,
        userDataError,
        fetchUserData: () => {}
        }}>
      {children}
    </UserContext.Provider>
  );
};

export const useAuthUser = () => useContext(UserContext);