import React, { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Loader2, TrendingUp, Presentation, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { generateForecast } from '../api/client';

export const ForecastPage: React.FC = () => {
    const [isGenerating, setIsGenerating] = useState(false);
    const [report, setReport] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleGenerate = async () => {
        setIsGenerating(true);
        setError(null);
        setReport(null);
        try {
            const data = await generateForecast();
            if (data.error) {
                // Backend LLM or parsing errors that still returned nicely packed json
                setReport(data.markdown); 
            } else {
                setReport(data.markdown);
            }
        } catch (err: any) {
            setError(err.message || "An unexpected error occurred generating the forecast.");
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="flex-1 p-8 space-y-8 overflow-y-auto w-full h-full custom-scrollbar">
            {/* Header */}
            <div className="flex flex-col gap-2">
                <div className="flex items-center gap-3">
                    <div className="p-3 rounded-xl bg-purple-500/10 dark:bg-purple-500/20 text-purple-600 dark:text-purple-400 border border-purple-500/20">
                        <TrendingUp className="h-6 w-6" />
                    </div>
                    <h1 className="text-4xl font-bold tracking-tight text-foreground">
                        Predictive Forecasting
                    </h1>
                </div>
                <p className="text-muted-foreground max-w-2xl leading-relaxed mt-2 text-lg">
                    Leverage our hybrid AI architecture to uncover seasonal trends. 
                    The math engine (Prophet) analyzes tens of thousands of historical purchase records, 
                    while the LLM agent synthesizes the findings into actionable executive intelligence.
                </p>
            </div>

            {/* Main Action Area */}
            <div className="flex justify-start">
                <Button 
                    onClick={handleGenerate} 
                    disabled={isGenerating}
                    size="lg"
                    className="gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 shadow-lg shadow-purple-500/20 border-0 h-14 px-8 text-lg font-medium"
                >
                    {isGenerating ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            Analyzing Data...
                        </>
                    ) : (
                        <>
                            <Presentation className="w-5 h-5" />
                            Generate Trend Report
                        </>
                    )}
                </Button>
            </div>

            {/* Error State */}
            {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-600 dark:text-red-400 flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 mt-0.5 shrink-0" />
                    <p>{error}</p>
                </div>
            )}

            {/* Report Container */}
            <Card className="min-h-[400px] border-white/20 dark:border-white/10 bg-white/40 dark:bg-black/40 backdrop-blur-md shadow-2xl relative overflow-hidden">
                <div className="p-8">
                    {!report && !isGenerating && !error && (
                        <div className="h-[300px] flex flex-col items-center justify-center text-muted-foreground/60 gap-4">
                            <TrendingUp className="w-16 h-16 opacity-20" />
                            <p className="text-lg font-medium">Click generate to build the predictive report.</p>
                        </div>
                    )}
                    
                    {isGenerating && (
                        <div className="h-[300px] flex flex-col items-center justify-center text-muted-foreground gap-6">
                            <div className="relative">
                                <div className="absolute inset-0 bg-purple-500/20 blur-xl rounded-full"></div>
                                <Loader2 className="w-12 h-12 animate-spin text-purple-500 relative z-10" />
                            </div>
                            <div className="flex flex-col items-center gap-2">
                                <p className="text-lg font-medium text-foreground">Orchestrating Analytical Agents</p>
                                <p className="text-sm">Fetching 5000+ historical records → Training Time-Series Model → Extracting Seasonality → Prompting LLM</p>
                            </div>
                        </div>
                    )}

                    {report && !isGenerating && (
                        <div className="prose prose-purple dark:prose-invert max-w-none 
                            prose-headings:text-foreground prose-h1:text-3xl prose-h2:text-2xl 
                            prose-h3:text-purple-600 dark:prose-h3:text-purple-400 
                            prose-p:text-foreground/90 prose-li:text-foreground/90
                            prose-strong:text-foreground prose-strong:font-semibold
                            prose-table:border prose-table:border-border prose-th:bg-muted/50 prose-td:border-t prose-td:border-border">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                {report}
                            </ReactMarkdown>
                        </div>
                    )}
                </div>
            </Card>
        </div>
    );
};
