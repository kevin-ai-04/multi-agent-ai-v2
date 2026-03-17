import React, { useState, useEffect, useRef } from 'react';
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageBubble } from "./MessageBubble";
import { sendMessage } from "@/api/client";
import { OrchestratorStatus } from "./OrchestratorStatus";

export interface Message {
    role: 'user' | 'assistant';
    content: string;
    steps?: string[];
    ui_actions?: any[];
}

interface ChatInterfaceProps {
    agentEmailEnabled: boolean;
    agentComplianceEnabled: boolean;
    agentPdfEnabled: boolean;
    agentForecastEnabled: boolean;
    messages: Message[];
    setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
    input: string;
    setInput: (value: string) => void;
    isLoading: boolean;
    setIsLoading: (loading: boolean) => void;
    onUIAction?: (action: { action_type: string; params: any }) => void;
}

export function ChatInterface({
    agentEmailEnabled,
    agentComplianceEnabled,
    agentPdfEnabled,
    agentForecastEnabled,
    messages,
    setMessages,
    input,
    setInput,
    isLoading,
    setIsLoading,
    onUIAction
}: ChatInterfaceProps) {
    const [currentSteps, setCurrentSteps] = useState<string[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages, currentSteps, isLoading]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = input;
        setInput("");
        setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setIsLoading(true);
        setCurrentSteps([]);

        // simulate orchestrator thinking start
        setCurrentSteps(["Orchestrator: Analyzing input..."]);

        try {
            const response = await sendMessage({
                message: userMessage,
                agent_email_enabled: agentEmailEnabled,
                agent_compliance_enabled: agentComplianceEnabled,
                agent_pdf_enabled: agentPdfEnabled,
                agent_forecast_enabled: agentForecastEnabled,
            });

            // Update with final response
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: response.response_text,
                steps: response.steps,
                ui_actions: response.ui_actions
            }]);

            // Handle UI Actions from LLM
            if (response.ui_actions && onUIAction) {
                response.ui_actions.forEach((action: any) => {
                    if (action.action_type !== 'trigger_api') {
                        onUIAction(action);
                    }
                });
            }
            setCurrentSteps([]);

        } catch (error) {
            setMessages(prev => [...prev, { role: 'assistant', content: "Error: Failed to process request." }]);
        } finally {
            setIsLoading(false);
            setCurrentSteps([]);
        }
    };

    return (
        <div className="flex flex-col h-full bg-transparent">
            {/* Messages Area */}
            <ScrollArea className="flex-1 px-4 py-6">
                <div className="max-w-4xl mx-auto space-y-8">
                    {messages.map((msg, index) => (
                        <MessageBubble key={index} msg={msg} onActionClick={onUIAction} />
                    ))}

                    {/* Live Status Indicator (Floating) */}
                    {(isLoading || currentSteps.length > 0) && (
                        <div className="max-w-xl mx-auto my-4">
                            <OrchestratorStatus isProcessing={isLoading} steps={currentSteps} />
                        </div>
                    )}

                    <div ref={scrollRef} className="h-4" />
                </div>
            </ScrollArea>

            {/* Floating Input Area */}
            <div className="p-6 bg-transparent">
                <div className="max-w-3xl mx-auto rounded-full p-2 bg-white/70 dark:bg-black/70 backdrop-blur-xl border border-transparent flex items-center gap-2 transition-all duration-300 focus-within:bg-white/80 dark:focus-within:bg-black/80 focus-within:shadow-[0_0_0_1px_rgba(59,130,246,0.5),0_0_12px_rgba(6,182,212,0.4)] overflow-hidden bg-clip-padding">
                    <form onSubmit={handleSubmit} className="flex-1 flex items-center px-2">
                        <Input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type a number or text..."
                            className="flex-1 bg-transparent !border-none !shadow-none !ring-0 !outline-none focus-visible:ring-0 focus-visible:ring-offset-0 text-base py-6 placeholder:text-muted-foreground/70"
                            disabled={isLoading}
                        />
                        <Button
                            type="submit"
                            disabled={isLoading}
                            size="icon"
                            className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white shadow-lg shadow-blue-500/30 transition-all hover:scale-105"
                        >
                            <Send className="w-4 h-4" />
                        </Button>
                    </form>
                </div>
                <div className="text-center mt-2">
                    <span className="text-[10px] text-muted-foreground/50 uppercase tracking-widest">AI Powered Neural Converter</span>
                </div>
            </div>
        </div>
    );
}
