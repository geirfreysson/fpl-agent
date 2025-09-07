"use client";

import { useEffect, useCallback, useRef } from 'react';
import { generateTableImage, shareToTwitter, downloadImage, copyImageToClipboard } from '@/lib/table-share';

// Hook that safely adds share functionality without DOM manipulation conflicts
export function useTableShare() {
  const processedTables = useRef(new Set<HTMLTableElement>());
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

  const addShareButtons = useCallback((table: HTMLTableElement) => {
    if (processedTables.current.has(table)) {
      return;
    }

    try {
      processedTables.current.add(table);
      
      // Create share buttons container that gets inserted AFTER the table
      const shareContainer = document.createElement('div');
      shareContainer.className = 'table-share-buttons flex gap-2 mt-2 mb-4 text-sm';
      shareContainer.style.cssText = 'opacity: 0.8; transition: opacity 0.2s;';
      
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

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    
    const checkForTables = () => {
      try {
        const tables = document.querySelectorAll('table:not([data-share-processed])');
        
        tables.forEach((table) => {
          const tableElement = table as HTMLTableElement;
          if (tableElement.isConnected && !processedTables.current.has(tableElement)) {
            tableElement.setAttribute('data-share-processed', 'true');
            addShareButtons(tableElement);
          }
        });
      } catch (error) {
        console.error('Error checking for tables:', error);
      }
      
      // Check again after a delay for streaming content
      timeoutId = setTimeout(checkForTables, 1000);
    };

    // Initial check
    checkForTables();

    return () => {
      clearTimeout(timeoutId);
      // Cleanup all share button containers
      cleanupFunctions.current.forEach(cleanup => cleanup());
      cleanupFunctions.current.clear();
      processedTables.current.clear();
    };
  }, [addShareButtons]);

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