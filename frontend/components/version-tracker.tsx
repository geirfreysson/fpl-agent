"use client";

import { useEffect } from 'react';
import { toast } from 'sonner';
import releases from '@/data/releases-list';

export const VersionTracker = () => {
  useEffect(() => {
    const checkForNewRelease = () => {
      const currentVersion = releases.currentVersion;
      const lastVersionSeen = localStorage.getItem('lastVersionSeen');
      
      if (!lastVersionSeen) {
        // First time user, show toast and set current version as seen
        const currentRelease = releases.releases[currentVersion.toString()];
        const releaseTitle = currentRelease?.title || `Release ${currentVersion}`;
        
        toast.success(`New release: ${releaseTitle} 🎉🎉🎉`, {
          duration: 10000,
          action: {
            label: 'View',
            onClick: () => window.open('/releases', '_blank')
          }
        });
        
        localStorage.setItem('lastVersionSeen', currentVersion.toString());
        return;
      }
      
      const lastSeenNumber = parseInt(lastVersionSeen);
      
      if (lastSeenNumber < currentVersion) {
        // New release available
        const currentRelease = releases.releases[currentVersion.toString()];
        const releaseTitle = currentRelease?.title || `Release ${currentVersion}`;
        
        toast.success(`New release: ${releaseTitle} 🎉🎉🎉`, {
          duration: 10000,
          action: {
            label: 'View',
            onClick: () => window.open('/releases', '_blank')
          }
        });
        
        // Update the last seen version
        localStorage.setItem('lastVersionSeen', currentVersion.toString());
      }
    };
    
    // Check after a short delay to ensure UI is ready
    const timeoutId = setTimeout(checkForNewRelease, 1000);
    
    return () => clearTimeout(timeoutId);
  }, []);
  
  return null;
};