'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { useUser } from '@auth0/nextjs-auth0';
import { UserProfile, ExtendedUserProfile } from "@/lib/types";





const UserContext = createContext<UserDataContextType>({
  isUserDataLoading: true,
  userData: null,
  authIsLoading:true,
  userDataError: false,
  fetchUserData: () => {}
});

  interface UserDataContextType {
  userData: ExtendedUserProfile | null ;
  isUserDataLoading: boolean;
  userDataError: boolean;
  authIsLoading: boolean;
  fetchUserData: () => void;

}



export const AuthUserProvider = ({ children }: { children: React.ReactNode }) => {
  let { user, isLoading } = useUser();
  const [userData, setUserData] = useState<UserProfile | null>(user);
  const [isUserDataLoading, setIsUserDataLoading] = useState(true);
  const [userDataError, setUserDataError] = useState<boolean>(false);

  const authIsLoading = isLoading;


   useEffect(() => {
    console.log('different states of the user', user);
    if (user && !userData) {
      fetchUserData();
      console.log("User is authenticated, fetching user data:", user.sub);
    }
  }, [user]);


  const fetchUserData = async () => {
   

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/me`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_email: user?.email })
      });

    

     
      if (!response.ok) {
        throw new Error(`Failed to fetch user data: ${response.status}`);
      }

    

      const data = await response.json();

     

      const familyRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/family`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ family_id: data?.family.id })
        // body: JSON.stringify({ family_id: 3})

      });

      const family = await familyRes.json();

      // console.log('family',family);
     

      const apiUserData = { ...data,  familyMembers: family.users };
      // const apiUserData = {  familyMembers: family.users };


      console.log("this is the apiuserdata", apiUserData)
              


    
      
      // Merge Auth0 user data with API data
      const mergedUserData: ExtendedUserProfile = {
        ...userProfileFromAuth0,
        ...apiUserData
      };

      console.log('testing to see the merged',mergedUserData)

    

      setUserData(mergedUserData);
      // console.log("User profile fetched successfully:", mergedUserData);

    } catch (error) {
      console.error("Error fetching user data:", error);
      console.log('this is the user data',userData)
      if (user){
      setUserData(user);

      }
      setUserDataError(true);
      console.log('********************* he reach here o jghoahgha')
      setIsUserDataLoading(false);
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
        fetchUserData
        }}>
      {children}
    </UserContext.Provider>
  );
};

export const useAuthUser = () => useContext(UserContext);