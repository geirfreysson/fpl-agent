"use client";

import { useEffect, useCallback, useRef } from 'react';
import { useThread } from '@assistant-ui/react';
import { generateTableImage, shareToTwitter, downloadImage, copyImageToClipboard } from '@/lib/table-share';

// Hook that adds share buttons after streaming completes
export function useTableShare() {
  const thread = useThread();
  const wasRunning = useRef(false);
  const processedMessages = useRef(new Set<string>());
  const cleanupFunctions = useRef(new Set<() => void>());

  const shareTable = useCallback(async (tableElement: HTMLTableElement, type: 'twitter' | 'download' | 'copy') => {
    try {
      if (!tableElement?.isConnected) {
        console.warn('Table not connected to DOM');
        return false;
      }

      const imageBlob = await generateTableImage({
        element: tableElement,
        title: getTableTitle(tableElement),
        description: getTableDescription(tableElement)
      });

      switch (type) {
        case 'twitter':
          await shareToTwitter(imageBlob, getTableTitle(tableElement) || "AI FPL analysis!! 🤖");
          break;
        case 'download':
          await downloadImage(imageBlob, 'fpl-table.png');
          break;
        case 'copy':
          const success = await copyImageToClipboard(imageBlob);
          if (!success) {
            await downloadImage(imageBlob, 'fpl-table.png');
          }
          break;
      }
      return true;
    } catch (error) {
      console.error(`Failed to ${type} table:`, error);
      return false;
    }
  }, []);

  const addShareButtonsToTable = useCallback((table: HTMLTableElement) => {
    // Check if buttons already exist after this table
    const nextSibling = table.nextElementSibling;
    if (nextSibling && nextSibling.classList.contains('table-share-buttons')) {
      return;
    }

    try {
      // Create share buttons container that gets inserted AFTER the table
      const shareContainer = document.createElement('div');
      shareContainer.className = 'table-share-buttons flex gap-2 mt-2 mb-4 text-sm';
      shareContainer.style.cssText = 'opacity: 0.8; transition: opacity 0.2s;';
      shareContainer.setAttribute('data-table-id', `table-${Date.now()}-${Math.random()}`);
      
      // Create buttons
      const buttons = [
        { label: 'Share', emoji: '𝕏', action: () => shareTable(table, 'twitter') },
        { label: 'Download', emoji: '💾', action: () => shareTable(table, 'download') },
        { label: 'Copy', emoji: '📋', action: () => shareTable(table, 'copy') }
      ];

      buttons.forEach(({ label, emoji, action }) => {
        const button = document.createElement('button');
        button.className = 'inline-flex items-center gap-1 px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded text-gray-700 transition-colors';
        button.innerHTML = `<span>${emoji}</span><span class="hidden sm:inline">${label}</span>`;
        button.onclick = (e) => {
          e.preventDefault();
          e.stopPropagation();
          action();
        };
        shareContainer.appendChild(button);
      });

      // Insert after the table using insertAdjacentElement (safer than parent manipulation)
      table.insertAdjacentElement('afterend', shareContainer);

      // Store cleanup function
      const cleanup = () => {
        try {
          if (shareContainer.parentNode) {
            shareContainer.parentNode.removeChild(shareContainer);
          }
        } catch (error) {
          console.warn('Failed to cleanup share container:', error);
        }
      };
      cleanupFunctions.current.add(cleanup);

    } catch (error) {
      console.error('Failed to add share buttons:', error);
    }
  }, [shareTable]);

  const processNewTables = useCallback(() => {
    try {
      // Find all tables that haven't been processed yet
      const unprocessedTables = document.querySelectorAll('table:not([data-share-processed])');
      console.log(`Found ${unprocessedTables.length} unprocessed tables`);
      
      if (unprocessedTables.length === 0) return;
      
      // Process each table
      unprocessedTables.forEach((table) => {
        const tableElement = table as HTMLTableElement;
        if (tableElement.isConnected) {
          console.log('Adding share buttons to table');
          tableElement.setAttribute('data-share-processed', 'true');
          addShareButtonsToTable(tableElement);
        }
      });
      
    } catch (error) {
      console.error('Error processing new tables:', error);
    }
  }, [addShareButtonsToTable]);

  // Stream completion detection
  useEffect(() => {
    // When streaming stops (isRunning goes from true to false), process new tables
    if (wasRunning.current && !thread.isRunning) {
      console.log('Stream completed, processing tables...');
      // Small delay to ensure DOM is fully updated
      setTimeout(() => {
        processNewTables();
      }, 100);
    }
    
    // Update the running state
    wasRunning.current = thread.isRunning;
  }, [thread.isRunning, processNewTables]);

  // Initial check for existing tables when component mounts
  useEffect(() => {
    // Check for existing tables when the hook first mounts
    const initialCheck = setTimeout(() => {
      processNewTables();
    }, 500);

    return () => {
      clearTimeout(initialCheck);
      // Cleanup all share button containers
      cleanupFunctions.current.forEach(cleanup => cleanup());
      cleanupFunctions.current.clear();
      processedMessages.current.clear();
    };
  }, [processNewTables]);

  return { shareTable };
}

function getTableTitle(table: HTMLTableElement): string | undefined {
  // Look for a title in preceding headings
  let element = table.previousElementSibling;
  while (element) {
    if (element.tagName.match(/^H[1-6]$/)) {
      return element.textContent?.trim();
    }
    element = element.previousElementSibling;
  }
  
  // Look for title in the first row if it's a header
  const firstRow = table.querySelector('tr');
  if (firstRow && firstRow.cells.length === 1) {
    return firstRow.textContent?.trim();
  }
  
  return undefined;
}

function getTableDescription(table: HTMLTableElement): string | undefined {
  // Look for description text before the table
  let element = table.previousElementSibling;
  while (element && !element.tagName.match(/^H[1-6]$/)) {
    if (element.tagName === 'P') {
      return element.textContent?.trim();
    }
    element = element.previousElementSibling;
  }
  return undefined;
}