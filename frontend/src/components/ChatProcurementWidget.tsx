import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, Download, CheckCircle2, XCircle, AlertCircle, ShoppingCart } from "lucide-react";

interface ChatProcurementWidgetProps {
    params: {
        mode: 'manual' | 'email';
        item_name?: string;
        email_id?: string;
    }
}

export function ChatProcurementWidget({ params }: ChatProcurementWidgetProps) {
    const [isLoading, setIsLoading] = useState(true);
    const [data, setData] = useState<any>(null);
    const [quantity, setQuantity] = useState<number>(1);

    // Status
    const [complianceStatus, setComplianceStatus] = useState<string>("Pending");
    const [complianceExplanation, setComplianceExplanation] = useState<string>("");
    const [orderId, setOrderId] = useState<number | null>(null);
    const [pdfPath, setPdfPath] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const [isCheckingCompliance, setIsCheckingCompliance] = useState(false);
    const [isGeneratingOrder, setIsGeneratingOrder] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            setIsLoading(true);
            setError(null);
            try {
                if (params.mode === 'manual' && params.item_name) {
                    const res = await fetch(`http://localhost:8000/items/lookup?name=${encodeURIComponent(params.item_name)}`);
                    if (!res.ok) throw new Error("Item not found. Please try checking the exact name.");
                    const json = await res.json();

                    setData({
                        item_name: json.item.name,
                        item_id: json.item.id,
                        vendor_name: json.vendor?.name || 'Unknown',
                        item_unit_price: json.item.unit_price,
                        total_cost: json.item.unit_price * quantity
                    });
                } else if (params.mode === 'email' && params.email_id) {
                    const res = await fetch(`http://localhost:8000/emails/${params.email_id}/analysis`);
                    if (!res.ok) throw new Error("Email analysis not found");
                    const json = await res.json();
                    if (json.status === "success" && json.data) {
                        setData(json.data);
                        setQuantity(json.data.item_quantity || 1);
                        setComplianceStatus(json.data.compliance_status || "Pending");
                        setComplianceExplanation(json.data.compliance_explanation || "");
                        setOrderId(json.data.order_id || null);
                        setPdfPath(json.data.pdf_path || null);
                    }
                } else {
                    throw new Error("Invalid parameters for procurement.");
                }
            } catch (err: any) {
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };
        fetchData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [params]);

    // Update total cost when quantity changes for manual mode
    useEffect(() => {
        if (params.mode === 'manual' && data && !orderId) {
            setData((prev: any) => ({
                ...prev,
                total_cost: prev.item_unit_price * quantity
            }));
        }
    }, [quantity, params.mode]);

    const handleRunCompliance = async () => {
        if (params.mode === 'email' && params.email_id) {
            setIsCheckingCompliance(true);
            try {
                const res = await fetch(`http://localhost:8000/procurement/${params.email_id}/compliance`, { method: "POST" });
                const json = await res.json();
                setComplianceStatus(json.passed ? "Passed" : "Failed");
                setComplianceExplanation(json.explanation);
            } catch (err: any) {
                alert(`Failed: ${err.message}`);
            } finally {
                setIsCheckingCompliance(false);
            }
        }
    };

    const handleGenerateOrder = async () => {
        setIsGeneratingOrder(true);
        setError(null);
        try {
            if (params.mode === 'manual') {
                const res = await fetch(`http://localhost:8000/orders/manual`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ item_name: data.item_name, quantity })
                });
                const json = await res.json();
                if (!res.ok) {
                    if (res.status === 400 && json.detail.startsWith("Compliance failed:")) {
                        setComplianceStatus("Failed");
                        setComplianceExplanation(json.detail.replace("Compliance failed: ", ""));
                        return;
                    }
                    throw new Error(json.detail || "Failed to generate order");
                }
                setOrderId(json.order_id);
                setPdfPath(json.pdf_path);
                setComplianceStatus("Passed");
                setComplianceExplanation("Auto-approved via manual order limits.");
            } else if (params.mode === 'email' && params.email_id) {
                const res = await fetch(`http://localhost:8000/procurement/${params.email_id}/order`, { method: "POST" });
                const json = await res.json();
                if (!res.ok) {
                    throw new Error(json.detail || "Failed to generate order");
                }
                if (json.status === "success" || json.order_id) {
                    setOrderId(json.order_id);
                    setPdfPath(json.pdf_path);
                }
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsGeneratingOrder(false);
        }
    };

    if (isLoading) {
        return (
            <div className="mt-4 p-4 rounded-xl border border-white/10 bg-white/5 animate-pulse flex items-center justify-center gap-3 w-full max-w-sm">
                <Loader2 className="h-5 w-5 animate-spin text-blue-400" />
                <span className="text-sm">Loading procurement data...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="mt-4 p-4 rounded-xl border border-red-500/20 bg-red-500/10 flex items-center gap-3 w-full max-w-sm text-red-500/90 text-sm">
                <AlertCircle className="h-5 w-5 shrink-0" />
                <p>{error}</p>
            </div>
        );
    }

    if (!data) return null;

    return (
        <div className="mt-4 w-full max-w-md rounded-2xl border border-white/10 bg-white/40 dark:bg-black/40 backdrop-blur-md overflow-hidden shadow-xl animate-in fade-in slide-in-from-bottom-2 duration-300">
            {/* Header */}
            <div className="px-5 py-3 border-b border-white/10 bg-blue-500/10 flex justify-between items-center">
                <div className="flex items-center gap-2 text-blue-700 dark:text-blue-300">
                    <ShoppingCart className="w-4 h-4" />
                    <span className="font-semibold text-sm">Procurement Order</span>
                </div>
                {orderId && (
                    <span className="text-xs font-mono bg-green-500/20 text-green-600 dark:text-green-400 px-2 py-0.5 rounded border border-green-500/30">
                        #{orderId}
                    </span>
                )}
            </div>

            <div className="p-5 space-y-4 text-sm">
                {/* Product Details */}
                <div className="space-y-2">
                    <div className="flex justify-between items-center">
                        <span className="text-muted-foreground text-xs uppercase">Item</span>
                        <span className="font-medium truncate max-w-[200px]">{data.item_name}</span>
                    </div>
                    <div className="flex justify-between items-center">
                        <span className="text-muted-foreground text-xs uppercase">Vendor</span>
                        <span className="font-medium text-right text-gray-700 dark:text-gray-300">{data.vendor_name}</span>
                    </div>
                    <div className="flex justify-between items-center">
                        <span className="text-muted-foreground text-xs uppercase">Unit Price</span>
                        <span className="font-mono">${data.item_unit_price?.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                        <span className="text-muted-foreground text-xs uppercase">Quantity</span>
                        {!orderId && params.mode === 'manual' ? (
                            <Input
                                type="number"
                                value={quantity}
                                onChange={(e) => setQuantity(Number(e.target.value))}
                                className="w-20 h-7 text-right bg-white/5 border-white/20"
                                min={1}
                            />
                        ) : (
                            <span className="font-medium">{quantity}</span>
                        )}
                    </div>
                </div>

                <div className="h-px bg-white/10 w-full" />

                <div className="flex justify-between items-center">
                    <span className="font-semibold">Total Cost</span>
                    <span className="font-mono font-bold text-lg text-blue-600 dark:text-blue-400">
                        ${data.total_cost?.toFixed(2) || (data.item_unit_price * quantity).toFixed(2)}
                    </span>
                </div>

                {/* Compliance Status Block */}
                {complianceStatus !== 'Pending' && (
                    <div className={`p-3 rounded-xl border flex gap-3 ${complianceStatus === 'Passed'
                        ? 'bg-green-500/10 border-green-500/20 text-green-600 dark:text-green-400'
                        : 'bg-red-500/10 border-red-500/20 text-red-600 dark:text-red-400'
                        }`}>
                        {complianceStatus === 'Passed' ? <CheckCircle2 className="w-5 h-5 shrink-0" /> : <XCircle className="w-5 h-5 shrink-0" />}
                        <div className="flex-1 text-xs">
                            <p className="font-semibold mb-1">Compliance {complianceStatus}</p>
                            <p className="opacity-80 leading-relaxed">{complianceExplanation}</p>
                        </div>
                    </div>
                )}

                {/* Actions */}
                <div className="pt-2">
                    {orderId ? (
                        <div className="flex flex-col gap-2">
                            <Button variant="default" className="w-full bg-green-600 hover:bg-green-500 text-white gap-2 pointer-events-none">
                                <CheckCircle2 className="w-4 h-4" /> Order Created
                            </Button>
                            {pdfPath && (
                                <a
                                    href={`http://localhost:8000${pdfPath.startsWith('/') ? '' : '/'}${pdfPath}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="w-full"
                                >
                                    <Button variant="outline" className="w-full gap-2 border-blue-500/30 text-blue-600 dark:text-blue-400 hover:bg-blue-500/10">
                                        <Download className="w-4 h-4" /> Download Purchase Order
                                    </Button>
                                </a>
                            )}
                        </div>
                    ) : (
                        <div className="flex gap-2">
                            {params.mode === 'email' && complianceStatus !== 'Passed' && complianceStatus !== 'Failed' && (
                                <Button
                                    className="flex-1 bg-blue-600 hover:bg-blue-500 text-white"
                                    onClick={handleRunCompliance}
                                    disabled={isCheckingCompliance}
                                >
                                    {isCheckingCompliance ? <Loader2 className="w-4 h-4 animate-spin" /> : "Run Compliance"}
                                </Button>
                            )}
                            {(!params.mode || params.mode === 'manual' || complianceStatus === 'Passed') && complianceStatus !== 'Failed' && (
                                <Button
                                    className="flex-1 bg-green-600 hover:bg-green-500 text-white"
                                    onClick={handleGenerateOrder}
                                    disabled={isGeneratingOrder}
                                >
                                    {isGeneratingOrder ? <Loader2 className="w-4 h-4 animate-spin" /> : "Place Order"}
                                </Button>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
