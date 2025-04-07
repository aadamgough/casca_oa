"use client"

import { Button } from "@/components/ui/button";

interface ResultsProps {
    isOpen: boolean;
    onClose: () => void;
    results: {
        summary: string;
        timestamp: string;
    }; 
}

export function AnalysisModal({ isOpen, onClose, results }: ResultsProps) {
    if (!isOpen || !results) return null;

    // debug logs
    console.log('Results:', results);
    console.log('Summary type:', typeof results.summary);
    console.log('Summary value:', results.summary);

    // Extract score from the summary text
    const extractScore = (text: string): number => {
        if (typeof text !== 'string') {
            console.log('Warning: text is not a string:', text);
            return 0;
        }
        const scoreMatch = text.match(/Score:\s*(\d+)/);
        return scoreMatch ? parseInt(scoreMatch[1]) : 0;
    };
    
    // Extract decision from the summary text
    const extractDecision = (text: string): string => {
        if (typeof text !== 'string') {
            console.log('Warning: text is not a string in extractDecision:', text);
            return "NO_DECISION";
        }
        const decisionMatch = text.match(/Decision:\s*([A-Z_]+)/);
        return decisionMatch ? decisionMatch[1] : "NO_DECISION";
    };

    const score = extractScore(results.summary);
    const decision = extractDecision(results.summary);

    const getStatusColor = (score: number) => {
        if (score >= 70) return "text-green-500";
        if (score >= 50) return "text-yellow-500";
        return "text-red-500";
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-background p-8 rounded-lg shadow-lg max-w-2xl w-full mx-4">
                <h2 className="text-2xl font-bold mb-6">Analysis Results</h2>
                
                <div className="grid gap-6">
                    {/* Overall Score */}
                    <div className="text-center">
                        <div className={`text-4xl font-bold ${getStatusColor(score)}`}>
                            {score}%
                        </div>
                        <div className="text-lg font-medium mt-2">{decision}</div>
                    </div>

                    {/* Analysis Summary */}
                    <div className="p-4 rounded-lg border">
                        <h3 className="font-semibold">Detailed Analysis</h3>
                        <div className="text-sm text-muted-foreground mt-1 whitespace-pre-line">
                            {results.summary}
                        </div>
                    </div>

                    <button 
                        onClick={onClose}
                        className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    );
}