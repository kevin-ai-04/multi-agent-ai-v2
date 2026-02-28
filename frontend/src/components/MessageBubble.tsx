import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Bot, User } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Message {
    role: 'user' | 'assistant';
    content: string;
    steps?: string[];
    ui_actions?: any[];
}

interface MessageBubbleProps {
    msg: Message;
    onActionClick?: (action: any) => void;
}

export function MessageBubble({ msg, onActionClick }: MessageBubbleProps) {
    return (
        <div className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''} animate-in fade-in slide-in-from-bottom-2 duration-500`}>

            {/* Avatar with Glow - Wrapped to prevent border aliasing */}
            {/* Avatar with Glow - Wrapped in separate div for clean border rendering */}
            <div className={`relative w-10 h-10 rounded-full flex-shrink-0 shadow-lg ${msg.role === 'user' ? 'shadow-cyan-500/30' : 'shadow-blue-500/30'}`}>
                <Avatar className="w-full h-full">
                    {msg.role === 'user' ? (
                        <AvatarFallback className="bg-cyan-600 text-white"><User className="w-5 h-5" /></AvatarFallback>
                    ) : (
                        <AvatarFallback className="bg-blue-600 text-white"><Bot className="w-5 h-5" /></AvatarFallback>
                    )}
                </Avatar>
            </div>

            <div className={`space-y-2 max-w-[75%]`}>
                {/* Message Bubble */}
                <div className={
                    `p-5 shadow-xl transition-all hover:scale-[1.01] duration-200 ${msg.role === 'user'
                        ? 'bg-gradient-to-br from-blue-600 to-cyan-600 text-white rounded-2xl rounded-tr-none shadow-blue-500/20'
                        : 'glass text-foreground rounded-2xl rounded-tl-none' // Glass effect for bot
                    }`
                }>
                    <p className="leading-relaxed text-[15px]">{msg.content}</p>
                </div>

                {/* Thought Process (Glass Card) */}
                {msg.role === 'assistant' && msg.steps && (
                    <div className="mt-2 rounded-xl overflow-hidden border border-white/20 dark:border-white/10 bg-white/40 dark:bg-black/20 backdrop-blur-sm">
                        <details className="group">
                            <summary className="cursor-pointer p-3 flex items-center text-xs font-semibold text-muted-foreground hover:text-primary transition-colors bg-white/20 dark:bg-black/20">
                                <div className="mr-2 h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                                View Neural Processing
                            </summary>
                            <div className="p-4 bg-black/5 dark:bg-white/5 border-t border-white/10">
                                <ul className="space-y-3">
                                    {msg.steps.map((step, i) => (
                                        <li key={i} className="text-xs flex items-start text-muted-foreground/80 font-mono">
                                            <span className="mr-2 text-blue-500 opacity-70">[{i + 1}]</span>
                                            {step}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </details>
                    </div>
                )}

                {/* UI Action Buttons (Quick Replies) */}
                {msg.role === 'assistant' && msg.ui_actions && msg.ui_actions.filter((a: any) => a.action_type === 'trigger_api').map((action: any, i: number) => (
                    <div key={i} className="mt-3 flex gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            className="bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 border-blue-500/30 font-medium"
                            onClick={() => onActionClick && onActionClick(action)}
                        >
                            {action.label || action.params?.label || "Execute Action"}
                        </Button>
                    </div>
                ))}
            </div>
        </div>
    );
}
