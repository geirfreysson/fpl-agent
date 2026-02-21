"use client";

import { ChevronRight, BarChart3, Users, Target, Trophy, ArrowRight, Quote } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SignIn } from '@clerk/nextjs';

export function LandingPage() {

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="pt-12 pb-12 lg:pt-20 lg:pb-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-3 lg:gap-16 xl:gap-20 items-center min-h-[80vh]">
            
            {/* Login Form - Left Side (1/3) */}
            <div className="lg:col-span-1 mb-12 lg:mb-0">
              {/* Badge */}
              <div className="inline-flex items-center px-3 py-1 rounded-full bg-accent text-accent-foreground mb-6">
                <Trophy className="h-4 w-4 mr-2" />
                AI-Powered FPL Analysis
              </div>

              {/* Main Headline */}
              <h1 className="text-3xl md:text-4xl lg:text-4xl xl:text-5xl font-bold text-foreground mb-6">
                Master <span className="text-primary">Fantasy Premier League</span> with AI
              </h1>

              {/* Sub-headline */}
              <p className="text-lg text-muted-foreground mb-8" id="reference-text">
                Get data-driven insights, player recommendations, and strategic advice from our advanced AI assistant.
              </p>

              {/* Login Form */}
              <div className="mb-8"
                   style={{ maxWidth: '420px', width: '100%' }}>
                <style jsx global>{`
                  /* Calculate reference text width and apply to form */
                  :root {
                    --reference-width: 100%;
                  }

                  @media (min-width: 768px) {
                    :root {
                      --reference-width: 420px;
                    }
                  }
                  .cl-signIn-root {
                    box-shadow: none !important;
                    border: none !important;
                    background: transparent !important;
                    max-width: 100% !important;
                    width: 100% !important;
                  }
                  
                  .cl-signIn-start {
                    box-shadow: none !important;
                    border: none !important;
                    background: transparent !important;
                    padding: 0 !important;
                    max-width: 100% !important;
                    width: 100% !important;
                  }
                  
                  .cl-card {
                    text-align: left !important;
                  }
                  
                  /* Hide social login buttons */
                  .cl-socialButtonsRoot,
                  .cl-dividerRow {
                    display: none !important;
                  }
                  
                  .cl-footer,
                  [data-clerk-component="SignIn"] .cl-footer {
                    display: none !important;
                  }
                  
                  .cl-main,
                  [data-clerk-component="SignIn"] .cl-main {
                    padding: 0 !important;
                    width: auto !important;
                  }
                  
                  .cl-header,
                  [data-clerk-component="SignIn"] .cl-header {
                    padding: 0 !important;
                    margin-bottom: 0rem !important;
                  }
                  .cl-headerSubtitle{
                    display: none !important;
                  }
                  
                  .cl-formField,
                  .cl-formFieldInput,
                  [data-clerk-component="SignIn"] .cl-formField,
                  [data-clerk-component="SignIn"] .cl-formFieldInput {
                    width: 99% !important;
                    max-width: none !important;
                  }
                  
                  input[placeholder="Enter your email address"] {
                    position: relative !important;
                    left: 2px !important;
                  }
                  
                  .cl-formButtonPrimary,
                  [data-clerk-component="SignIn"] .cl-formButtonPrimary {
                    width: 99% !important;
                    max-width: none !important;
                    border-radius: 6px !important;
                    position: relative !important;
                    bottom: 8px !important;
                    left: 2px !important;
                  }
                `}</style>
                <SignIn 
                  appearance={{
                    elements: {
                      formButtonPrimary: 'bg-primary hover:bg-primary/90 text-primary-foreground border-none shadow-none',
                      card: 'shadow-none border-none bg-transparent p-0',
                      cardBox: 'shadow-none border-none bg-transparent',
                      rootBox: 'shadow-none border-none bg-transparent',
                      headerTitle: 'text-foreground text-lg font-semibold',
                      headerSubtitle: 'text-muted-foreground text-sm',
                      socialButtonsBlockButton: 'border-border hover:bg-accent shadow-none',
                      formFieldLabel: 'text-foreground text-sm',
                      formFieldInput: 'border-border focus:ring-primary/20 shadow-none bg-background',
                      footerActionText: 'text-muted-foreground text-sm',
                      footerActionLink: 'text-primary hover:text-primary/80',
                      footer: 'hidden',
                      main: 'p-0',
                      header: 'p-0 mb-4',
                    }
                  }}
                  routing="hash"
                  signUpUrl="/sign-up"
                />
              </div>

            </div>

            {/* Video Placeholder - Right Side (2/3) */}
            <div className="lg:col-span-2">
              <div className="bg-gradient-to-br from-primary/10 to-accent/10 rounded-3xl aspect-video flex items-center justify-center shadow-2xl">
                <div className="text-center">
                  <div className="w-24 h-24 mx-auto mb-6 bg-primary/20 rounded-full flex items-center justify-center">
                    <svg className="w-10 h-10 text-primary" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-foreground mb-2">Watch FPL AI in Action</h3>
                  <p className="text-muted-foreground">See how our AI assistant helps you dominate Fantasy Premier League</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-muted/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Section Header */}
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Powerful FPL analysis tools
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Our AI assistant provides data-driven insights using advanced player search, transfer optimization, and fixture analysis tools.
            </p>
          </div>

          {/* Feature Blocks */}
          <div className="space-y-20">
            {/* Feature 1: Advanced Player Search & Analysis */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div>
                <div className="bg-primary/10 rounded-full p-3 w-12 h-12 mb-6 flex items-center justify-center">
                  <BarChart3 className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-2xl font-bold text-foreground mb-4">Advanced Player Search & Analysis</h3>
                <div className="flex items-start mb-6">
                  <Quote className="h-5 w-5 text-primary mr-3 mt-1 flex-shrink-0" />
                  <p className="text-lg text-muted-foreground italic">
                    &quot;Show me midfielders under £8m with high xG and good fixture difficulty&quot;
                  </p>
                </div>
                <ul className="space-y-3">
                  <li className="flex items-center">
                    <ChevronRight className="h-4 w-4 text-primary mr-2" />
                    <span className="text-foreground">Expected vs actual performance analysis</span>
                  </li>
                  <li className="flex items-center">
                    <ChevronRight className="h-4 w-4 text-primary mr-2" />
                    <span className="text-foreground">Points per million and efficiency metrics</span>
                  </li>
                  <li className="flex items-center">
                    <ChevronRight className="h-4 w-4 text-primary mr-2" />
                    <span className="text-foreground">Position rankings and ownership categories</span>
                  </li>
                </ul>
              </div>
              <div className="bg-gradient-to-br from-primary/10 to-accent/10 rounded-3xl h-80 flex items-center justify-center">
                <div className="text-muted-foreground text-center">
                  <BarChart3 className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <p>Player Search & Analysis</p>
                </div>
              </div>
            </div>

            {/* Feature 2: Smart Transfer & Captain Suggestions */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div className="order-2 lg:order-1">
                <div className="bg-gradient-to-br from-accent/10 to-primary/10 rounded-3xl h-80 flex items-center justify-center">
                  <div className="text-muted-foreground text-center">
                    <Users className="h-16 w-16 mx-auto mb-4 opacity-50" />
                    <p>Transfer & Captain AI</p>
                  </div>
                </div>
              </div>
              <div className="order-1 lg:order-2">
                <div className="bg-accent/10 rounded-full p-3 w-12 h-12 mb-6 flex items-center justify-center">
                  <Users className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-2xl font-bold text-foreground mb-4">Smart Transfer & Captain Suggestions</h3>
                <div className="flex items-start mb-6">
                  <Quote className="h-5 w-5 text-primary mr-3 mt-1 flex-shrink-0" />
                  <p className="text-lg text-muted-foreground italic">
                    &quot;Who should I captain this week?&quot; or &quot;Find me replacements for Salah&quot;
                  </p>
                </div>
                <ul className="space-y-3">
                  <li className="flex items-center">
                    <ChevronRight className="h-4 w-4 text-primary mr-2" />
                    <span className="text-foreground">Player replacement finder with key attributes</span>
                  </li>
                  <li className="flex items-center">
                    <ChevronRight className="h-4 w-4 text-primary mr-2" />
                    <span className="text-foreground">Captain scoring with fixture difficulty weighting</span>
                  </li>
                  <li className="flex items-center">
                    <ChevronRight className="h-4 w-4 text-primary mr-2" />
                    <span className="text-foreground">Differential player identification</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Feature 3: Fixture & Form Analysis */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div>
                <div className="bg-primary/10 rounded-full p-3 w-12 h-12 mb-6 flex items-center justify-center">
                  <Target className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-2xl font-bold text-foreground mb-4">Fixture & Form Analysis</h3>
                <div className="flex items-start mb-6">
                  <Quote className="h-5 w-5 text-primary mr-3 mt-1 flex-shrink-0" />
                  <p className="text-lg text-muted-foreground italic">
                    &quot;Which teams have the easiest fixtures?&quot; or &quot;Show me Palmer&apos;s recent form&quot;
                  </p>
                </div>
                <ul className="space-y-3">
                  <li className="flex items-center">
                    <ChevronRight className="h-4 w-4 text-primary mr-2" />
                    <span className="text-foreground">Team fixture difficulty (3, 5, 10 gameweek analysis)</span>
                  </li>
                  <li className="flex items-center">
                    <ChevronRight className="h-4 w-4 text-primary mr-2" />
                    <span className="text-foreground">Player form analysis with historical comparisons</span>
                  </li>
                  <li className="flex items-center">
                    <ChevronRight className="h-4 w-4 text-primary mr-2" />
                    <span className="text-foreground">Individual player fixture schedules</span>
                  </li>
                </ul>
              </div>
              <div className="bg-gradient-to-br from-primary/10 to-accent/10 rounded-3xl h-80 flex items-center justify-center">
                <div className="text-muted-foreground text-center">
                  <Target className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <p>Fixture & Form Analysis</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>


      {/* CTA Section */}
      <section className="py-20 bg-primary">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-primary-foreground mb-4">
            Ready to transform your FPL game?
          </h2>
          <p className="text-lg text-primary-foreground/90 mb-8 max-w-2xl mx-auto">
            Join thousands of managers who are already using AI to climb the leaderboards and dominate their mini-leagues.
          </p>
          <Button className="bg-background text-foreground px-8 py-4 rounded-lg text-lg font-semibold hover:bg-background/90 transition-colors">
            Start Your Free Trial
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-card border-t border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <div className="text-2xl font-bold text-primary mb-2">FPL With Robots</div>
              <p className="text-muted-foreground">
                AI-powered Fantasy Premier League assistant helping you make smarter decisions.
              </p>
            </div>
            <div className="flex space-x-8">
              <a href="#" className="text-muted-foreground hover:text-primary transition-colors">
                Release Notes
              </a>
              <a href="#" className="text-muted-foreground hover:text-primary transition-colors">
                Author and How it started
              </a>
            </div>
          </div>
          <div className="border-t border-border mt-8 pt-8 text-center">
            <p className="text-muted-foreground">
              © 2024 FPL With Robots. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}