import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Routes that don't require authentication
const PUBLIC_ROUTES = [
  '/landing',
  '/auth/login',
  '/auth/register',
  '/auth/callback',
];

// Routes that require admin role
const ADMIN_ROUTES = [
  '/admin',
];

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const token = request.cookies.get('access_token')?.value;
  const userRole = request.cookies.get('user-role')?.value;

  // Allow public routes without authentication
  if (PUBLIC_ROUTES.some(route => pathname.startsWith(route))) {
    return NextResponse.next();
  }

  // Redirect root to landing page
  if (pathname === '/') {
    if (token) {
      return NextResponse.next(); // Go to dashboard
    }
    return NextResponse.redirect(new URL('/landing', request.url));
  }

  // Check if user is authenticated for protected routes
  if (!token) {
    // Redirect to login if trying to access protected route
    if (pathname.startsWith('/dashboard') || ADMIN_ROUTES.some(route => pathname.startsWith(route))) {
      return NextResponse.redirect(new URL('/auth/login', request.url));
    }
  }

  // Check admin routes
  if (ADMIN_ROUTES.some(route => pathname.startsWith(route))) {
    if (!token) {
      return NextResponse.redirect(new URL('/auth/login', request.url));
    }
    if (userRole !== 'admin' && userRole !== 'superuser') {
      return NextResponse.redirect(new URL('/', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|api).*)',
  ],
};
