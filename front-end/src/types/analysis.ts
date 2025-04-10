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
                details: string;
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
            beginning_balance: number;
            ending_balance: number;
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
            recurring_debt_payments: string;
            inferred_liability_types: string;
            financial_indicators: Array<{
                category: string;
                observation: string;
                impact: string;
            }>;
        };
    };
}