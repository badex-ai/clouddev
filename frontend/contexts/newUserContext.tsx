import { createContext, useContext, useState, ReactNode } from 'react';

interface UserData {
  [key: string]: any;
}

interface UserContextType {
  userData: UserData | null;
  setUserData: (data: UserData | null) => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserDataProvider({ 
  children, 
  initialUserData 
}: { 
  children: ReactNode;
  initialUserData: UserData | null;
}) {
  const [userData, setUserData] = useState<UserData | null>(initialUserData);

  return (
    <UserContext.Provider value={{ userData, setUserData }}>
      {children}
    </UserContext.Provider>
  );
}

export const useAuthUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useAuthUser must be used within a UserDataProvider');
  }
  return context;
};
