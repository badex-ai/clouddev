'use client'
import React from 'react'
import Link from "next/link"
import {Button} from "@/components/ui/button"
// import { getSession } from '@auth0/nextjs-auth0/client  ';


function VerifyEmailPage() {

  async function handleResendVerificationEmail() {
      const response = await fetch(`http://localhost:8000/api/v1/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(user.id)
      });

  }

  return (
    <div>
      <h1>Verify Email</h1>
      <p>Please check your email for a verification link.</p>
        <p>If you don't see it, check your spam folder.</p>
        <p>After verification click the login <Link href="/auth/login">here</Link></p>
        <Button  onClick={handleResendVerificationEmail} asChild>
          Resend Verification Email
        </Button>
    </div>
  )
}

export default VerifyEmailPage