import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";
import { type NextRequest } from "next/server";

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");
  const next = requestUrl.searchParams.get("next") || "/dashboard";

  if (code) {
    const supabase = await createClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    
    if (!error) {
      // Successfully exchanged code for session, redirect to dashboard
      return NextResponse.redirect(new URL(next, request.url));
    }
  }

  // If no code or exchange failed, redirect to dashboard anyway
  // The middleware will handle auth state
  return NextResponse.redirect(new URL(next, request.url));
}

