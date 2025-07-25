"use client";

import { Button } from "@/components/ui/button";
import { auth0 } from "@/lib/auth0";
import Link from "next/link";
import { useRouter } from 'next/navigation';
// import { useUser } from "@auth0/nextjs-auth0";
import { useEffect,useState,createContext, useContext  } from "react";
import { useAuthUser } from '@/contexts/userContext';
import { UserProfile, ExtendedUserProfile } from "@/lib/types";


  interface UserDataContextType {
  userData: ExtendedUserProfile | null;
  isUserDataLoading: boolean;
  userDataError: string | null;

}

const UserDataContext = createContext<UserDataContextType | undefined>(undefined);

// Custom hook for children to access user data
export const useUserData = () => {
  const context = useContext(UserDataContext);
  if (context === undefined) {
    throw new Error('useUserData must be used within a DashboardLayout');
  }
  return context;
};




export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const { userData, isUserDataLoading, authIsLoading,userDataError, fetchUserData } = useAuthUser();
  
  // const session = await auth0.getSession();

  //  const [userData, setUserData] = useState<UserProfile | null>(null);
  //   const [isUserDataLoading, setIsUserDataLoading] = useState(false);
  // const [userDataError, setUserDataError] = useState<string | null>(null);

  const router = useRouter();




  useEffect(() => {


    if (!isUserDataLoading && !userData) {
      console.log("User not found, redirecting to login");
      // router.push('/auth/login');
    }
  }, [userData, authIsLoading, router]);

  let resp;

//  useEffect(() => {
//     if (user && !userData) {
//       fetchUserData(user);
//       console.log("User is authenticated, fetching user data:", user);
//     }
//   }, [user, userData]);

 
  const refetchUserData = () => {

    if (userData.role) {
      fetchUserData(userData.sub);
    }
  };
 


  

   if (authIsLoading) {
    return <div>Loading...</div>;
  }

   if (!userData?.sub) {
    return null; // avoid rendering the layout until redirect happens
  }



    if (userDataError) {
    return (

      <div className="min-h-screen flex flex-col">
        <header className="flex items-center justify-between px-6 py-4 border-b bg-white shadow-sm">
          <div className="text-2xl font-bold text-indigo-600">Kaban</div>
          <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">               
            <Button className="cursor-pointer" asChild>
              <Link href="/auth/logout">LogOut</Link>
            </Button>
          </nav>
        </header>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-xl font-semibold text-red-600 mb-2">Error loading user data</h2>
            <p className="text-gray-600 mb-4">{userDataError}</p>
            <Button onClick={refetchUserData}>Try Again</Button>
          </div>
        </div>
      </div>
    );
  }
  
  return (
   
      <div className="min-h-screen flex flex-col">
        <header className="flex items-center justify-between px-6 py-4 border-b bg-white shadow-sm">
          <div className="text-2xl font-bold text-indigo-600">Kaban</div>
          <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
            {userData && (
              <span className="text-gray-700">
                Welcome, {userData.username || userData.name || userData.email}
              </span>
            )}
            <Button className="cursor-pointer" asChild>
              <Link href="/auth/logout">LogOut</Link>
            </Button>
          </nav>
        </header>
        <div className="flex-1">
          {children}
        </div>
      </div>
    
  );
}