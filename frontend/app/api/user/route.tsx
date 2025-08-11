// app/api/user/route.ts
import { getUserData } from '@/lib/actions/userActions';
import { NextResponse } from 'next/server';

export async function GET() {
  const result = await getUserData();

  if (result instanceof Response) {
    return result;
  }

  if (!result.success) {
    return NextResponse.json({ error: result.error }, { status: result.status });
  }

  return NextResponse.json(result.data);
}