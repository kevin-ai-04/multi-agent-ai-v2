import { useState, useEffect, useCallback } from "react";
import { fetchOrdersPaginated, fetchOrdersSummary, type OrdersSummary } from "@/api/client";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
    Loader2, Calendar, FileText, Download, Building,
    DollarSign, Package, ShoppingCart, ChevronLeft, ChevronRight,
    ChevronsLeft, ChevronsRight, Search, X
} from "lucide-react";
import { format } from "date-fns";

const PER_PAGE = 20;

export function OrdersPage() {
    const [orders, setOrders] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Pagination state
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalOrders, setTotalOrders] = useState(0);

    const [searchInput, setSearchInput] = useState("");
    const [searchQuery, setSearchQuery] = useState("");

    // Summary state (loaded once)
    const [summary, setSummary] = useState<OrdersSummary | null>(null);

    // Load summary once
    useEffect(() => {
        fetchOrdersSummary().then(setSummary).catch(() => { });
    }, []);

    const loadOrders = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await fetchOrdersPaginated(
                page,
                PER_PAGE,
                searchQuery || undefined,
            );
            setOrders(data.orders);
            setTotalPages(data.total_pages);
            setTotalOrders(data.total);
        } catch (err: any) {
            setError(err.message || "Failed to load orders");
        } finally {
            setIsLoading(false);
        }
    }, [page, searchQuery]);

    useEffect(() => {
        loadOrders();
    }, [loadOrders]);

    // Reset to page 1 when filters change
    useEffect(() => {
        setPage(1);
    }, [searchQuery]);

    const handleSearch = () => {
        setSearchQuery(searchInput.trim());
    };

    const clearSearch = () => {
        setSearchInput("");
        setSearchQuery("");
    };


    return (
        <div className="flex h-full w-full overflow-hidden flex-col bg-white/30 dark:bg-black/20 backdrop-blur-md">
            {/* Header */}
            <div className="h-20 border-b border-white/20 px-8 flex items-center justify-between bg-white/40 dark:bg-black/40 backdrop-blur-xl z-10 shrink-0">
                <div className="flex flex-col">
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent flex items-center gap-3 tracking-tight">
                        <ShoppingCart className="h-6 w-6 text-blue-500" />
                        Purchase Orders Matrix
                    </h1>
                    <p className="text-sm text-muted-foreground mt-1">
                        Cryptographically signed procurement history. Contextual routing and compliance validation active.
                    </p>
                </div>

                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-4 bg-white/50 dark:bg-black/50 px-4 py-2 rounded-full border border-white/20 shadow-sm backdrop-blur-md">
                        <div className="flex flex-col items-end">
                            <span className="text-xs text-muted-foreground font-mono uppercase tracking-wider">Total Volume</span>
                            <span className="text-lg font-bold text-foreground">
                                ${(summary?.total_volume ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </span>
                        </div>
                    </div>
                    <div className="flex items-center gap-4 bg-white/50 dark:bg-black/50 px-4 py-2 rounded-full border border-white/20 shadow-sm backdrop-blur-md">
                        <div className="flex flex-col items-end">
                            <span className="text-xs text-muted-foreground font-mono uppercase tracking-wider">Orders</span>
                            <span className="text-lg font-bold text-foreground">
                                {(summary?.total_count ?? 0).toLocaleString()}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Filters Bar */}
            <div className="px-8 py-3 flex items-center gap-4 border-b border-white/10 bg-white/20 dark:bg-black/10 shrink-0">
                {/* Search */}
                <div className="relative flex-1 max-w-sm">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <input
                        type="text"
                        placeholder="Search orders..."
                        value={searchInput}
                        onChange={(e) => setSearchInput(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                        className="w-full pl-9 pr-8 py-2 text-sm rounded-lg border border-white/20 bg-white/50 dark:bg-black/30 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30 transition-all"
                    />
                    {searchInput && (
                        <button onClick={clearSearch} className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                            <X className="h-4 w-4" />
                        </button>
                    )}
                </div>


                {/* Page Info */}
                <div className="ml-auto text-sm text-muted-foreground font-mono">
                    Showing {orders.length} of {totalOrders.toLocaleString()} orders
                </div>
            </div>

            {/* List */}
            <ScrollArea className="flex-1 p-8">
                <div className="max-w-6xl mx-auto space-y-4">
                    {isLoading ? (
                        <div className="flex flex-col items-center justify-center p-20 text-muted-foreground space-y-4">
                            <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
                            <p className="animate-pulse">Accessing neural ledger...</p>
                        </div>
                    ) : error ? (
                        <div className="glass p-8 rounded-xl border border-red-500/20 text-red-500 flex flex-col items-center justify-center gap-4">
                            <div className="p-4 bg-red-500/10 rounded-full">
                                <FileText className="h-8 w-8 text-red-500" />
                            </div>
                            <p className="font-medium text-center">{error}</p>
                            <Button variant="outline" onClick={loadOrders} className="mt-4 border-red-500/20 hover:bg-red-500/10 hover:text-red-500">
                                Retry Connection
                            </Button>
                        </div>
                    ) : orders.length === 0 ? (
                        <div className="flex flex-col items-center justify-center p-32 text-muted-foreground glass border border-white/10 rounded-2xl bg-black/5">
                            <ShoppingCart className="h-16 w-16 mb-6 text-muted-foreground/30" />
                            <h3 className="text-xl font-semibold mb-2 text-foreground/70">Ledger Empty</h3>
                            <p className="max-w-sm text-center">No purchase orders found matching your criteria.</p>
                        </div>
                    ) : (
                        <div className="grid gap-4">
                            {orders.map((order) => (
                                <Card
                                    key={order.id}
                                    className="group relative overflow-hidden glass border-white/20 hover:border-blue-500/30 transition-all duration-500 hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:-translate-y-1 hover:bg-white/60 dark:hover:bg-black/60 p-0"
                                >
                                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-blue-500/80 shadow-[0_0_10px_rgba(59,130,246,0.5)]" />

                                    <div className="p-6 ml-2 flex flex-col md:flex-row gap-6 md:items-center">

                                        {/* ID */}
                                        <div className="flex flex-row md:flex-col items-center md:items-start justify-between md:justify-center w-full md:w-32 shrink-0 border-b md:border-b-0 md:border-r border-black/5 dark:border-white/10 pb-4 md:pb-0 md:pr-6 gap-2">
                                            <div className="flex flex-col">
                                                <span className="text-xs text-muted-foreground font-mono uppercase tracking-wider mb-1">REQ-ID</span>
                                                <span className="text-2xl font-black tracking-tighter text-foreground/80">#{order.id.toString().padStart(4, '0')}</span>
                                            </div>
                                        </div>

                                        {/* Core Details */}
                                        <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">

                                            {/* Item */}
                                            <div className="space-y-1.5">
                                                <p className="text-xs text-muted-foreground font-mono uppercase tracking-wider flex items-center gap-1.5 opacity-70">
                                                    <Package className="h-3 w-3" /> Material
                                                </p>
                                                <p className="font-semibold text-[15px] leading-tight text-foreground group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                                                    {order.item_name || 'Unknown Item'}
                                                </p>
                                                <div className="flex items-center gap-2 mt-1">
                                                    <Badge variant="secondary" className="bg-black/5 dark:bg-white/10 px-2 py-0 text-xs font-mono h-5 text-muted-foreground border-transparent">
                                                        QTY: {order.qty}
                                                    </Badge>
                                                    {order.unit_price && (
                                                        <span className="text-xs text-muted-foreground">@ ${order.unit_price} / ea</span>
                                                    )}
                                                </div>
                                            </div>

                                            {/* Vendor */}
                                            <div className="space-y-1.5">
                                                <p className="text-xs text-muted-foreground font-mono uppercase tracking-wider flex items-center gap-1.5 opacity-70">
                                                    <Building className="h-3 w-3" /> Supplier
                                                </p>
                                                <p className="font-medium text-[15px] leading-tight text-foreground truncate max-w-full">
                                                    {order.vendor_name || 'Unknown Vendor'}
                                                </p>
                                                <p className="text-xs text-muted-foreground truncate w-full group-hover:text-foreground/80 transition-colors">
                                                    {order.vendor_email || 'No email on file'}
                                                </p>
                                            </div>

                                            {/* Financials & Dates */}
                                            <div className="space-y-1.5">
                                                <p className="text-xs text-muted-foreground font-mono uppercase tracking-wider flex items-center gap-1.5 opacity-70">
                                                    <DollarSign className="h-3 w-3" /> Value
                                                </p>
                                                <p className="font-bold text-[15px] text-emerald-600 dark:text-emerald-400 tracking-tight">
                                                    ${(order.amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                                </p>
                                                <p className="text-xs text-muted-foreground font-mono flex items-center gap-1.5 opacity-60">
                                                    <Calendar className="h-3 w-3" />
                                                    {format(new Date(order.created_at || new Date()), "MMM dd, yyyy")}
                                                </p>
                                            </div>
                                        </div>

                                        {/* Actions */}
                                        <div className="w-full md:w-auto flex md:flex-col items-center justify-end gap-3 pt-4 md:pt-0 border-t md:border-t-0 border-black/5 dark:border-white/10 shrink-0 self-stretch md:pl-6">
                                            {order.pdf_path ? (
                                                <Button
                                                    variant="default"
                                                    className="w-full md:w-12 md:hover:w-32 group/btn relative overflow-hidden transition-all duration-300 bg-black hover:bg-gray-800 text-white dark:bg-white dark:text-black dark:hover:bg-gray-200 shadow-md"
                                                    asChild
                                                >
                                                    <a href={`http://localhost:8000/static/orders/${order.pdf_path.split('/').pop()}`} target="_blank" rel="noopener noreferrer">
                                                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none md:w-12 group-hover/btn:opacity-0 transition-opacity">
                                                            <Download className="h-4 w-4" />
                                                        </div>
                                                        <span className="flex items-center gap-2 md:opacity-0 md:w-0 group-hover/btn:opacity-100 group-hover/btn:w-auto overflow-hidden whitespace-nowrap transition-all delay-75 pointer-events-none">
                                                            <Download className="h-4 w-4 shrink-0" /> Open PDF
                                                        </span>
                                                    </a>
                                                </Button>
                                            ) : (
                                                <div className="h-9 w-12 rounded-md border border-dashed border-black/10 dark:border-white/10 flex items-center justify-center group-hover:border-blue-500/20 transition-colors" title="No PDF generated">
                                                    <FileText className="h-4 w-4 text-muted-foreground/30" />
                                                </div>
                                            )}
                                        </div>

                                    </div>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>

                {/* Pagination Controls */}
                {!isLoading && !error && totalPages > 1 && (
                    <div className="max-w-6xl mx-auto mt-8 flex items-center justify-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            disabled={page <= 1}
                            onClick={() => setPage(1)}
                            className="glass border-white/20 hover:border-blue-500/30"
                        >
                            <ChevronsLeft className="h-4 w-4" />
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            disabled={page <= 1}
                            onClick={() => setPage((p) => Math.max(1, p - 1))}
                            className="glass border-white/20 hover:border-blue-500/30"
                        >
                            <ChevronLeft className="h-4 w-4" />
                        </Button>

                        <div className="flex items-center gap-1 px-2">
                            {/* Show page numbers around current page */}
                            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                                let pageNum: number;
                                if (totalPages <= 5) {
                                    pageNum = i + 1;
                                } else if (page <= 3) {
                                    pageNum = i + 1;
                                } else if (page >= totalPages - 2) {
                                    pageNum = totalPages - 4 + i;
                                } else {
                                    pageNum = page - 2 + i;
                                }
                                return (
                                    <Button
                                        key={pageNum}
                                        variant={pageNum === page ? "default" : "outline"}
                                        size="sm"
                                        onClick={() => setPage(pageNum)}
                                        className={`w-9 h-9 ${pageNum === page
                                            ? 'bg-blue-600 text-white hover:bg-blue-700'
                                            : 'glass border-white/20 hover:border-blue-500/30'
                                            }`}
                                    >
                                        {pageNum}
                                    </Button>
                                );
                            })}
                        </div>

                        <Button
                            variant="outline"
                            size="sm"
                            disabled={page >= totalPages}
                            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                            className="glass border-white/20 hover:border-blue-500/30"
                        >
                            <ChevronRight className="h-4 w-4" />
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            disabled={page >= totalPages}
                            onClick={() => setPage(totalPages)}
                            className="glass border-white/20 hover:border-blue-500/30"
                        >
                            <ChevronsRight className="h-4 w-4" />
                        </Button>
                    </div>
                )}
                <div className="h-32" />
            </ScrollArea>
        </div>
    );
}
