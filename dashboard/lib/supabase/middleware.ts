import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({
    request,
  });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) =>
            request.cookies.set(name, value)
          );
          supabaseResponse = NextResponse.next({
            request,
          });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  // IMPORTANT: Avoid writing any logic between createServerClient and
  // supabase.auth.getUser(). A simple mistake could make it very hard to debug
  // issues with users being randomly logged out.

  // Refresh session if expired - required for Server Components
  // https://supabase.com/docs/guides/auth/server-side/nextjs
  const {
    data: { user },
  } = await supabase.auth.getUser();

  const url = request.nextUrl.clone();
  const isLoggedIn = !!user;
  const isOnDashboard = url.pathname.startsWith("/dashboard");
  const isOnMarkets = url.pathname.startsWith("/markets");
  const isOnSettings = url.pathname.startsWith("/settings");
  const isAuthCallback = url.pathname.startsWith("/auth/callback");

  // Allow auth callback route to proceed without redirect
  if (isAuthCallback) {
    return supabaseResponse;
  }

  // Protect dashboard, markets, and settings routes
  if (isOnDashboard || isOnMarkets || isOnSettings) {
    if (!isLoggedIn) {
      url.pathname = "/";
      return NextResponse.redirect(url);
    }
  } else if (isLoggedIn && url.pathname === "/") {
    // Redirect logged-in users away from landing page
    url.pathname = "/dashboard";
    return NextResponse.redirect(url);
  }

  // IMPORTANT: You *must* return the supabaseResponse object as it is. If you're
  // creating a new response object with NextResponse.next() make sure to:
  // 1. Pass the request in it, like so: const myNewResponse = NextResponse.next({ request })
  // 2. Copy over the cookies, like so: myNewResponse.cookies.setAll(supabaseResponse.cookies.getAll())
  // 3. Change the myNewResponse object to fit your needs, but avoid changing the cookies!
  // 4. Finally: return myNewResponse
  // If this is not done, you may be causing the browser and server to go out of
  // sync and terminate the user's session prematurely.

  return supabaseResponse;
}

