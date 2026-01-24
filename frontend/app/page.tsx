// components/LandingPage.tsx
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { auth0 } from '@/lib/auth0';
import { redirect } from 'next/navigation';
import { format } from 'date-fns';

export default async function LandingPage() {
  const session = await auth0.getSession();
  const today = format(new Date(), 'yyyy-MM-dd');
  const RELEASE = process.env.NEXT_PUBLIC_RELEASE;

  if (session) {
    redirect(`/dashboard?d=${today}`);
  }

  //  console.log('this is the session', session);
  return (
    <div>
      {!session && (
        <div className="min-h-screen flex flex-col bg-background text-foreground">

          {/* Header */}
          <header className="flex items-center justify-between px-6 py-4 border-b bg-white shadow-sm">
            <div className="text-2xl font-bold text-indigo-600">Kaban</div>
            <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
              <a href="#about" className="hover:text-indigo-600 transition-colors">
                About
              </a>
              <a href="/auth/login" className="hover:text-indigo-600 transition-colors">
                Login
              </a>
              <a href="/signup" className="hover:text-indigo-600 transition-colors">
                Sign Up
              </a>

              <a
                href="https://github.com/your-github-project-link"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-indigo-600 transition-colors"
              >
                GitHub
              </a>
            </nav>
          </header>

          {RELEASE === "CANARY" && (
          <div style={{ paddingLeft: '12px' }}>
            <div className="bg-gradient-to-r from-blue-500 to-blue-700 px-6 py-1.5 inline-block shadow-md rounded-br rounded-bl">
              <span className="text-white text-sm font-bold tracking-widest">CANARY</span>
            </div>
          </div>
          )}

          <main className="flex-grow flex items-center justify-center px-6 py-16">
            <div className="max-w-2xl text-center">
              <h1 className="text-4xl font-bold mb-4">Organize Your Work Visually with Kaban</h1>
              <p className="text-lg text-muted-foreground mb-6">
                Kaban is a sleek, powerful Kanban-style project management tool that helps you
                visualize your tasks, streamline your workflow, and boost team productivity. Manage
                tasks from "To Do" to "Done" with intuitive drag-and-drop boards.
              </p>
              <Button asChild>
                <a href="signup">Get Started</a>
              </Button>
            </div>
          </main>

          <Separator className="w-full" />

          <footer className="text-center text-sm text-muted-foreground py-4">
            © {new Date().getFullYear()} Kaban. All rights reserved.
          </footer>
        </div>
      )}
    </div>
  );
}
