import React from 'react'
import Link from "next/link"

function VerifyEmailPage() {
  return (
    <div>
      <h1>Verify Email</h1>
      <p>Please check your email for a verification link.</p>
        <p>If you don't see it, check your spam folder.</p>
        <p>After verification click the login <Link href="/auth/login">here</Link></p>
    </div>
  )
}

export default VerifyEmailPage() 