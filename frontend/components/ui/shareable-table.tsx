"use client";

import { useState, useRef, ReactNode } from 'react';
import { Download, Copy, Twitter } from 'lucide-react';
import { cn } from '@/lib/utils';
import { generateTableImage, shareToTwitter, downloadImage, copyImageToClipboard } from '@/lib/table-share';

interface ShareableTableProps {
  children: ReactNode;
  title?: string;
  description?: string;
  className?: string;
}

export function ShareableTable({ children, title, description, className }: ShareableTableProps) {
  const [isHovering, setIsHovering] = useState(false);
  const [isSharing, setIsSharing] = useState(false);
  const [shareComplete, setShareComplete] = useState(false);
  const tableRef = useRef<HTMLDivElement>(null);

  const handleShare = async (type: 'twitter' | 'download' | 'copy') => {
    if (!tableRef.current || isSharing) return;

    setIsSharing(true);
    try {
      const tableElement = tableRef.current.querySelector('table');
      if (!tableElement) return;

      const imageBlob = await generateTableImage({
        element: tableElement,
        title,
        description
      });

      switch (type) {
        case 'twitter':
          await shareToTwitter(imageBlob, title || "Check out this FPL analysis! 🏆");
          break;
        case 'download':
          await downloadImage(imageBlob, 'fpl-table.png');
          break;
        case 'copy':
          const success = await copyImageToClipboard(imageBlob);
          if (!success) {
            // Fallback to download if clipboard fails
            await downloadImage(imageBlob, 'fpl-table.png');
          }
          break;
      }

      setShareComplete(true);
      setTimeout(() => setShareComplete(false), 2000);
    } catch (error) {
      console.error('Failed to share table:', error);
    } finally {
      setIsSharing(false);
    }
  };

  return (
    <div
      ref={tableRef}
      className={cn("relative group", className)}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      {children}
      
      {/* Always visible share indicator for debugging */}
      <div className="absolute top-2 right-2 z-10 bg-red-500 text-white px-2 py-1 rounded text-xs">
        DEBUG
      </div>
      
      {/* Share button overlay */}
      <div
        className={cn(
          "absolute top-2 right-10 z-10 transition-all duration-200",
          isHovering || shareComplete || isSharing ? "opacity-100 scale-100" : "opacity-0 scale-95 pointer-events-none"
        )}
      >
        <div className="flex items-center gap-1 bg-background/95 backdrop-blur-sm border rounded-md shadow-md p-1">
          <button
            onClick={() => handleShare('twitter')}
            disabled={isSharing}
            className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-blue-600 hover:bg-blue-50 rounded transition-colors disabled:opacity-50"
            title="Share to Twitter"
          >
            <Twitter className="w-3 h-3" />
            <span className="hidden sm:inline">Twitter</span>
          </button>
          
          <button
            onClick={() => handleShare('download')}
            disabled={isSharing}
            className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-50 rounded transition-colors disabled:opacity-50"
            title="Download image"
          >
            <Download className="w-3 h-3" />
            <span className="hidden sm:inline">Save</span>
          </button>
          
          <button
            onClick={() => handleShare('copy')}
            disabled={isSharing}
            className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-50 rounded transition-colors disabled:opacity-50"
            title="Copy image"
          >
            <Copy className="w-3 h-3" />
            <span className="hidden sm:inline">Copy</span>
          </button>
        </div>
      </div>

      {/* Share status indicator */}
      {shareComplete && (
        <div className="absolute top-2 right-2 bg-green-100 border border-green-200 text-green-800 px-2 py-1 rounded text-xs font-medium">
          ✓ Shared!
        </div>
      )}
      
      {/* Loading indicator */}
      {isSharing && (
        <div className="absolute top-2 right-2 bg-blue-100 border border-blue-200 text-blue-800 px-2 py-1 rounded text-xs font-medium">
          Generating...
        </div>
      )}
    </div>
  );
}