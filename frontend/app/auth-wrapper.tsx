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
      <div className="min-h-screen bg-white">
        <div className="min-h-screen flex flex-col lg:flex-row max-w-[1150px] mx-auto">
          {/* Left side - Login */}
          <div className="flex-1 flex items-center justify-center p-6 lg:p-4 lg:pr-2">
            <div className="w-full max-w-md">
              <div className="text-center mb-8">
                <div className="flex justify-center mb-6">
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
              <div className="flex justify-center">
                <SignIn 
                  appearance={{
                    elements: {
                      formButtonPrimary: 'bg-blue-600 hover:bg-blue-700',
                      card: 'shadow-none border-none',
                    }
                  }}
                  routing="hash"
                  signUpUrl="/sign-up"
                />
              </div>
            </div>
          </div>
          
          {/* Right side - Video */}
          <div className="flex-1 bg-white flex items-center justify-center p-6 lg:p-4 lg:pl-2">
            <div className="w-full max-w-2xl" style={{marginTop: '10px'}}>
              <video 
                className="w-full h-auto max-h-[42rem] object-contain rounded-lg"
                autoPlay
                muted
                loop
                playsInline
              >
                <source src="/assets/fpl-with-robots-v2-frontpage-video.mp4" type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Signed in - show app
  return <>{children}</>;
}