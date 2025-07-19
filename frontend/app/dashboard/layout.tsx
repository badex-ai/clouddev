"use client";

import { Button } from "@/components/ui/button";
import { auth0 } from "@/lib/auth0";
import Link from "next/link";

export default async function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {

  const session = await auth0.getSession();
  
    const handleLogout = () => {
      window.location.href = "/logout"; // Redirect to the logout page
    };

     if (!session) {
    window.location.href = "/login";
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