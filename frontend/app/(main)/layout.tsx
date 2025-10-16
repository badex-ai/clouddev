"use client";

import { Button } from "@/components/ui/button";
import { auth0 } from "@/lib/auth0";
import Link from "next/link";
import { useRouter } from 'next/navigation';
// import { useUser } from "@auth0/nextjs-auth0";
import { useEffect,useState,createContext, useContext  } from "react";
import { useAuthUser } from '@/contexts/userContext';
import { UserProfile, ExtendedUserProfile } from "@/lib/types";
import {Settings} from  'lucide-react';
import { useUser } from '@auth0/nextjs-auth0'





export default  function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  
  const router = useRouter();
  // fetchUserData
  const { userData, isUserDataLoading, authIsLoading,userDataError } = useAuthUser();


  let { user, isLoading } = useUser();
    
  

  
  useEffect(() => {
    

    
    if (!authIsLoading && !user?.sub) {
      router.push('/auth/login');
    }
    
  }, [userData, authIsLoading]);
  
  
  
 
  const refetchUserData = () => {

    if (userData?.role) {
      // fetchUserData();
    }
  };
 

   if (userDataError) {
    return       <div className="min-h-screen flex flex-col">
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
      </div>;
  }


 
 

     
  


  
  return (
    <div>
      { userData?.id && !isUserDataLoading &&  <div className="min-h-screen flex flex-col">
        <header className="flex items-center justify-between px-6 py-4 border-b bg-white shadow-sm">
          <div>
            <Link href="/dashboard">
              <div className="text-2xl font-bold text-indigo-600">
                Kaban
              </div>
            </Link>
          </div>
          
          <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
            {userData && (
              <span className="text-gray-700">
                Welcome, {userData.username || userData.name || userData.email}
              </span>
            )}
            <Link href="/settings" className="flex items-center hover:text-blue-800">
               <Settings className="cursor-pointer" />
            </Link>
           
            <Button className="cursor-pointer" asChild>
              <Link href="/auth/logout">LogOut</Link>
            </Button>
          </nav>
        </header>
        <div className="flex-1">
          {children}
        </div>
      </div>
           
      }
    </div>
 
    
    
  );
}