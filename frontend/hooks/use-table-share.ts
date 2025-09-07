"use client";

import { useEffect } from 'react';
import { generateTableImage, shareToTwitter, downloadImage, copyImageToClipboard } from '@/lib/table-share';

export function useTableShare() {
  useEffect(() => {
    const addShareButtonsToTables = () => {
      // Find all tables that don't already have share buttons
      const tables = document.querySelectorAll('table:not([data-share-enabled])');
      
      tables.forEach((table) => {
        const tableElement = table as HTMLTableElement;
        
        // Mark this table as processed
        tableElement.setAttribute('data-share-enabled', 'true');
        
        // Create wrapper if table isn't already wrapped
        let wrapper = table.closest('.table-share-wrapper');
        if (!wrapper) {
          wrapper = document.createElement('div');
          wrapper.className = 'table-share-wrapper';
          table.parentNode?.insertBefore(wrapper, table);
          wrapper.appendChild(table);
        }
        
        // Create share button container below the table
        const shareContainer = document.createElement('div');
        shareContainer.className = 'share-button-container flex justify-start -mt-3 mb-4 gap-1';
        
        const shareButtons = document.createElement('div');
        shareButtons.className = 'flex items-center gap-1 bg-white p-1';
        
        // Twitter share button
        const twitterBtn = createShareButton('Share', 'text-gray-600 hover:bg-gray-50', '𝕏', async () => {
          try {
            const imageBlob = await generateTableImage({
              element: tableElement,
              title: getTableTitle(tableElement),
              description: getTableDescription(tableElement)
            });
            await shareToTwitter(imageBlob, getTableTitle(tableElement) || "AI FPL analysis!! 🤖");
          } catch (error) {
            console.error('Failed to share to Twitter:', error);
          }
        });
        
        // Download button
        const downloadBtn = createShareButton('Download', 'text-gray-600 hover:bg-gray-50', '💾', async () => {
          try {
            const imageBlob = await generateTableImage({
              element: tableElement,
              title: getTableTitle(tableElement),
              description: getTableDescription(tableElement)
            });
            await downloadImage(imageBlob, 'fpl-table.png');
          } catch (error) {
            console.error('Failed to download:', error);
          }
        });
        
        // Copy button
        const copyBtn = createShareButton('Copy', 'text-gray-600 hover:bg-gray-50', '📋', async () => {
          try {
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
          }
        });
        
        shareButtons.appendChild(twitterBtn);
        shareButtons.appendChild(downloadBtn);
        shareButtons.appendChild(copyBtn);
        shareContainer.appendChild(shareButtons);
        wrapper.appendChild(shareContainer);
      });
    };

    // Initial check for existing tables
    addShareButtonsToTables();

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
        // Delay slightly to ensure the table is fully rendered
        setTimeout(addShareButtonsToTables, 100);
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
  }, []);
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