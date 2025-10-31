// app/page.tsx

import { redirect } from 'next/navigation';
import { createClient } from '@/lib/supabase/server';

export default async function Home() {
  const supabase = await createClient();
  
  const { data: { user } } = await supabase.auth.getUser();

  // If user is authenticated, redirect to chat
  if (user) {
    redirect('/chat');
  }

  // If not authenticated, redirect to login
  redirect('/login');
}