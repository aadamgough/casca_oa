"use client"

import { Button } from "@/components/ui/button";
import { AnalysisResults } from "@/types/analysis";
import { useState } from "react";

interface ResultsProps {
    isOpen: boolean;
    onClose: () => void;
    results: AnalysisResults;
}

export function AnalysisModal({ isOpen, onClose, results }: ResultsProps) {
    const [showScoreInfo, setShowScoreInfo] = useState(false);
    if (!isOpen || !results) return null;

    const getDecisionColor = (decision: string) => {
        switch (decision) {
            case 'Loan Approved': return "text-green-500";
            case 'Further information needed': return "text-yellow-500";
            case 'Loan Denied': return "text-red-500";
            default: return "text-gray-500";
        }
    };

    const getSeverityColor = (severity: string) => {
        switch (severity.toLowerCase()) {
            case 'high': return "border-red-500";
            case 'medium': return "border-yellow-500";
            case 'low': return "border-green-500";
            default: return "border-gray-500";
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-background p-8 rounded-lg shadow-lg max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-6">
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                    <Button 
                        onClick={() => setShowScoreInfo(true)}
                        className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded"
                    >
                        What is the loan score?
                    </Button>
                </div>

                {/* Score Info Modal */}
                {showScoreInfo && (
                    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[60]">
                        <div className="bg-white p-6 rounded-lg shadow-lg max-w-md mx-4">
                            <h3 className="text-lg font-semibold mb-2">Understanding the Loan Score</h3>
                            <p className="text-sm text-gray-600 mb-4">
                                The loan score (0-100) evaluates creditworthiness based on cash flow, income stability, 
                                expense management, and overall financial health. Scores above 75 typically indicate 
                                loan approval, while lower scores may require additional review.
                            </p>
                            <Button 
                                onClick={() => setShowScoreInfo(false)}
                                className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded"
                            >
                                Close
                            </Button>
                        </div>
                    </div>
                )}

                {/* Overall Score */}
                <div className="text-center mb-8">
                    <div className="text-5xl font-bold">
                        Loan Score: <span className={getDecisionColor(results.summary.health_status)}>
                            {results.summary.overall_score}
                        </span>
                    </div>
                    <div className="text-xl mt-2">{results.summary.health_status}</div>
                </div>

                {/* Key Findings */}
                <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-2">Key Findings</h3>
                </div>

                {/* Component Scores with Summaries */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    {Object.entries(results.detailed_analysis.components).map(([key, component]) => (
                        <div key={key} className="p-4 border rounded-lg">
                            <div className="flex justify-between items-center mb-2">
                                <h4 className="font-semibold capitalize">{key.replace('_', ' ')}</h4>
                                <span className={getDecisionColor(component.status)}>
                                    {component.score}
                                </span>
                            </div>
                            <p className="text-sm text-muted-foreground">{component.summary}</p>
                            {/* Display component-specific details */}
                            {component.details && (
                                <div className="mt-2 text-sm">
                                    {key === 'cash_flow'}
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                {/* Flags and Recommendations */}
                <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-2">Flags to watch out for</h3>
                    <div className="space-y-2">
                        {results.recommendations.flags.map((flag, index) => (
                            <div key={index} className={`p-3 rounded-lg border ${getSeverityColor(flag.severity)} bg-opacity-10`}>
                                <span className="font-medium">{flag.message}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Metrics */}
                <h3 className="text-lg font-semibold mb-2">Metrics</h3>
                {/* Metrics Section */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 border rounded-lg">
                        <h4 className="font-semibold mb-2">Cash Flow & Income</h4>
                        <div className="space-y-1 text-sm">
                            <p>Net Monthly Flow: ${results.metrics.cash_flow.net_monthly_flow}</p>
                            <p>Income: ${results.metrics.cash_flow.income}</p>
                            <p>Expenses: ${results.metrics.cash_flow.expenses}</p>
                            <p>Beginning Balance: ${results.metrics.cash_flow.beginning_balance}</p>
                            <p>Ending Balance: ${results.metrics.cash_flow.ending_balance}</p>
                            <p>Regular Income Sources: {results.metrics.income_sources.regular}</p>
                            <p>Irregular Income Sources: {results.metrics.income_sources.irregular}</p>
                        </div>
                    </div>
                    <div className="p-4 border rounded-lg">
                        <h4 className="font-semibold mb-2">Debt & Financial Health</h4>
                        <div className="space-y-1 text-sm">
                            <p>Credit Utilization: {results.metrics.debt_and_savings.credit_utilization}</p>
                                {Array.isArray(results.metrics.debt_and_savings.outstanding_debt) && 
                                    results.metrics.debt_and_savings.outstanding_debt.map((debt, index) => (
                                        <p key={index}>Outstanding Debt: ${debt.amount} - {debt.description}</p>
                                    ))
                                }`
                            {results.metrics.debt_and_savings.financial_indicators.map((indicator, index) => (
                                <p key={index} className="ml-2">• {indicator.category}: {indicator.impact}</p>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}