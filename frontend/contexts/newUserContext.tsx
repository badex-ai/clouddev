'use client'
import { createContext, useContext, useState, ReactNode } from 'react';

interface UserData {
  [key: string]: any;
}

interface UserContextType {
  userData: UserData | null;
  setUserData: (data: UserData | null) => void;
}

const newUserContext = createContext<UserContextType | undefined>(undefined);

export function UserDataProvider({ 
  children, 
  initialUserData 
}: { 
  children: ReactNode;
  initialUserData: UserData | null;
}) {
  const [userData, setUserData] = useState<UserData | null>(initialUserData);

  return (
    <newUserContext.Provider value={{ userData, setUserData }}>
      {children}
    </newUserContext.Provider>
  );
}

export const useNewAuthUser = () => {
  const context = useContext(newUserContext);
  if (context === undefined) {
    throw new Error('useNewAuthUser must be used within a UserDataProvider');
  }
  return context;
};
