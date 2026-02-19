import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { sendMessage } from "@/api/client";
import { OrchestratorStatus } from "./OrchestratorStatus";

interface Message {
    role: 'user' | 'assistant';
    content: string;
    steps?: string[];
}

interface ChatInterfaceProps {
    agentAEnabled: boolean;
    agentBEnabled: boolean;
}

export function ChatInterface({ agentAEnabled, agentBEnabled }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
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
                input_text: userMessage,
                agent_a_enabled: agentAEnabled,
                agent_b_enabled: agentBEnabled
            });

            // Update with final response
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: response.response_text,
                steps: response.steps
            }]);
            setCurrentSteps([]); // Clear real-time steps as they are now in history if needed, or we can keep them briefly? 
            // Actually, let's keep the real-time steps empty and let the message history show steps if we want.
            // But for better UX, we can just show the final result and maybe an expander for steps?
            // For this implementation, I'll follow the Streamlit pattern: Show steps during processing.

        } catch (error) {
            setMessages(prev => [...prev, { role: 'assistant', content: "Error: Failed to process request." }]);
        } finally {
            setIsLoading(false);
            setCurrentSteps([]);
        }
    };

    return (
        <div className="flex flex-col h-full bg-background transition-colors duration-300">
            <ScrollArea className="flex-1 p-4">
                <div className="max-w-3xl mx-auto space-y-6">
                    {messages.map((msg, index) => (
                        <div key={index} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                            <Avatar className="w-8 h-8">
                                {msg.role === 'user' ? (
                                    <AvatarFallback className="bg-primary text-primary-foreground"><User className="w-4 h-4" /></AvatarFallback>
                                ) : (
                                    <AvatarFallback className="bg-accent text-accent-foreground"><Bot className="w-4 h-4" /></AvatarFallback>
                                )}
                            </Avatar>

                            <div className={`space-y-2 max-w-[80%]`}>
                                <Card className={`p-4 ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-card text-card-foreground'}`}>
                                    <p className="leading-relaxed">{msg.content}</p>
                                </Card>
                                {/* Show steps for assistant messages if available */}
                                {msg.role === 'assistant' && msg.steps && (
                                    <div className="text-xs text-muted-foreground pl-1">
                                        <details>
                                            <summary className="cursor-pointer hover:underline">View Thought Process</summary>
                                            <ul className="mt-2 space-y-1 list-disc list-inside">
                                                {msg.steps.map((step, i) => <li key={i}>{step}</li>)}
                                            </ul>
                                        </details>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}

                    {/* Live Status Indicator */}
                    {(isLoading || currentSteps.length > 0) && (
                        <div className="max-w-3xl mx-auto">
                            <OrchestratorStatus isProcessing={isLoading} steps={currentSteps} />
                        </div>
                    )}

                    <div ref={scrollRef} />
                </div>
            </ScrollArea>

            <div className="p-4 bg-background border-t">
                <form onSubmit={handleSubmit} className="flex gap-2 max-w-3xl mx-auto">
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type a message..."
                        className="flex-1"
                        disabled={isLoading}
                    />
                    <Button type="submit" disabled={isLoading} size="icon">
                        <Send className="w-4 h-4" />
                    </Button>
                </form>
            </div>
        </div>
    );
}
