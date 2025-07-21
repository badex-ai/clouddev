'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { useUser } from '@auth0/nextjs-auth0';
import  {UserProfile} from '@/lib/types';



type UserContextType = {
  user: UserProfile | null | undefined;
  isLoading: boolean;
};

const UserContext = createContext<UserContextType>({
  user: undefined,
  isLoading: true,
});

export const AuthUserProvider = ({ children }: { children: React.ReactNode }) => {
  let { user, isLoading } = useUser();
   user;

  return (
    <UserContext.Provider value={{ user, isLoading }}>
      {children}
    </UserContext.Provider>
  );
};

export const useAuthUser = () => useContext(UserContext);