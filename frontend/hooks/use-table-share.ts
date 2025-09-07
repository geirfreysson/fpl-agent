"use client";

import { useEffect, useCallback, useRef } from 'react';
import { generateTableImage, shareToTwitter, downloadImage, copyImageToClipboard } from '@/lib/table-share';

export function useTableShare() {
  const processedTables = useRef(new WeakSet());
  const pendingUpdates = useRef(false);

  const addShareButtonsToTables = useCallback(() => {
    try {
      // Find all tables that don't already have share buttons
      const tables = document.querySelectorAll('table:not([data-share-enabled])');
      
      tables.forEach((table) => {
        try {
          const tableElement = table as HTMLTableElement;
          
          // Skip if already processed
          if (processedTables.current.has(tableElement)) {
            return;
          }
          
          // Verify the table is still connected to the DOM
          if (!tableElement.isConnected || !tableElement.parentNode) {
            return;
          }
          
          // Mark this table as processed
          tableElement.setAttribute('data-share-enabled', 'true');
          processedTables.current.add(tableElement);
          
          // Create wrapper if table isn't already wrapped
          let wrapper = table.closest('.table-share-wrapper');
          if (!wrapper) {
            // Double-check parent still exists and table is still connected
            const parent = tableElement.parentNode;
            if (!parent || !tableElement.isConnected) {
              return;
            }
            
            wrapper = document.createElement('div');
            wrapper.className = 'table-share-wrapper';
            
            // Safely insert the wrapper
            parent.insertBefore(wrapper, tableElement);
            wrapper.appendChild(tableElement);
          }
          
          // Verify wrapper is still connected before adding share buttons
          if (!wrapper.isConnected) {
            return;
          }
          
          // Create share button container below the table
          const shareContainer = document.createElement('div');
          shareContainer.className = 'share-button-container flex justify-start -mt-3 mb-4 gap-1';
          
          const shareButtons = document.createElement('div');
          shareButtons.className = 'flex items-center gap-1 bg-white p-1';
          
          // Twitter share button
          const twitterBtn = createShareButton('Share', 'text-gray-600 hover:bg-gray-50', '𝕏', async () => {
            try {
              // Verify table still exists before processing
              if (!tableElement.isConnected || !tableElement.parentNode) {
                console.warn('Table no longer connected to DOM, skipping share');
                return;
              }
              
              const imageBlob = await generateTableImage({
                element: tableElement,
                title: getTableTitle(tableElement),
                description: getTableDescription(tableElement)
              });
              await shareToTwitter(imageBlob, getTableTitle(tableElement) || "AI FPL analysis!! 🤖");
            } catch (error) {
              console.error('Failed to share to Twitter:', error);
              // Don't throw, just log and continue
            }
          });
          
          // Download button
          const downloadBtn = createShareButton('Download', 'text-gray-600 hover:bg-gray-50', '💾', async () => {
            try {
              // Verify table still exists before processing
              if (!tableElement.isConnected || !tableElement.parentNode) {
                console.warn('Table no longer connected to DOM, skipping download');
                return;
              }
              
              const imageBlob = await generateTableImage({
                element: tableElement,
                title: getTableTitle(tableElement),
                description: getTableDescription(tableElement)
              });
              await downloadImage(imageBlob, 'fpl-table.png');
            } catch (error) {
              console.error('Failed to download:', error);
              // Don't throw, just log and continue
            }
          });
          
          // Copy button
          const copyBtn = createShareButton('Copy', 'text-gray-600 hover:bg-gray-50', '📋', async () => {
            try {
              // Verify table still exists before processing
              if (!tableElement.isConnected || !tableElement.parentNode) {
                console.warn('Table no longer connected to DOM, skipping copy');
                return;
              }
              
              const imageBlob = await generateTableImage({
                element: tableElement,
                title: getTableTitle(tableElement),
                description: getTableDescription(tableElement)
              });
              const success = await copyImageToClipboard(imageBlob);
              if (!success) {
                await downloadImage(imageBlob, 'fpl-table.png');
              }
            } catch (error) {
              console.error('Failed to copy:', error);
              // Don't throw, just log and continue
            }
          });
          
          try {
            shareButtons.appendChild(twitterBtn);
            shareButtons.appendChild(downloadBtn);
            shareButtons.appendChild(copyBtn);
            shareContainer.appendChild(shareButtons);
            
            // Verify wrapper is still connected before adding
            if (wrapper.isConnected && wrapper.parentNode) {
              wrapper.appendChild(shareContainer);
            } else {
              console.warn('Wrapper no longer connected, skipping share container');
            }
          } catch (error) {
            console.error('Failed to add share buttons to container:', error);
          }
        } catch (error) {
          console.error('Failed to add share buttons to table:', error);
        }
      });
    } catch (error) {
      console.error('Failed to process tables for sharing:', error);
    }
  }, []);

  // Debounced function to handle table updates
  const debouncedAddShareButtons = useCallback(() => {
    if (pendingUpdates.current) return;
    
    pendingUpdates.current = true;
    requestAnimationFrame(() => {
      addShareButtonsToTables();
      pendingUpdates.current = false;
    });
  }, [addShareButtonsToTables]);

  useEffect(() => {
    // Initial check for existing tables
    requestAnimationFrame(() => addShareButtonsToTables());

    // Watch for new tables being added (for streaming content)
    const observer = new MutationObserver((mutations) => {
      let hasNewTables = false;
      
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
              const element = node as Element;
              // Check if the added node contains tables or is a table itself
              if (element.tagName === 'TABLE' || element.querySelector('table')) {
                hasNewTables = true;
              }
            }
          });
        }
      });
      
      if (hasNewTables) {
        debouncedAddShareButtons();
      }
    });

    // Start observing the document for changes
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    return () => {
      observer.disconnect();
    };
  }, [addShareButtonsToTables, debouncedAddShareButtons]);
}

function createShareButton(label: string, className: string, emoji: string, onClick: () => void): HTMLButtonElement {
  const button = document.createElement('button');
  button.className = `flex items-center gap-1 px-2 py-1 text-xs font-medium rounded transition-colors ${className}`;
  button.title = label;
  button.innerHTML = `
    <span>${emoji}</span>
    <span class="hidden sm:inline">${label}</span>
  `;
  button.addEventListener('click', onClick);
  return button;
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