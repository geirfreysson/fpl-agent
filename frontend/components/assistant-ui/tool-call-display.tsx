import { CheckIcon, ChevronDownIcon, ChevronUpIcon } from "lucide-react";
import { useState } from "react";
import { Button } from "../ui/button";
import { getToolDisplayName } from "../../lib/tool-display-names";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";

interface ToolCallDisplayProps {
  toolName: string;
  arguments: Record<string, unknown>;
  result: string;
  count?: number;
  allCalls?: Array<{
    arguments: Record<string, unknown>;
    result: string;
  }>;
}

export const ToolCallDisplay = ({ toolName, arguments: args, result, count = 1, allCalls }: ToolCallDisplayProps) => {
  const [isCollapsed, setIsCollapsed] = useState(true);
  
  // Special handling for final_answer tool - don't show as a tool card
  if (toolName === 'final_answer') {
    return null; // Don't render final_answer tool cards
  }
  
  const displayCalls = allCalls || [{ arguments: args, result }];
  const isMultiple = count > 1;
  
  // Regular tool call display
  return (
    <div className="mb-4 flex w-full flex-col gap-3 rounded-lg border py-3">
      <div className="flex items-center gap-2 px-4">
        <CheckIcon className="size-4" />
        <p className="" style={{ fontSize: '16px' }}>
          <b>{getToolDisplayName(toolName)}</b>
          {isMultiple && (
            <span className="ml-2 inline-flex h-5 w-5 items-center justify-center rounded-full bg-blue-100 text-xs font-medium text-blue-800">
              {count}
            </span>
          )}
        </p>
        <div className="flex-grow" />
        <Button onClick={() => setIsCollapsed(!isCollapsed)} variant="ghost" size="sm">
          {isCollapsed ? <ChevronUpIcon className="size-4" /> : <ChevronDownIcon className="size-4" />}
        </Button>
      </div>
      {!isCollapsed && (
        <div className="flex flex-col gap-2 border-t pt-2">
          {isMultiple ? (
            // Show all calls when multiple
            displayCalls.map((call, index) => (
              <div key={index} className={index > 0 ? "border-t border-dashed pt-2" : ""}>
                <div className="px-4">
                  <p className="font-semibold mb-1" style={{ fontSize: '16px' }}>Call {index + 1} - Arguments:</p>
                  <pre className="whitespace-pre-wrap bg-gray-50 p-2 rounded" style={{ fontSize: '16px' }}>
                    {JSON.stringify(call.arguments, null, 2)}
                  </pre>
                </div>
                <div className="px-4 pt-2">
                  <p className="font-semibold mb-1" style={{ fontSize: '16px' }}>Call {index + 1} - Result:</p>
                  <div className="prose max-w-none" style={{ fontSize: '16px' }}>
                    <ReactMarkdown 
                      remarkPlugins={[remarkGfm]}
                      components={{
                        table: ({ className, ...props }) => (
                          <table className={cn("my-5 w-full border-separate border-spacing-0 overflow-y-auto", className)} {...props} />
                        ),
                        th: ({ className, ...props }) => (
                          <th className={cn("bg-muted px-4 py-2 text-left font-bold first:rounded-tl-lg last:rounded-tr-lg [&[align=center]]:text-center [&[align=right]]:text-right", className)} {...props} />
                        ),
                        td: ({ className, ...props }) => (
                          <td className={cn("border-b border-l px-4 py-2 text-left last:border-r [&[align=center]]:text-center [&[align=right]]:text-right", className)} {...props} />
                        ),
                        tr: ({ className, ...props }) => (
                          <tr className={cn("m-0 border-b p-0 first:border-t [&:last-child>td:first-child]:rounded-bl-lg [&:last-child>td:last-child]:rounded-br-lg", className)} {...props} />
                        ),
                      }}
                    >
                      {call.result}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            ))
          ) : (
            // Single call display
            <>
              <div className="px-4">
                <p className="font-semibold mb-1" style={{ fontSize: '16px' }}>Arguments:</p>
                <pre className="whitespace-pre-wrap bg-gray-50 p-2 rounded" style={{ fontSize: '16px' }}>
                  {JSON.stringify(args, null, 2)}
                </pre>
              </div>
              <div className="border-t border-dashed px-4 pt-2">
                <p className="font-semibold mb-1" style={{ fontSize: '16px' }}>Result:</p>
                <div className="prose max-w-none" style={{ fontSize: '16px' }}>
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      table: ({ className, ...props }) => (
                        <table className={cn("my-5 w-full border-separate border-spacing-0 overflow-y-auto", className)} {...props} />
                      ),
                      th: ({ className, ...props }) => (
                        <th className={cn("bg-muted px-4 py-2 text-left font-bold first:rounded-tl-lg last:rounded-tr-lg [&[align=center]]:text-center [&[align=right]]:text-right", className)} {...props} />
                      ),
                      td: ({ className, ...props }) => (
                        <td className={cn("border-b border-l px-4 py-2 text-left last:border-r [&[align=center]]:text-center [&[align=right]]:text-right", className)} {...props} />
                      ),
                      tr: ({ className, ...props }) => (
                        <tr className={cn("m-0 border-b p-0 first:border-t [&:last-child>td:first-child]:rounded-bl-lg [&:last-child>td:last-child]:rounded-br-lg", className)} {...props} />
                      ),
                    }}
                  >
                    {result}
                  </ReactMarkdown>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};