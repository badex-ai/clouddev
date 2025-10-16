'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { useUser } from '@auth0/nextjs-auth0';
import { UserProfile, ExtendedUserProfile } from "@/lib/types";
import { getUserData } from '@/lib/actions/userActions';






const UserContext = createContext<UserDataContextType>({
  isUserDataLoading: true,
  userData: null,
  authIsLoading:true,
  userDataError: false,
  // fetchUserData: () => {}
});

  interface UserDataContextType {
  userData: ExtendedUserProfile | null ;
  isUserDataLoading: boolean;
  userDataError: boolean;
  authIsLoading: boolean;
  // fetchUserData: () => void;

}



export const AuthUserProvider = ({ children }: { children: React.ReactNode }) => {
  let { user, isLoading } = useUser();
  const [userData, setUserData] = useState<ExtendedUserProfile | null>(null);
  const [isUserDataLoading, setIsUserDataLoading] = useState(true);
  const [userDataError, setUserDataError] = useState<boolean>(false);



  let authIsLoading = isLoading;


   useEffect(() => {
        if(user?.email){

          fetchUserData(user);
        }
  }, [user]);


  const  fetchUserData = async (user: any) => {
   
        
    try {
    
     
      setIsUserDataLoading(true);
      const userDataResult = await getUserData(user);
      console.log('userDataResult', userDataResult);
      setUserData(userDataResult.data)
      console.log(userDataResult.data, 'userDataResult in context');

    } catch (error) {

   
     
      setUserDataError(true);
  
      setUserData(user)
      console.log(error, 'this is the error from te fetch')
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
        // fetchUserData
        }}>
      {children}
    </UserContext.Provider>
  );
};

export const useAuthUser = () => useContext(UserContext);