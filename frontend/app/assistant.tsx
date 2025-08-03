"use client";

import { AssistantRuntimeProvider } from "@assistant-ui/react";
import { useChatRuntime } from "@assistant-ui/react-ai-sdk";
import { Thread } from "@/components/assistant-ui/thread";
import { UserButton, useAuth } from "@clerk/nextjs";
// Commented out for simple layout - uncomment to restore sidebar functionality
// import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
// import { AppSidebar } from "@/components/app-sidebar";
// import { Separator } from "@/components/ui/separator";
// import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb";

export const Assistant = () => {
  const { getToken, isSignedIn } = useAuth();
  
  const runtime = useChatRuntime({
    api: "/api/chat",
    headers: async () => {
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
  });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div className="relative h-screen flex flex-col">
        {/* Header with branding and sign out button */}
        <header className="flex items-center justify-between p-4 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">FPL</span>
              </div>
              <h1 className="text-xl font-semibold text-foreground">FPL Agent</h1>
            </div>
            <div className="text-sm text-muted-foreground hidden sm:block">
              Your Fantasy Premier League AI Assistant
            </div>
          </div>
          <UserButton 
            appearance={{
              elements: {
                avatarBox: "w-10 h-10"
              }
            }}
            showName={false}
          />
        </header>
        <div className="flex-1 overflow-hidden">
          <Thread />
        </div>
      </div>
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
