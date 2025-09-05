import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Link from "next/link";
import { Calendar, Star, ArrowLeft } from "lucide-react";
import releases from "@/data/releases.json";

export default function ReleasesPage() {
  const sortedReleases = Object.entries(releases.releases)
    .sort(([a], [b]) => parseInt(b) - parseInt(a))
    .map(([version, release]) => ({ version: parseInt(version), ...release }));

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-12 max-w-4xl">
        {/* Back to Home Link */}
        <div className="mb-8">
          <Link 
            href="/" 
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-white/50 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to FPL Agent
          </Link>
        </div>
        
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 mb-4">
            <Star className="w-8 h-8 text-emerald-600" />
            <h1 className="text-4xl font-bold text-slate-900">Releases</h1>
          </div>
          <p className="text-lg text-slate-600 leading-relaxed max-w-2xl mx-auto">
            Stay up to date with the latest features, improvements, and bug
            fixes in your Fantasy Premier League AI Assistant. Read more about
            FPL With Robots <a href="https://geirfreysson.com/index.html#category=FPL" className="underline hover:no-underline">here</a>. Give{" "}
            <a 
              href="https://docs.google.com/forms/d/e/1FAIpQLSf9VXR3PickYikDJDWmwyNqb7WlhewPZykDLGutBYzUWGSLvA/viewform?usp=header"
              className="underline hover:no-underline"
            >
              feedback here
            </a>
            .
          </p>
        </div>

        {/* Releases List */}
        <div className="space-y-8">
          {sortedReleases.map((release, index) => (
            <div
              key={release.version}
              className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden hover:shadow-xl transition-shadow duration-300"
            >
              <div className="bg-gradient-to-r from-emerald-500 to-emerald-600 px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="bg-white/20 rounded-lg px-3 py-1">
                      <span className="text-white font-bold text-lg">
                        v{release.version}
                      </span>
                    </div>
                    <h2 className="text-xl font-semibold text-white">
                      {release.title}
                    </h2>
                  </div>
                  {index === 0 && (
                    <div className="bg-amber-400 text-amber-900 px-3 py-1 rounded-full text-sm font-medium">
                      Latest
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-2 mt-2">
                  <Calendar className="w-4 h-4 text-emerald-100" />
                  <span className="text-emerald-100 text-sm">
                    {new Date(release.date).toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })}
                  </span>
                </div>
              </div>

              <div className="px-6 py-6">
                <div className="prose prose-slate max-w-none">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      h2: ({ children }) => (
                        <h2 className="text-xl font-semibold text-slate-800 mt-6 mb-3 first:mt-0">
                          {children}
                        </h2>
                      ),
                      h3: ({ children }) => (
                        <h3 className="text-lg font-medium text-slate-700 mt-4 mb-2">
                          {children}
                        </h3>
                      ),
                      ul: ({ children }) => (
                        <ul className="space-y-1 text-slate-600 ml-4">
                          {children}
                        </ul>
                      ),
                      li: ({ children }) => (
                        <li className="flex items-start gap-2">
                          <span className="text-emerald-500 mt-1.5">•</span>
                          <span>{children}</span>
                        </li>
                      ),
                      p: ({ children }) => (
                        <p className="text-slate-600 leading-relaxed mb-3">
                          {children}
                        </p>
                      ),
                    }}
                  >
                    {release.content}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="text-center mt-12 pt-8 border-t border-slate-200">
          <p className="text-slate-500">
            Having issues or suggestions? Let us know through the chat
            interface!
          </p>
        </div>
      </div>
    </div>
  );
}
