"use client";

import { Button } from "@/components/ui/button";
import { auth0 } from "@/lib/auth0";

export default async function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {

  const session = await auth0.getSession();
    const handleLogout = () => {
      window.location.href = "/login"; // Redirect to the login page
    };

     if (!session) {
    return (
      <main>
        <a href="/auth/login">Log in</a>
      </main>
    );
  }
  
  return (


    <div>
        <header className="flex items-center justify-between px-6 py-4 border-b bg-white shadow-sm">
            <div className="text-2xl font-bold text-indigo-600">Kaban</div>
            <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">               
                <Button className="cursor-pointer" onClick={handleLogout}>LogOut</Button>
            </nav>
        </header>
    <div>
      {children}
    </div>
    </div>
   
  );
}