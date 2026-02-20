import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
    DialogFooter
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
    Search,
    RotateCw,
    Reply,
    Forward,
    Trash2,
    PenSquare,
    Send as SendIcon,
    MoreHorizontal,
    Star,
    Mail,
    ArrowLeft,
    RefreshCw,
    Wand2,
    Loader2
} from "lucide-react";
import { fetchEmails, sendEmail, syncEmails, EmailItem, analyzeEmail, analyzeAllEmails, getEmailAnalysis } from "@/api/client";

interface EmailPageProps {
    folder: string;
}

export function EmailPage({ folder }: EmailPageProps) {
    const [emails, setEmails] = useState<EmailItem[]>([]);
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedEmail, setSelectedEmail] = useState<EmailItem | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isSyncing, setIsSyncing] = useState(false);

    // Compose State
    const [isComposeOpen, setIsComposeOpen] = useState(false);
    const [composeTo, setComposeTo] = useState("");
    const [composeSubject, setComposeSubject] = useState("");
    const [composeBody, setComposeBody] = useState("");
    const [isSending, setIsSending] = useState(false);

    // Analysis State
    const [isAnalyzingAll, setIsAnalyzingAll] = useState(false);
    const [analyzingEmailId, setAnalyzingEmailId] = useState<string | null>(null);
    const [analysisData, setAnalysisData] = useState<any | null>(null);
    const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(false);

    // Fetch Emails
    const loadEmails = async () => {
        setIsLoading(true);
        try {
            const data = await fetchEmails(folder);
            setEmails(data);
            setSelectedEmail(null); // Deselect on folder change
        } catch (error) {
            console.error("Failed to load emails", error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSync = async () => {
        setIsSyncing(true);
        try {
            await syncEmails(folder);
            await loadEmails();
        } catch (error) {
            alert("Failed to sync emails");
        } finally {
            setIsSyncing(false);
        }
    };

    useEffect(() => {
        loadEmails();
    }, [folder]);

    // Handle Analysis
    useEffect(() => {
        if (selectedEmail) {
            const fetchAnalysis = async () => {
                setIsLoadingAnalysis(true);
                setAnalysisData(null);
                try {
                    const res = await getEmailAnalysis(selectedEmail.id);
                    if (res.status === "success") {
                        setAnalysisData(res.data);
                    }
                } catch (e) {
                    console.error("Failed to fetch analysis", e);
                } finally {
                    setIsLoadingAnalysis(false);
                }
            };
            fetchAnalysis();
        } else {
            setAnalysisData(null);
        }
    }, [selectedEmail]);

    const handleAnalyzeEmail = async (emailId: string, e: React.MouseEvent) => {
        e.stopPropagation(); // Prevent opening email detail
        setAnalyzingEmailId(emailId);
        try {
            await analyzeEmail(emailId);
            await loadEmails(); // Reload emails to update has_analysis flag
        } catch (error) {
            alert("Failed to analyze email");
        } finally {
            setAnalyzingEmailId(null);
        }
    };

    const handleAnalyzeAll = async () => {
        setIsAnalyzingAll(true);
        try {
            await analyzeAllEmails();
            await loadEmails(); // refresh list
        } catch (error) {
            alert("Failed to analyze all emails");
        } finally {
            setIsAnalyzingAll(false);
        }
    };

    // Handle Send Email
    const handleSendEmail = async () => {
        if (!composeTo || !composeBody) {
            alert("Recipient and message body cannot be empty.");
            return;
        }
        setIsSending(true);
        try {
            await sendEmail({
                to_email: composeTo,
                subject: composeSubject,
                body: composeBody
            });
            setIsComposeOpen(false);
            setComposeTo("");
            setComposeSubject("");
            setComposeBody("");
            // Refresh if in sent folder
            if (folder === "sent") loadEmails();
            alert("Email sent successfully!");
        } catch (error) {
            alert("Failed to send email");
        } finally {
            setIsSending(false);
        }
    };

    const filteredEmails = emails.filter(email =>
    (email.sender.toLowerCase().includes(searchQuery.toLowerCase()) ||
        email.subject.toLowerCase().includes(searchQuery.toLowerCase()))
    );

    // ----------------------------------------------------------------------
    // View: Email Detail
    // ----------------------------------------------------------------------
    if (selectedEmail) {
        return (
            <div className="h-full flex flex-col bg-white/30 dark:bg-black/20 backdrop-blur-md">
                {/* Detail View Toolbar */}
                <div className="h-16 border-b border-white/20 px-6 flex items-center justify-between bg-white/40 dark:bg-black/40">
                    <div className="flex items-center gap-4">
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setSelectedEmail(null)}
                            className="hover:bg-white/20 dark:hover:bg-white/10"
                        >
                            <ArrowLeft className="h-5 w-5" />
                        </Button>
                        <div className="flex gap-2">
                            <Button variant="ghost" size="icon" className="hover:bg-white/20 dark:hover:bg-white/10">
                                <Reply className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="icon" className="hover:bg-white/20 dark:hover:bg-white/10">
                                <Forward className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="icon" className="text-red-400 hover:text-red-500 hover:bg-red-500/10">
                                <Trash2 className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Detail Content */}
                <ScrollArea className="flex-1 p-8">
                    <div className="max-w-3xl mx-auto">
                        <div className="mb-8">
                            <h1 className="text-2xl font-bold mb-4">{selectedEmail.subject}</h1>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-white font-bold">
                                        {selectedEmail.sender[0]?.toUpperCase()}
                                    </div>
                                    <div>
                                        <div className="font-semibold">{selectedEmail.sender}</div>
                                        <div className="text-xs text-muted-foreground">{selectedEmail.date}</div>
                                    </div>
                                </div>
                                <div className="text-xs text-muted-foreground bg-white/10 px-2 py-1 rounded-full border border-white/10 hidden">
                                    {selectedEmail.folder}
                                </div>
                            </div>
                        </div>

                        {/* Analysis Card */}
                        {isLoadingAnalysis && (
                            <div className="mb-8 p-6 rounded-xl border border-white/10 bg-white/5 animate-pulse flex items-center gap-3">
                                <Loader2 className="h-5 w-5 animate-spin text-purple-400" />
                                <span className="text-sm text-foreground/80">Loading Analysis...</span>
                            </div>
                        )}
                        {!isLoadingAnalysis && analysisData && (
                            <div className="mb-8 overflow-hidden rounded-xl border border-purple-500/20 bg-gradient-to-br from-purple-500/5 to-blue-500/5 backdrop-blur-sm">
                                <div className="px-6 py-3 border-b border-purple-500/10 bg-purple-500/10 flex items-center gap-2">
                                    <Wand2 className="h-4 w-4 text-purple-400" />
                                    <h3 className="text-sm font-semibold text-purple-200">AI Analysis Summary</h3>
                                </div>
                                <div className="p-6">
                                    <p className="text-sm text-foreground/90 mb-4">{analysisData.summary}</p>
                                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                                        <div>
                                            <span className="text-muted-foreground block text-xs">Priority</span>
                                            <span className={`font-medium ${analysisData.priority === 'High' ? 'text-red-400' :
                                                analysisData.priority === 'Medium' ? 'text-yellow-400' : 'text-green-400'
                                                }`}>{analysisData.priority}</span>
                                        </div>
                                        <div>
                                            <span className="text-muted-foreground block text-xs">Item</span>
                                            <span className="font-medium text-foreground">{analysisData.item_name}</span>
                                        </div>
                                        <div>
                                            <span className="text-muted-foreground block text-xs">Quantity</span>
                                            <span className="font-medium text-foreground">{analysisData.quantity} Units</span>
                                        </div>
                                        <div>
                                            <span className="text-muted-foreground block text-xs">Vendor</span>
                                            <span className="font-medium text-foreground">{analysisData.vendor_name || 'N/A'}</span>
                                        </div>
                                        <div>
                                            <span className="text-muted-foreground block text-xs">Vendor Email</span>
                                            <span className="font-medium text-foreground">{analysisData.vendor_email || 'N/A'}</span>
                                        </div>
                                        <div>
                                            <span className="text-muted-foreground block text-xs">Vendor Phone</span>
                                            <span className="font-medium text-foreground">{analysisData.vendor_phone || 'N/A'}</span>
                                        </div>
                                        <div>
                                            <span className="text-muted-foreground block text-xs">Unit Cost</span>
                                            <span className="font-medium text-foreground">
                                                {analysisData.item_unit_price ? `$${analysisData.item_unit_price.toLocaleString()}` : 'N/A'}
                                            </span>
                                        </div>
                                        <div>
                                            <span className="text-muted-foreground block text-xs">Total Cost</span>
                                            <span className="font-medium text-foreground">
                                                {analysisData.total_cost ? `$${analysisData.total_cost.toLocaleString()}` : 'N/A'}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div className="prose dark:prose-invert max-w-none text-foreground/90 whitespace-pre-wrap leading-relaxed font-sans">
                            {selectedEmail.body}
                        </div>
                    </div>
                </ScrollArea>
            </div>
        );
    }

    // ----------------------------------------------------------------------
    // View: Email List
    // ----------------------------------------------------------------------
    return (
        <div className="h-full flex flex-col bg-white/30 dark:bg-black/20 backdrop-blur-md">
            {/* List View Toolbar */}
            <div className="h-16 border-b border-white/20 px-6 flex items-center justify-between bg-white/40 dark:bg-black/40">
                <div className="flex items-center gap-4 flex-1">
                    <div className="relative flex-1 max-w-sm group">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-blue-500 transition-colors" />
                        <Input
                            placeholder={`Search ${folder}...`}
                            className="pl-9 bg-white/50 dark:bg-black/50 border-white/20 dark:border-white/10 focus-visible:ring-blue-500/50 transition-all focus:bg-white/80 dark:focus:bg-black/80"
                            value={searchQuery}
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(e.target.value)}
                        />
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={handleSync}
                        disabled={isSyncing}
                        className="text-muted-foreground hover:text-primary"
                        title="Sync from Server"
                    >
                        <RefreshCw className={`h-4 w-4 ${isSyncing ? 'animate-spin' : ''}`} />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={loadEmails} disabled={isLoading} className="text-muted-foreground hover:text-primary" title="Refresh View">
                        <RotateCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                    </Button>

                    {folder === 'inbox' && (
                        <Button
                            variant="outline"
                            className="gap-2 bg-purple-500/10 hover:bg-purple-500/20 text-purple-600 dark:text-purple-400 border-purple-500/20 ml-2 shadow-lg shadow-purple-500/10"
                            onClick={handleAnalyzeAll}
                            disabled={isAnalyzingAll}
                        >
                            {isAnalyzingAll ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
                            Analyze All
                        </Button>
                    )}

                    {/* Compose Dialog */}
                    <Dialog open={isComposeOpen} onOpenChange={setIsComposeOpen}>
                        <DialogTrigger asChild>
                            <Button className="gap-2 bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/20">
                                <PenSquare className="w-4 h-4" /> Compose
                            </Button>
                        </DialogTrigger>
                        <DialogContent className="sm:max-w-[600px] bg-white/95 dark:bg-gray-950/95 backdrop-blur-xl border-white/10">
                            <DialogHeader>
                                <DialogTitle>New Message</DialogTitle>
                            </DialogHeader>
                            <div className="grid gap-4 py-4">
                                <div className="grid grid-cols-4 items-center gap-4">
                                    <Label htmlFor="to" className="text-right">To</Label>
                                    <Input
                                        id="to"
                                        value={composeTo}
                                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setComposeTo(e.target.value)}
                                        className="col-span-3 bg-white/5"
                                        placeholder="recipient@example.com"
                                    />
                                </div>
                                <div className="grid grid-cols-4 items-center gap-4">
                                    <Label htmlFor="subject" className="text-right">Subject</Label>
                                    <Input
                                        id="subject"
                                        value={composeSubject}
                                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setComposeSubject(e.target.value)}
                                        className="col-span-3 bg-white/5"
                                        placeholder="Subject"
                                    />
                                </div>
                                <div className="grid grid-cols-4 items-start gap-4">
                                    <Label htmlFor="message" className="text-right pt-2">Message</Label>
                                    <Textarea
                                        id="message"
                                        value={composeBody}
                                        onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setComposeBody(e.target.value)}
                                        className="col-span-3 min-h-[200px] bg-white/5 font-mono text-sm"
                                        placeholder="Type your message here..."
                                    />
                                </div>
                            </div>
                            <DialogFooter>
                                <Button type="submit" onClick={handleSendEmail} disabled={isSending} className="gap-2 bg-blue-600 hover:bg-blue-500">
                                    {isSending ? 'Sending...' : <><SendIcon className="w-4 h-4" /> Send Email</>}
                                </Button>
                            </DialogFooter>
                        </DialogContent>
                    </Dialog>
                </div>
            </div>

            {/* Email List */}
            <ScrollArea className="flex-1">
                <div className="divide-y divide-white/10 dark:divide-white/5">
                    {filteredEmails.map((email) => (
                        <div
                            key={email.id}
                            onClick={() => setSelectedEmail(email)}
                            className="group px-6 py-4 hover:bg-white/40 dark:hover:bg-white/5 transition-colors cursor-pointer flex items-center gap-4"
                        >
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 flex items-center justify-center border border-white/10">
                                <span className="font-semibold text-sm text-gray-600 dark:text-gray-300">
                                    {email.sender[0]?.toUpperCase()}
                                </span>
                            </div>

                            <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between mb-0.5">
                                    <h4 className="text-sm font-semibold text-foreground truncate">
                                        {email.sender}
                                    </h4>
                                    <span className="text-xs text-muted-foreground whitespace-nowrap ml-2">
                                        {email.date}
                                    </span>
                                </div>
                                <h5 className="text-sm font-medium text-foreground/90 truncate">
                                    {email.subject}
                                </h5>
                                <p className="text-xs text-muted-foreground truncate opacity-80 group-hover:opacity-100 transition-opacity">
                                    {email.body}
                                </p>
                            </div>

                            <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                {!email.has_analysis && (
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-8 w-8 text-purple-500 hover:bg-purple-500/20 hover:text-purple-600"
                                        onClick={(e) => handleAnalyzeEmail(email.id, e)}
                                        disabled={analyzingEmailId === email.id}
                                        title="Analyze Email"
                                    >
                                        {analyzingEmailId === email.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <Wand2 className="h-4 w-4" />}
                                    </Button>
                                )}
                                <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-yellow-500/20 hover:text-yellow-500">
                                    <Star className="h-4 w-4" />
                                </Button>
                                <Button variant="ghost" size="icon" className="h-8 w-8">
                                    <MoreHorizontal className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    ))}

                    {isLoading && filteredEmails.length === 0 && (
                        <div className="flex flex-col items-center justify-center py-20 text-muted-foreground animate-pulse">
                            <RotateCw className="h-8 w-8 mb-4 animate-spin opacity-50" />
                            <p className="text-sm">Syncing emails...</p>
                        </div>
                    )}

                    {!isLoading && filteredEmails.length === 0 && (
                        <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
                            <Mail className="h-12 w-12 mb-4 opacity-20" />
                            <p className="text-lg font-medium">No emails in {folder}</p>
                        </div>
                    )}
                </div>
            </ScrollArea>
        </div>
    );
}
