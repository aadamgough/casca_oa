"use client"

import { useState, useEffect } from 'react';


// TODO: change progress bar to actually load per stage
const stages = [ 
  "Processing document...",
  "Extracting transactions...",
  "Analyzing patterns...",
  "Generating recommendations..."
];

interface LoadingProps {
  isLoading: boolean;
}

export function AnalysisLoading({ isLoading }: LoadingProps) {
  const [currentStage, setCurrentStage] = useState(0);

  useEffect(() => {
    // Reset currentStage when isLoading changes to true
    if (isLoading) {
        setCurrentStage(0);
      }
      
    if (!isLoading) return;

    const interval = setInterval(() => {
      setCurrentStage((prev) => (prev < stages.length - 1 ? prev + 1 : prev));
    }, 4000);

    return () => clearInterval(interval);
  }, [isLoading]);

  if (!isLoading) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-background p-8 rounded-lg shadow-lg max-w-md w-full mx-4">
        <div className="flex flex-col items-center gap-4">
          <p className="text-lg font-medium">{stages[currentStage]}</p>
          <div className="w-full bg-muted rounded-full h-2">
            <div 
              className="bg-primary h-2 rounded-full transition-all duration-500"
              style={{ width: `${((currentStage + 1) / stages.length) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
}