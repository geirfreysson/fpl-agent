"use client";

import { AssistantRuntimeProvider, useThread } from "@assistant-ui/react";
import { useChatRuntime } from "@assistant-ui/react-ai-sdk";
import { Thread } from "@/components/assistant-ui/thread";
import { UserButton, useAuth } from "@clerk/nextjs";
import Image from "next/image";
import Link from "next/link";
import { useMessageCounter } from "@/hooks/use-message-counter";
import { MilestoneModal } from "@/components/ui/milestone-modal";
import { VersionTracker } from "@/components/version-tracker";
import { useEffect, useRef } from "react";
import { Bookmark } from "lucide-react";
// Commented out for simple layout - uncomment to restore sidebar functionality
// import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
// import { AppSidebar } from "@/components/app-sidebar";
// import { Separator } from "@/components/ui/separator";
// import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb";

// Component to monitor messages and trigger counter
const MessageMonitor = ({ incrementCounter }: { incrementCounter: () => void }) => {
  const thread = useThread({ optional: true });
  const previousMessageCountRef = useRef(0);

  useEffect(() => {
    if (!thread) return;
    
    const currentCount = thread.messages.length;
    const previousCount = previousMessageCountRef.current;
    
    console.log(`Thread messages: ${currentCount}, previous: ${previousCount}`);
    
    // Check if a new assistant message was added
    if (currentCount > previousCount && currentCount > 0) {
      const newMessage = thread.messages[currentCount - 1];
      console.log(`New message role: ${newMessage.role}`);
      
      // Increment when an assistant message is added
      if (newMessage.role === "assistant") {
        console.log('Assistant message detected, incrementing counter');
        incrementCounter();
      }
    }
    
    previousMessageCountRef.current = currentCount;
  }, [thread?.messages.length, incrementCounter, thread]);

  return null;
};

export const Assistant = () => {
  const { getToken, isSignedIn } = useAuth();
  const { messageCount, showModal, incrementCounter, closeModal } = useMessageCounter();
  
  const runtime = useChatRuntime({
    api: "/api/chat",
    headers: async (): Promise<Record<string, string>> => {
      if (!isSignedIn) {
        return {};
      }
      
      const token = await getToken();
      if (!token) {
        return {};
      }
      
      return {
        "Authorization": `Bearer ${token}`,
      };
    },
    onFinish: () => {
      // Increment counter when assistant completes a response
      console.log('onFinish callback triggered');
      incrementCounter();
    },
  });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <MessageMonitor incrementCounter={incrementCounter} />
      <VersionTracker />
      <div className="relative h-screen flex flex-col">
        {/* Header with branding and sign out button */}
        <header className="flex items-center justify-between p-4 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Image 
                src="/assets/logo.svg" 
                alt="FPL With Robots Logo" 
                width={32} 
                height={32}
                className="w-8 h-8"
              />
              <h1 className="text-xl font-semibold text-foreground">FPL With Robots</h1>
            </div>
            <div className="text-sm text-muted-foreground hidden sm:block">
              Your Fantasy Premier League AI Assistant
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Link 
              href="/releases" 
              className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted rounded-md transition-colors"
            >
              <Bookmark className="w-4 h-4" />
              <span className="hidden sm:inline">Releases</span>
            </Link>
            <UserButton 
              appearance={{
                elements: {
                  avatarBox: "w-10 h-10"
                }
              }}
              showName={false}
            />
          </div>
        </header>
        <div className="flex-1 overflow-hidden">
          <Thread />
        </div>
      </div>
      
      {/* Milestone Modal */}
      <MilestoneModal 
        isOpen={showModal} 
        onClose={closeModal} 
        messageCount={messageCount} 
      />
      
      {/* Commented out sidebar layout - uncomment to restore:
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset>
          <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
            <SidebarTrigger />
            <Separator orientation="vertical" className="mr-2 h-4" />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem className="hidden md:block">
                  <BreadcrumbLink href="#">
                    Build Your Own ChatGPT UX
                  </BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator className="hidden md:block" />
                <BreadcrumbItem>
                  <BreadcrumbPage>
                    Starter Template
                  </BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </header>
          <Thread />
        </SidebarInset>
      </SidebarProvider>
      */}
    </AssistantRuntimeProvider>
  );
};
