"use client";

import { useState, useEffect, useCallback } from "react";

const MESSAGE_COUNTER_KEY = "fpl-agent-message-counter";

export function useMessageCounter() {
  const [messageCount, setMessageCount] = useState<number>(0);
  const [showModal, setShowModal] = useState<boolean>(false);

  // Load counter from localStorage on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedCount = localStorage.getItem(MESSAGE_COUNTER_KEY);
      if (storedCount) {
        setMessageCount(parseInt(storedCount, 10));
      }
    }
  }, []);

  // Function to increment the counter
  const incrementCounter = useCallback(() => {
    setMessageCount((prevCount) => {
      const newCount = prevCount + 1;
      
      // Save to localStorage
      if (typeof window !== "undefined") {
        localStorage.setItem(MESSAGE_COUNTER_KEY, newCount.toString());
      }
      
      // Debug logging
      console.log(`Message count: ${newCount}`);
      
      // Show modal every 2 messages
      if (newCount % 10 === 0) {
        console.log(`Should show modal at message ${newCount}`);
        setShowModal(true);
      }
      
      return newCount;
    });
  }, []);

  // Function to close the modal
  const closeModal = useCallback(() => {
    setShowModal(false);
  }, []);

  // Function to reset the counter (if needed)
  const resetCounter = useCallback(() => {
    setMessageCount(0);
    if (typeof window !== "undefined") {
      localStorage.removeItem(MESSAGE_COUNTER_KEY);
    }
  }, []);

  return {
    messageCount,
    showModal,
    incrementCounter,
    closeModal,
    resetCounter,
  };
}