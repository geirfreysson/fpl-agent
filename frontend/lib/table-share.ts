import html2canvas from 'html2canvas';

interface ShareOptions {
  element: HTMLElement;
  title?: string;
  description?: string;
}

// Safe DOM element removal helper
function safeRemoveChild(parent: Node, child: Node): boolean {
  try {
    if (child.parentNode === parent) {
      parent.removeChild(child);
      return true;
    } else if (child.parentNode) {
      child.parentNode.removeChild(child);
      return true;
    }
  } catch (error) {
    console.warn('Failed to remove DOM element:', error);
  }
  return false;
}

export async function generateTableImage({ element, title, description }: ShareOptions): Promise<Blob> {
  return new Promise((resolve, reject) => {
    // Create an isolated iframe to avoid CSS conflicts
    const iframe = document.createElement('iframe');
    iframe.style.cssText = `
      position: absolute;
      top: -9999px;
      left: -9999px;
      width: 800px;
      height: 600px;
      border: none;
    `;
    
    document.body.appendChild(iframe);
    
    iframe.onload = async () => {
      try {
        const iframeDoc = iframe.contentDocument!;
        
        // Create a clean HTML document
        iframeDoc.open();
        iframeDoc.write(`
          <!DOCTYPE html>
          <html>
          <head>
            <style>
              * { margin: 0; padding: 0; box-sizing: border-box; }
              body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: white;
                padding: 24px;
                color: #111827;
              }
              .container {
                max-width: 800px;
                margin: 0 auto;
              }
              .header {
                text-align: center;
                margin-bottom: 16px;
              }
              .title {
                font-size: 20px;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 8px;
              }
              .description {
                font-size: 14px;
                color: #666666;
                margin-bottom: 8px;
              }
              .table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                overflow: hidden;
                margin: 0 auto;
              }
              .table th {
                background: #f3f4f6;
                padding: 12px 16px;
                text-align: left;
                font-weight: 600;
                color: #374151;
                border-right: 1px solid #e5e7eb;
              }
              .table th:last-child {
                border-right: none;
              }
              .table td {
                padding: 12px 16px;
                text-align: left;
                border-right: 1px solid #e5e7eb;
                border-top: 1px solid #e5e7eb;
              }
              .table td:last-child {
                border-right: none;
              }
              .table tr:nth-child(even) td {
                background: #f9fafb;
              }
              .footer {
                margin-top: 16px;
                text-align: center;
                font-size: 12px;
                color: #666666;
              }
            </style>
          </head>
          <body>
            <div class="container">
              <div class="header">
                ${title ? `<div class="title">${title}</div>` : ''}
                ${description ? `<div class="description">${description}</div>` : ''}
              </div>
              <table class="table">
                ${getTableHTML(element)}
              </table>
              <div class="footer">
                fpl.withrobots.ai
              </div>
            </div>
          </body>
          </html>
        `);
        iframeDoc.close();
        
        // Wait a bit for rendering
        setTimeout(async () => {
          try {
            const canvas = await html2canvas(iframeDoc.body, {
              backgroundColor: '#ffffff',
              scale: 2,
              logging: false,
              useCORS: true,
              allowTaint: true,
            });
            
            canvas.toBlob((blob) => {
              safeRemoveChild(document.body, iframe);
              if (blob) {
                resolve(blob);
              } else {
                reject(new Error('Failed to generate blob'));
              }
            }, 'image/png', 0.9);
          } catch (error) {
            safeRemoveChild(document.body, iframe);
            reject(error);
          }
        }, 500);
        
      } catch (error) {
        safeRemoveChild(document.body, iframe);
        reject(error);
      }
    };
    
    iframe.onerror = () => {
      safeRemoveChild(document.body, iframe);
      reject(new Error('Failed to load iframe'));
    };
    
    // Trigger load
    iframe.src = 'about:blank';
  });
}

function getTableHTML(element: HTMLElement): string {
  const rows = element.querySelectorAll('tr');
  return Array.from(rows).map(row => {
    const cells = row.querySelectorAll('td, th');
    const cellsHTML = Array.from(cells).map(cell => {
      const isHeader = cell.tagName === 'TH';
      const align = cell.getAttribute('align') || 'left';
      const content = cell.textContent || '';
      return `<${isHeader ? 'th' : 'td'} style="text-align: ${align}">${content}</${isHeader ? 'th' : 'td'}>`;
    }).join('');
    return `<tr>${cellsHTML}</tr>`;
  }).join('');
}

export async function shareToTwitter(imageBlob: Blob, text: string = "Check out this FPL analysis! 🏆") {
  // For now, we'll download the image and copy text to clipboard
  // Twitter's API requires backend integration for direct image posting
  
  await downloadImage(imageBlob, 'fpl-analysis.png');
  await copyToClipboard(text + "\n\n#FPL #FantasyPremierLeague");
  
  // Open Twitter compose window
  const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text + "\n\n#FPL #FantasyPremierLeague")}`;
  window.open(twitterUrl, '_blank');
}

export async function downloadImage(blob: Blob, filename: string = 'table-share.png') {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  
  try {
    document.body.appendChild(link);
    link.click();
    safeRemoveChild(document.body, link);
  } catch (error) {
    console.warn('Failed to handle download link:', error);
    // Try to remove the link even if there was an error
    safeRemoveChild(document.body, link);
  } finally {
    URL.revokeObjectURL(url);
  }
}

export async function copyImageToClipboard(blob: Blob) {
  if (navigator.clipboard && window.ClipboardItem) {
    try {
      await navigator.clipboard.write([
        new ClipboardItem({
          [blob.type]: blob
        })
      ]);
      return true;
    } catch (err) {
      console.error('Failed to copy image to clipboard:', err);
      return false;
    }
  }
  return false;
}

export async function copyToClipboard(text: string) {
  if (navigator.clipboard) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (err) {
      console.error('Failed to copy text to clipboard:', err);
      return false;
    }
  }
  return false;
}