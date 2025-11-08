import { createClient } from "@/lib/supabase/server";

/**
 * Get the current user session from Supabase
 * Use this in Server Components and Server Actions
 */
export async function getSession() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  return user;
}

/**
 * Get the current user from Supabase
 * Use this in Server Components and Server Actions
 */
export async function getUser() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  return user;
}

