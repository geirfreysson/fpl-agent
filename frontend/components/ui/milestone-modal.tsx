"use client";

import { useEffect } from "react";
import { X, Trophy, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

interface MilestoneModalProps {
  isOpen: boolean;
  onClose: () => void;
  messageCount: number;
}

export function MilestoneModal({ isOpen, onClose, messageCount }: MilestoneModalProps) {
  // Debug logging
  console.log(`MilestoneModal: isOpen=${isOpen}, messageCount=${messageCount}`);
  
  // Close modal on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      // Prevent body scroll when modal is open
      document.body.style.overflow = "hidden";
    }

    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.body.style.overflow = "unset";
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 animate-in fade-in-0" 
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative w-full max-w-md mx-4 bg-background rounded-lg shadow-xl border animate-in fade-in-0 zoom-in-95 slide-in-from-bottom-2">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        >
          <X className="h-4 w-4" />
          <span className="sr-only">Close</span>
        </button>

        {/* Header */}
        <div className="flex flex-col items-center justify-center pt-8 pb-4 px-6">
          <div 
            className="flex items-center justify-center w-16 h-16 rounded-full mb-4 animate-pulse"
            style={{
              background: 'linear-gradient(to right, #a855f7, #ec4899)',
              width: '64px',
              height: '64px'
            }}
          >
            <Trophy 
              className="text-white" 
              size={32}
              style={{
                width: '32px',
                height: '32px',
                color: 'white',
                fill: 'currentColor'
              }}
            />
          </div>
          <h2 className="text-2xl font-bold text-center mb-2 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            Consider buying me a beer!
          </h2>
          <div className="flex items-center gap-2 text-muted-foreground mb-6">
            <Sparkles className="w-4 h-4" />
            <span className="text-sm">You&apos;ve sent {messageCount} messages to the FPL Agent!</span>
            <Sparkles className="w-4 h-4" />
          </div>
        </div>

        {/* Content */}
        <div className="px-6 pb-8 sm:pb-6">
          <div className="space-y-4">
            <p>This free FPL tool costs money to run - each AI response adds up. If it&apos;s helping your game, a beer would keep the lights on!</p>

          </div>

          {/* Action buttons */}
          <div className="flex flex-col gap-2 mt-6" style={{ paddingBottom: '1rem' }}>
            <Button 
              onClick={() => {
                window.open('https://buymeacoffee.com/geirfreysson', '_blank');
                onClose();
              }}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium"
              style={{
                background: 'linear-gradient(to right, #9333ea, #db2777)',
                color: 'white'
              }}
            >
              Of course I&apos;ll buy you a beer!
            </Button>
            <Button 
              variant="outline" 
              onClick={onClose}
              className="w-full"
            >
              I’m the one who never buys their round. Go away.
            </Button>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute -top-2 -left-2 w-4 h-4 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
        <div className="absolute -top-1 -right-3 w-3 h-3 bg-pink-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
        <div className="absolute -bottom-2 -left-3 w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
        <div className="absolute -bottom-1 -right-2 w-2 h-2 bg-yellow-500 rounded-full animate-bounce" style={{ animationDelay: "450ms" }} />
      </div>
    </div>
  );
}