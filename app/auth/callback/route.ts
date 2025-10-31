// app/auth/callback/route.ts

import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get('code');
  const origin = requestUrl.origin;

  if (code) {
    const supabase = await createClient();
    
    // Exchange code for session
    const { data, error } = await supabase.auth.exchangeCodeForSession(code);
    
    if (error) {
      console.error('Auth callback error:', error);
      return NextResponse.redirect(`${origin}/login?error=auth_failed`);
    }

    if (data.user) {
      // Check if customer record exists
      const { data: existingCustomer } = await supabase
        .from('customers')
        .select('id')
        .eq('user_id', data.user.id)
        .single();

      // Create customer record if it doesn't exist
      if (!existingCustomer) {
        const { error: insertError } = await supabase
          .from('customers')
          .insert({
            user_id: data.user.id,
            email: data.user.email!,
            full_name: data.user.user_metadata.full_name || data.user.user_metadata.name || 'User',
            pan_number: null,
            kyc_status: 'pending',
          });

        if (insertError) {
          console.error('Error creating customer:', insertError);
          // Continue anyway - we can create customer later
        }
      }
    }

    // Redirect to chat
    return NextResponse.redirect(`${origin}/chat`);
  }

  // No code present, redirect to login
  return NextResponse.redirect(`${origin}/login`);
}
