export interface AnalysisResults {
    summary: {
        overall_score: number;
        health_status: string;
        key_findings: string;
    };
    detailed_analysis: {
        components: {
            [key: string]: {
                score: number;
                status: string;
                summary: string;
                details: any;
            };
        };
        narrative: string;
    };
    recommendations: {
        immediate_actions: string[];
        flags: Array<{
            type: string;
            severity: string;
            message: string;
        }>;
    };
    metrics: {
        cash_flow: {
            net_monthly_flow: number;
            income: number;
            expenses: number;
        };
        expense_breakdown: {
            major_expenses: number;
            recurring_expenses: number;
        };
        income_sources: {
            regular: number;
            irregular: number;
        };
        debt_and_savings: {
            credit_utilization: string;
            outstanding_debt: number;
            financial_indicators: Array<{
                category: string;
                observation: string;
                impact: string;
            }>;
        };
    };
}