import { motion, AnimatePresence } from "framer-motion";
import { Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface OrchestratorStatusProps {
    isProcessing: boolean;
    steps: string[];
}

export function OrchestratorStatus({ isProcessing, steps }: OrchestratorStatusProps) {
    return (
        <div className="w-full max-w-2xl mx-auto mb-4">
            <AnimatePresence>
                {isProcessing && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="flex items-center gap-2 p-3 mb-2 text-sm text-blue-600 bg-blue-50 rounded-md border border-blue-200"
                    >
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="font-semibold">Orchestrator Processing...</span>
                    </motion.div>
                )}
            </AnimatePresence>

            <div className="space-y-2">
                {steps.map((step, index) => (
                    <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center gap-2 text-sm text-muted-foreground"
                    >
                        <Badge variant="outline" className="h-5 px-1.5 text-[10px] uppercase">Step {index + 1}</Badge>
                        <span>{step}</span>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
