'use client'
import React, { useState } from 'react'
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useUser } from "@auth0/nextjs-auth0"
import { Mail, AlertCircle, CheckCircle, RefreshCw } from "lucide-react"
import { toast } from "sonner"

function VerifyEmailPage() {
  let { user } = useUser();
  console.log("User:", user);
  const [isLoading, setisLoading] = useState(false)

  function disableBtn(){
    
  }
  async function handleResendVerificationEmail(id: string) {
    setisLoading(true);
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/emailVerification`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: id })
    });
    if (response.ok) {
      toast("Email Verification Sent");
      setisLoading(false);
    } else {
      toast("Something went wrong, please try again later");
      setisLoading(false);
    }
    console.log('verification clicked');
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="shadow-2xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="text-center pb-6">
            <div className="mx-auto mb-4 w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
              <Mail className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
              Verify Your Email
            </CardTitle>
            <CardDescription className="text-gray-600 mt-2">
              We've sent a verification link to your email address
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-6">
           

            <div className="text-center space-y-4">
              <p className="text-sm text-gray-600">
                After verification, you can{' '}
                <Link 
                  href="/auth/login" 
                  className="font-medium text-blue-600 hover:text-blue-500 underline underline-offset-4 transition-colors"
                >
                  login here
                </Link>
              </p>

              <div className="pt-4">
                <Button 
                  onClick={() => handleResendVerificationEmail(user.sub)}
                  className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium py-2.5 rounded-lg shadow-md hover:shadow-lg transition-all duration-200 transform hover:scale-[1.02]"
                >
                  {isLoading ? 
                    <><RefreshCw className="w-4 h-4 mr-2 animate-spin" /> </> : (
                    "Resend Verification Email"
                   )
                  }
                 
                </Button>
              </div>
            </div>

            <div className="text-center pt-4 border-t border-gray-100">
              <p className="text-xs text-gray-500">
                Having trouble? Contact our support team
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default VerifyEmailPage