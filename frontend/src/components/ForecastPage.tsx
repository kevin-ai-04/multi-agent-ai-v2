import React, { useEffect } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Loader2, TrendingUp, Presentation, AlertCircle, Bot } from 'lucide-react';
import { generateForecast, fetchLatestForecast, fetchForecastHistory, fetchForecastById } from '../api/client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './ui/dropdown-menu';
import { History } from 'lucide-react';

export interface ForecastPageProps {
    isGenerating: boolean;
    setIsGenerating: (val: boolean) => void;
    report: string | null;
    setReport: (val: string | null) => void;
    chartData: any[] | null;
    setChartData: (val: any[] | null) => void;
    error: string | null;
    setError: (val: string | null) => void;
}

export const ForecastPage: React.FC<ForecastPageProps> = ({
    isGenerating, setIsGenerating, report, setReport, chartData, setChartData, error, setError
}) => {
    const [selectedItems, setSelectedItems] = React.useState<string[]>([]);
    const [history, setHistory] = React.useState<any[]>([]);

    React.useEffect(() => {
        fetchForecastHistory().then(res => {
            if (res.status === 'success') setHistory(res.data);
        }).catch(() => {});
    }, [isGenerating]);
    
    const allChartKeys = React.useMemo(() => {
        if (!chartData || chartData.length === 0) return [];
        return Object.keys(chartData[0]).filter(k => k !== 'name');
    }, [chartData]);

    React.useEffect(() => {
        if (allChartKeys.length > 0) {
            // Select up to 4 items initially so the chart isn't overly cluttered
            setSelectedItems(allChartKeys.slice(0, 4));
        } else {
            setSelectedItems([]);
        }
    }, [allChartKeys]);

    const colors = [
        "#8b5cf6", "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#ec4899", 
        "#6366f1", "#14b8a6", "#84cc16", "#eab308", "#f97316", "#f43f5e",
        "#d946ef", "#0ea5e9", "#22c55e"
    ];

    useEffect(() => {
        if (isGenerating || report) return; // Skip if already loaded or currently generating
        fetchLatestForecast()
            .then(res => {
                if (res.status === 'success' && res.data) {
                    setReport(res.data.markdown || null);
                    if (res.data.chart_data) {
                        try {
                            setChartData(JSON.parse(res.data.chart_data));
                        } catch(e) {}
                    }
                }
            })
            .catch(err => console.log("No stored forecast available."));
    }, [isGenerating, report, setReport, setChartData]);

    const handleGenerate = async () => {
        setIsGenerating(true);
        setError(null);
        setReport(null);
        setChartData(null);
        try {
            const data = await generateForecast();
            if (data.error) {
                // Backend LLM or parsing errors that still returned nicely packed json
                setReport(data.markdown); 
            } else {
                setReport(data.markdown);
            }
            if (data.chart_data) {
                setChartData(typeof data.chart_data === 'string' ? JSON.parse(data.chart_data) : data.chart_data);
            }
        } catch (err: any) {
            setError(err.message || "An unexpected error occurred generating the forecast.");
        } finally {
            setIsGenerating(false);
        }
    };

    const handleLoadHistory = async (id: number) => {
        try {
            const data = await fetchForecastById(id);
            if (data.status === 'success' && data.data) {
                setReport(data.data.markdown || null);
                if (data.data.chart_data) {
                    try {
                        setChartData(JSON.parse(data.data.chart_data));
                    } catch(e) {}
                }
            }
        } catch (err) {
            console.error("Failed to load history", err);
        }
    };

    const renderReportContent = () => {
        if (!report) return null;
        
        try {
            const parsed = JSON.parse(report);
            return (
                <div className="flex flex-col gap-10 w-full animate-in fade-in slide-in-from-bottom-4 duration-700">
                    {/* Executive Summary */}
                    <div className="bg-gradient-to-br from-purple-600 via-indigo-600 to-blue-700 rounded-[2rem] p-8 md:p-12 shadow-2xl text-white relative overflow-hidden">
                        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-64 h-64 bg-white/20 rounded-full blur-3xl"></div>
                        <h2 className="text-3xl font-black mb-6 flex items-center gap-3 drop-shadow-md">
                            <TrendingUp className="w-8 h-8 opacity-90" />
                            Executive Overview
                        </h2>
                        <p className="text-lg md:text-xl leading-relaxed opacity-95 font-medium drop-shadow-sm">
                            {parsed.executive_summary}
                        </p>
                    </div>

                    {/* Overall Trend */}
                    {parsed.overall_trend && (
                        <div className="bg-white dark:bg-gray-900 rounded-[2rem] p-8 shadow-xl border border-slate-200 dark:border-white/5 flex flex-col md:flex-row items-center gap-8 hover:shadow-2xl transition-shadow duration-500">
                            <div className="flex flex-col items-center justify-center min-w-[160px] p-6 rounded-[1.5rem] bg-slate-50 dark:bg-black/20 border border-slate-100 dark:border-white/5 shadow-inner">
                                <span className={`text-5xl font-black tracking-tighter ${parsed.overall_trend.direction?.toLowerCase() === 'downward' ? 'text-rose-500' : 'text-emerald-500'}`}>
                                    {parsed.overall_trend.percentage}%
                                </span>
                                <span className="text-slate-500 font-bold uppercase tracking-widest text-xs mt-3">
                                    {parsed.overall_trend.direction} Trend
                                </span>
                            </div>
                            <div className="flex-1">
                                <h3 className="text-2xl font-black text-slate-800 dark:text-slate-100 mb-3 tracking-tight">Macro Analysis</h3>
                                <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-lg">
                                    {parsed.overall_trend.analysis}
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Anomalies Grid */}
                    {parsed.anomalies && parsed.anomalies.length > 0 && (
                        <div className="mt-4">
                            <h3 className="text-2xl font-black text-slate-800 dark:text-slate-100 mb-8 tracking-tight">Key Component Insights</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
                                {parsed.anomalies.map((anomaly: any, idx: number) => {
                                    const isHigh = anomaly.severity?.toLowerCase() === 'high';
                                    return (
                                        <div key={idx} className="bg-white dark:bg-gray-900 flex flex-col rounded-[1.5rem] p-7 shadow-lg border border-slate-200 dark:border-white/5 hover:-translate-y-1 hover:shadow-2xl transition-all duration-300 relative overflow-hidden group">
                                            <div className={`absolute top-0 left-0 w-2 h-full transition-all duration-300 group-hover:w-3 ${isHigh ? 'bg-gradient-to-b from-rose-400 to-rose-600' : 'bg-gradient-to-b from-amber-400 to-orange-500'}`}></div>
                                            <div className="flex justify-between items-start mb-5 pl-2">
                                                <h4 className="text-xl font-bold text-slate-800 dark:text-slate-100 pr-4 leading-tight">{anomaly.item}</h4>
                                                <span className={`px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-widest ${isHigh ? 'bg-rose-100 text-rose-700 dark:bg-rose-500/20 dark:text-rose-400' : 'bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400'}`}>
                                                    {anomaly.severity}
                                                </span>
                                            </div>
                                            <p className="text-slate-600 dark:text-slate-400 mb-6 flex-1 pl-2 text-[1.05rem] leading-relaxed">
                                                {anomaly.insight}
                                            </p>
                                            <div className="mt-auto bg-slate-50 dark:bg-black/40 rounded-2xl p-5 border border-slate-100 dark:border-white/5 ml-2">
                                                <div className="text-[0.65rem] font-black text-purple-600 dark:text-purple-400 uppercase mb-2 tracking-widest flex items-center gap-2">
                                                    <div className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse"></div>
                                                    Recommended Strategy
                                                </div>
                                                <div className="text-slate-700 dark:text-slate-200 font-semibold text-[0.95rem] leading-snug">
                                                    {anomaly.recommended_action}
                                                </div>
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                        </div>
                    )}
                    
                    {/* Subtle LLM Model Label */}
                    {parsed.model_used && (
                        <div className="flex justify-end mt-4">
                            <span className="px-4 py-1.5 rounded-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-[0.65rem] font-black tracking-widest text-slate-500 uppercase flex items-center gap-2 shadow-sm">
                                <Bot className="w-3.5 h-3.5 text-purple-500" />
                                Synchronized via {parsed.model_used}
                            </span>
                        </div>
                    )}
                </div>
            );
        } catch (e) {
            // Fallback for old markdown reports
            return (
                <div className="bg-white dark:bg-gray-900 rounded-[2rem] p-10 md:p-14 border border-slate-200 dark:border-white/5 shadow-2xl">
                    <div className="text-purple-500 text-xs mb-6 font-black uppercase tracking-widest">Legacy Report Format</div>
                    <pre className="whitespace-pre-wrap font-sans text-slate-700 dark:text-slate-300 leading-relaxed text-lg">
                        {report.startsWith('#') ? report : `# Executive Forecast\n\n${report}`}
                    </pre>
                </div>
            );
        }
    };

    return (
        <div className="flex-1 p-8 space-y-8 overflow-y-auto w-full h-full custom-scrollbar">
            {/* Header Area */}
            <div className="flex justify-between items-start w-full gap-4 flex-col lg:flex-row">
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
                        The math engine analyzes historical records, while the LLM synthesizes actionable intelligence.
                    </p>
                </div>
                
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="outline" className="gap-2 bg-white/5 border-white/10 hover:bg-white/10 mt-2 lg:mt-0 shadow-lg">
                            <History className="w-4 h-4" />
                            View History
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-64 glass border-white/10 max-h-96 overflow-y-auto custom-scrollbar p-2">
                        {history.map((h: any) => (
                            <DropdownMenuItem 
                                key={h.id} 
                                onClick={() => handleLoadHistory(h.id)}
                                className="cursor-pointer gap-2 py-3 rounded-lg hover:bg-white/10 mb-1"
                            >
                                <div className="flex flex-col gap-1 w-full text-left">
                                    <span className="font-semibold text-sm">Report #{h.id}</span>
                                    <span className="text-xs text-muted-foreground">{new Date(h.created_at).toLocaleString()}</span>
                                </div>
                            </DropdownMenuItem>
                        ))}
                        {history.length === 0 && (
                            <div className="p-4 text-center text-sm text-muted-foreground">No history available</div>
                        )}
                    </DropdownMenuContent>
                </DropdownMenu>
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
                        <div className="flex flex-col gap-12 w-full pb-16">
                            {/* Render Dynamic UI Blocks */}
                            <div className="w-full flex justify-center mt-2">
                                <div className="w-full max-w-[1100px]">
                                    {renderReportContent()}
                                </div>
                            </div>
                            
                            {chartData && chartData.length > 0 && (
                                <div className="mt-12 pt-12 border-t border-slate-200 dark:border-white/10 max-w-[1000px] mx-auto w-full">
                                    <div className="flex flex-col mb-8 text-center md:text-left">
                                        <h3 className="text-3xl font-bold bg-gradient-to-r from-purple-700 to-indigo-600 dark:from-purple-400 dark:to-blue-400 bg-clip-text text-transparent mb-3 tracking-tight">
                                            Interactive Analysis Trends
                                        </h3>
                                        <p className="text-slate-500 dark:text-slate-400 text-lg">Select items below to toggle lines and isolate key components.</p>
                                    </div>
                                    
                                    {/* Interactive Legend / Filters */}
                                    <div className="flex flex-wrap justify-center md:justify-start gap-3 mb-10 p-6 md:p-8 bg-white dark:bg-black/20 rounded-[1.5rem] border border-slate-200 dark:border-white/5 shadow-sm">
                                        {allChartKeys.map((key, index) => {
                                            const isSelected = selectedItems.includes(key);
                                            const color = colors[index % colors.length];
                                            return (
                                                <button
                                                    key={key}
                                                    onClick={() => {
                                                        if (isSelected) {
                                                            setSelectedItems(prev => prev.filter(i => i !== key));
                                                        } else {
                                                            setSelectedItems(prev => [...prev, key]);
                                                        }
                                                    }}
                                                    className={`px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 border shadow-sm hover:scale-105 active:scale-95 ${isSelected ? '' : 'opacity-50 hover:opacity-80 bg-slate-50 dark:bg-transparent'}`}
                                                    style={{
                                                        backgroundColor: isSelected ? `${color}15` : undefined,
                                                        borderColor: isSelected ? color : 'currentColor',
                                                        color: isSelected ? color : '#64748b'
                                                    }}
                                                >
                                                    {key}
                                                </button>
                                            )
                                        })}
                                    </div>

                                    <div className="h-[550px] w-full bg-white dark:bg-gray-900/50 p-6 md:p-8 rounded-[2rem] border border-slate-200 dark:border-white/5 shadow-xl">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <LineChart
                                                data={chartData}
                                                margin={{ top: 10, right: 30, left: 20, bottom: 10 }}
                                            >
                                                <CartesianGrid strokeDasharray="4 4" stroke="#ffffff10" />
                                                <XAxis dataKey="name" stroke="#6b7280" tick={{fill: '#9ca3af'}} axisLine={false} tickLine={false} dy={10} />
                                                <YAxis stroke="#6b7280" tick={{fill: '#9ca3af'}} axisLine={false} tickLine={false} dx={-10} />
                                                <Tooltip 
                                                    contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', backdropFilter: 'blur(8px)', padding: '12px 16px', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)' }}
                                                    itemStyle={{ color: '#e5e7eb', fontSize: '14px', paddingVertical: '4px' }}
                                                    labelStyle={{ color: '#9ca3af', marginBottom: '8px', fontWeight: 'bold' }}
                                                />
                                                {allChartKeys
                                                    .filter(key => selectedItems.includes(key))
                                                    .map((key) => {
                                                        const index = allChartKeys.indexOf(key);
                                                        return (
                                                            <Line 
                                                                key={key}
                                                                type="monotone" 
                                                                dataKey={key} 
                                                                stroke={colors[index % colors.length]} 
                                                                strokeWidth={4}
                                                                dot={{ r: 5, strokeWidth: 2, fill: 'var(--background)', stroke: colors[index % colors.length] }}
                                                                activeDot={{ r: 8, strokeWidth: 0, fill: colors[index % colors.length] }}
                                                                animationDuration={1500}
                                                            />
                                                        );
                                                    })
                                                }
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </Card>
        </div>
    );
};
