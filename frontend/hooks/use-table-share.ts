"use client";

import { useCallback } from 'react';
import { generateTableImage, shareToTwitter, downloadImage, copyImageToClipboard } from '@/lib/table-share';

// Simplified hook that provides share functions without automatic DOM manipulation
export function useTableShare() {
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