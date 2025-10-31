// app/(protected)/layout.tsx

import { redirect } from 'next/navigation';
import { createClient } from '@/lib/supabase/server';

export default async function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createClient();
  
  const { data: { user } } = await supabase.auth.getUser();

  // If not authenticated, redirect to login
  if (!user) {
    redirect('/login');
  }

  return <>{children}</>;
}