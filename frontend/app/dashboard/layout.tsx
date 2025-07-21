"use client";

import { Button } from "@/components/ui/button";
import { auth0 } from "@/lib/auth0";
import Link from "next/link";
import { useRouter } from 'next/navigation';
// import { useUser } from "@auth0/nextjs-auth0";
import { useEffect } from "react";
import { useAuthUser } from '@/contexts/userContext';


export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const { user, isLoading } = useAuthUser();
  // const session = await auth0.getSession();


  const router = useRouter();

  useEffect(() => {
  console.log('this is the user:', user);

    if (!isLoading && !user) {
      console.log("User not found, redirecting to login");
      router.push('/auth/login');
    }
  }, [user, isLoading, router]);

  console.log("User:", user);

   if (isLoading) {
    return <div>Loading...</div>;
  }

   if (!user) {
    return null; // avoid rendering the layout until redirect happens
  }
  
  return (


    <div>
        <header className="flex items-center justify-between px-6 py-4 border-b bg-white shadow-sm">
            <div className="text-2xl font-bold text-indigo-600">Kaban</div>
            <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">               
                <Button className="cursor-pointer" asChild>
                   <Link href="/auth/logout">LogOut</Link>
                </Button>
            </nav>
        </header>
    <div>
      {children}
    </div>
    </div>
   
  );
}