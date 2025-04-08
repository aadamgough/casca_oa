"use client"

import { Button } from "@/components/ui/button";
import { AnalysisResults } from "@/types/analysis";

interface ResultsProps {
    isOpen: boolean;
    onClose: () => void;
    results: AnalysisResults;
}

export function AnalysisModal({ isOpen, onClose, results }: ResultsProps) {
    if (!isOpen || !results) return null;

    const getDecisionColor = (decision: string) => {
        switch (decision) {
            case 'Excellent: Loan Approved': return "text-green-500";
            case 'Good: Loan Approved': return "text-green-500";
            case 'Fair: Further information needed': return "text-yellow-500";
            case 'Concering: Loan Denied': return "text-red-500";
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
                </div>

                {/* Overall Score */}
                <div className="text-center mb-8">
                    <div className={`text-5xl font-bold ${getSeverityColor(results.summary.overall_score.toString())}`}>
                        Loan Score: {results.summary.overall_score}
                    </div>
                    <div className="text-xl mt-2">{results.summary.health_status}</div>
                </div>

                {/* Key Findings */}
                <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-2">Key Findings</h3>
                </div>

                {/* Component Scores */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                {Object.entries(results.detailed_analysis.components).map(([key, component]) => (
                    <div key={key} className="p-4 border rounded-lg">
                        <div className="flex justify-between items-center mb-2">
                            <h4 className="font-semibold capitalize">{key.replace('_', ' ')}</h4>
                            <span className={getDecisionColor(component.status)}>  {/* Use component.status instead of score */}
                                {component.score}
                            </span>
                        </div>
                        <p className="text-sm text-muted-foreground">{component.summary}</p>
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
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 border rounded-lg">
                        <h4 className="font-semibold mb-2">Cash Flow</h4>
                        <div className="space-y-1 text-sm">
                            <p>Credit Utilization: {results.metrics.debt_and_savings.credit_utilization}</p>
                            <p>Outstanding Debt: ${results.metrics.debt_and_savings.outstanding_debt}</p>
                            {/* Display financial indicators */}
                            <div className="mt-2">
                                <p className="font-medium">Key Indicators:</p>
                                {results.metrics.debt_and_savings.financial_indicators.map((indicator, index) => (
                                    <p key={index} className="ml-2">
                                        • {indicator.category}: {indicator.impact}
                                    </p>
                                ))}
                            </div>
                        </div>
                    </div>
                    <div className="p-4 border rounded-lg">
                        <h4 className="font-semibold mb-2">Debt & Savings</h4>
                        <div className="space-y-1 text-sm">
                            <p>Credit Utilization: {results.metrics.debt_and_savings.credit_utilization}</p>
                            <p>Outstanding Debt: ${results.metrics.debt_and_savings.outstanding_debt}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}