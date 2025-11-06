'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { signupSchema, type SignupFormData } from '@/lib/validations/auth';
import { toast } from 'sonner';
import { getConfig } from '../../../lib/config';
import { createNewUser } from '../../../lib/actions/userActions';
import { v4 as uuidv4 } from 'uuid';

export default function SignupPage() {
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
  });

  function generateIdempotencyKey(): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 15);
    return `signup-${timestamp}-${random}`;
  }

  const onSubmit = async (data: SignupFormData) => {
    setIsLoading(true);
    // console.log(data, 'SINPU BUTTON CLICKED');

   
    try {
      const idempotencyKey = `signup-${data.email}-${uuidv4()}`;

      const response = await createNewUser(data, idempotencyKey);
      console.log(response, 'tis is te response');
      // Add your registration logic

      window.location.href = '/verify';
      // toast('Signup successful! Please verify your email.');
     
  toast('Signup successful!', {
    description: 'Please ceck your email and verify ' ,
    action: {
      label: "Close",
      onClick: () => {
        toast.dismiss();
      },
    },
    duration: 4000, // in ms (default is 4000)
  });
} catch (error) {
  // console.error('Signup error:', error);
  const message = error instanceof Error ? error.message : String(error);
  toast('Signup failed', {
    description: message,
    action: {
      label: "Close",
      onClick: () => {
        toast.dismiss();
      },
    },
    duration: 4000, // in ms (default is 4000)
  });
} finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Kanban</h1>
          <p className="text-gray-600">Create your productivity workspace</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Create your account</CardTitle>
            <CardDescription>Get started with your new workspace</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="fullName">Full Name</Label>
                <Input
                  id="fullName"
                  type="text"
                  placeholder="Enter your full name"
                  {...register('name')}
                  className={errors.name ? 'border-red-500' : ''}
                />
                {errors.name && <p className="text-sm text-red-600">{errors.name.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="family">Family Name</Label>
                <Input
                  id="family"
                  type="text"
                  placeholder="Enter your family name"
                  {...register('family_name')}
                  className={errors.family_name ? 'border-red-500' : ''}
                />
                {errors.family_name && (
                  <p className="text-sm text-red-600">{errors.family_name.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email address"
                  {...register('email')}
                  className={errors.email ? 'border-red-500' : ''}
                />
                {errors.email && <p className="text-sm text-red-600">{errors.email.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Create a password"
                  {...register('password')}
                  className={errors.password ? 'border-red-500' : ''}
                />
                {errors.password && (
                  <p className="text-sm text-red-600">{errors.password.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="Confirm your password"
                  {...register('confirmPassword')}
                  className={errors.confirmPassword ? 'border-red-500' : ''}
                />
                {errors.confirmPassword && (
                  <p className="text-sm text-red-600">{errors.confirmPassword.message}</p>
                )}
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? 'Creating account...' : 'Create account'}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="text-center">
          <p className="text-sm text-gray-600">
            Already have an account? {/* "/auth/login?returnTo=/dashboard" */}
            <Link href="/auth/login" className="font-medium text-blue-600 hover:text-blue-500">
              Sign in here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
