'use client';

import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useUser } from '@auth0/nextjs-auth0';
import { ExtendedUserProfile } from '@/lib/types';
import { getUserData } from '@/lib/actions/userActions';
import { toast } from 'sonner';

interface UserDataContextType {
  userData: ExtendedUserProfile | null;
  isUserDataLoading: boolean;
  userDataError: boolean;
  authIsLoading: boolean;
  refetchUserData: () => void;
}

const UserContext = createContext<UserDataContextType>({
  isUserDataLoading: true,
  userData: null,
  authIsLoading: true,
  userDataError: false,
  refetchUserData: () => {},
});

export const AuthUserProvider = ({ children }: { children: React.ReactNode }) => {
  let { user, isLoading } = useUser();
  const [userData, setUserData] = useState<ExtendedUserProfile | null>(null);
  const [isUserDataLoading, setIsUserDataLoading] = useState(true);
  const [userDataError, setUserDataError] = useState<boolean>(false);

  let authIsLoading = isLoading;

  useEffect(() => {
    if (user?.email) {
      fetchUserData(user);
    }
  }, [user]);

  const fetchUserData = useCallback(async (authUser: typeof user) => {
    if (!authUser?.email) return;

    try {
      setIsUserDataLoading(true);
      setUserDataError(false);
      const userDataResult = await getUserData(authUser);
      setUserData(userDataResult);
    } catch (error) {
      setUserDataError(true);
      setUserData(authUser as ExtendedUserProfile);
      const errorMessage = error instanceof Error ? error.message : 'An unexpected error occurred';
      toast.error('User Profile Error', { description: errorMessage });
    } finally {
      setIsUserDataLoading(false);
    }
  }, []);

  const refetchUserData = useCallback(() => {
    if (user) {
      fetchUserData(user);
    }
  }, [user, fetchUserData]);

  return (
    <UserContext.Provider
      value={{
        isUserDataLoading,
        userData,
        authIsLoading,
        userDataError,
        refetchUserData,
      }}
    >
      {children}
    </UserContext.Provider>
  );
};

export const useAuthUser = () => useContext(UserContext);
