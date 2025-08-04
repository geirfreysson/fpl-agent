"use client";

import { useAuth, SignIn } from '@clerk/nextjs';
import { ReactNode } from 'react';
import Image from 'next/image';

interface AuthWrapperProps {
  children: ReactNode;
}

export function AuthWrapper({ children }: AuthWrapperProps) {
  const { isLoaded, isSignedIn } = useAuth();

  // Loading state
  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-white text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Not signed in - show sign in
  if (!isSignedIn) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full mx-4">
          <div className="text-center mb-6">
            <div className="flex justify-center mb-4">
              <Image 
                src="/assets/login-logo.svg" 
                alt="FPL Agent" 
                width={80} 
                height={80}
                className="w-20 h-20"
              />
            </div>
            <h1 className="text-3xl font-bold text-blue-900 mb-2">FPL With Robots</h1>
            <p className="text-gray-600">Your Fantasy Premier League AI Assistant</p>
          </div>
          <SignIn 
            appearance={{
              elements: {
                formButtonPrimary: 'bg-blue-600 hover:bg-blue-700',
                card: 'shadow-none',
              }
            }}
            routing="hash"
            signUpUrl="/sign-up"
          />
        </div>
      </div>
    );
  }

  // Signed in - show app
  return <>{children}</>;
}