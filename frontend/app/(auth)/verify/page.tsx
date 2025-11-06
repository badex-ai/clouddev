'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useUser } from '@auth0/nextjs-auth0';
import { Mail, AlertCircle, CheckCircle, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';
import { getConfig } from '../../../lib/config';

const { apiUrl } = getConfig();

function VerifyEmailPage() {
  let { user } = useUser();
  console.log('User:', user);
  const [isLoading, setisLoading] = useState(false);

  function disableBtn() {}
  async function handleResendVerificationEmail(id: string) {
    setisLoading(true);

    try{

         const response = await fetch(`${apiUrl}/api/v1/auth/emailVerification`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: id }),
    });

     toast('Email Verification Sent', {
          description: 'Email verification email as been sent again.',
         action: {
            label: 'Close',
            onClick: () => {
              toast.dismiss();
            },
        },
          duration: 4000,
        });
     
    }catch(error){

     const message = error instanceof Error ? error.message : String(error);
      toast('Error sendin email verfication', {
       description: message,
       action: {
         label: 'Close',
         onClick: () => {
           toast.dismiss();
         },
       },
       duration: 4000,
     });
    }finally{
       setisLoading(false);
    }
 
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
                {user && (
                  <Button
                    onClick={() => handleResendVerificationEmail(user?.sub)}
                    className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium py-2.5 rounded-lg shadow-md hover:shadow-lg transition-all duration-200 transform hover:scale-[1.02]"
                  >
                    {isLoading ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />{' '}
                      </>
                    ) : (
                      'Resend Verification Email'
                    )}
                  </Button>
                )}
              </div>
            </div>

            <div className="text-center pt-4 border-t border-gray-100">
              <p className="text-xs text-gray-500">Having trouble? Contact our support team</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default VerifyEmailPage;
