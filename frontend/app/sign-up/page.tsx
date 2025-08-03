"use client";

import { SignUp } from '@clerk/nextjs';

export default function SignUpPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 to-blue-600">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full mx-4">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-blue-900 mb-2">🤖 FPL Agent</h1>
          <p className="text-gray-600">Your Fantasy Premier League AI Assistant</p>
        </div>
        <SignUp 
          appearance={{
            elements: {
              formButtonPrimary: 'bg-blue-600 hover:bg-blue-700',
              card: 'shadow-none',
            }
          }}
          routing="hash"
          signInUrl="/"
        />
      </div>
    </div>
  );
}