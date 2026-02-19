import { useState, useEffect } from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Search, Filter, ArrowUpDown, Star, MoreHorizontal, Mail, ArrowLeft, Reply, Forward, Trash2 } from "lucide-react";

interface Email {
    id: number;
    sender: string;
    subject: string;
    preview: string;
    body: string;
    time: string;
    isStarred: boolean;
    isUnread: boolean;
    tag: string;
    folder: string;
}

const dummyEmails: Email[] = [
    {
        id: 1,
        sender: "Sarah Johnson",
        subject: "Project Update: Q1 Goals",
        preview: "Here are the updated KPIs for the first quarter given the new...",
        body: "Hi Team,\n\nHere are the updated KPIs for the first quarter given the new strategic direction. We need to focus on user retention and viral growth loops.\n\nPlease review the attached document and let me know your thoughts by EOD Friday.\n\nBest,\nSarah",
        time: "10:30 AM",
        isStarred: true,
        isUnread: true,
        tag: "Work",
        folder: "inbox"
    },
    {
        id: 2,
        sender: "Tech Daily",
        subject: "The Future of AI Agents",
        preview: "In today's newsletter, we dive deep into autonomous agents and...",
        body: "Welcome to Tech Daily!\n\nIn today's newsletter, we dive deep into autonomous agents and how they are reshaping the software landscape. From coding assistants to fully autonomous procurement bots, the future is agentic.\n\nRead more...",
        time: "9:15 AM",
        isStarred: false,
        isUnread: true,
        tag: "Newsletter",
        folder: "inbox"
    },
    {
        id: 3,
        sender: "Alex Chen",
        subject: "Lunch tomorrow?",
        preview: "Hey! Are we still on for trying that new sushi place downtown?",
        body: "Hey! Are we still on for trying that new sushi place downtown? I heard they have great lunch specials.\n\nLet me know!",
        time: "Yesterday",
        isStarred: false,
        isUnread: false,
        tag: "Personal",
        folder: "inbox"
    },
    {
        id: 4,
        sender: "Cloud Billing",
        subject: "Invoice #2024-001",
        preview: "Your monthly subscription has been renewed. View details attached...",
        body: "Dear Customer,\n\nYour monthly subscription has been renewed. The invoice #2024-001 is attached to this email.\n\nAmount: $29.99\n\nThank you for your business.",
        time: "Yesterday",
        isStarred: false,
        isUnread: false,
        tag: "Finance",
        folder: "inbox"
    },
    {
        id: 5,
        sender: "Me",
        subject: "Draft: Q2 Proposal",
        preview: "This is a draft for the upcoming Q2 planning meeting...",
        body: "This is a draft for the upcoming Q2 planning meeting. Need to add budget projections.",
        time: "2 days ago",
        isStarred: false,
        isUnread: false,
        tag: "Work",
        folder: "drafts"
    },
    {
        id: 6,
        sender: "Me",
        subject: "Re: Project Update",
        preview: "Thanks Sarah, received. Will review.",
        body: "Thanks Sarah, received. Will review and get back to you.",
        time: "3 days ago",
        isStarred: false,
        isUnread: false,
        tag: "Work",
        folder: "sent"
    }
];

interface EmailPageProps {
    folder?: string;
}

export function EmailPage({ folder = "inbox" }: EmailPageProps) {
    const [search, setSearch] = useState("");
    const [filter] = useState("all");
    const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);

    // Reset selection when folder changes
    useEffect(() => {
        setSelectedEmail(null);
    }, [folder]);

    const filteredEmails = dummyEmails.filter(email =>
        email.folder === folder &&
        (email.sender.toLowerCase().includes(search.toLowerCase()) ||
            email.subject.toLowerCase().includes(search.toLowerCase())) &&
        (filter === "all" || email.tag.toLowerCase() === filter.toLowerCase())
    );

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
                                        {selectedEmail.sender[0]}
                                    </div>
                                    <div>
                                        <div className="font-semibold">{selectedEmail.sender}</div>
                                        <div className="text-xs text-muted-foreground">{selectedEmail.time}</div>
                                    </div>
                                </div>
                                <div className="text-xs text-muted-foreground bg-white/10 px-2 py-1 rounded-full border border-white/10">
                                    {selectedEmail.tag}
                                </div>
                            </div>
                        </div>
                        <div className="prose dark:prose-invert max-w-none text-foreground/90 whitespace-pre-wrap leading-relaxed">
                            {selectedEmail.body}
                        </div>
                    </div>
                </ScrollArea>
            </div>
        );
    }

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
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-primary">
                        <Filter className="h-4 w-4 mr-2" />
                        Filter
                    </Button>
                    <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-primary">
                        <ArrowUpDown className="h-4 w-4 mr-2" />
                        Sort
                    </Button>
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
                            <div className="flex-shrink-0">
                                {email.isUnread && <div className="w-2.5 h-2.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]" />}
                            </div>

                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 flex items-center justify-center border border-white/10">
                                <span className="font-semibold text-sm text-gray-600 dark:text-gray-300">
                                    {email.sender[0]}
                                </span>
                            </div>

                            <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between mb-0.5">
                                    <h4 className={`text-sm truncate ${email.isUnread ? 'font-semibold text-foreground' : 'font-medium text-muted-foreground'}`}>
                                        {email.sender}
                                    </h4>
                                    <span className="text-xs text-muted-foreground whitespace-nowrap ml-2">
                                        {email.time}
                                    </span>
                                </div>
                                <h5 className="text-sm font-medium text-foreground/90 truncate">
                                    {email.subject}
                                </h5>
                                <p className="text-xs text-muted-foreground truncate opacity-80 group-hover:opacity-100 transition-opacity">
                                    {email.preview}
                                </p>
                            </div>

                            <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-yellow-500/20 hover:text-yellow-500">
                                    <Star className={`h-4 w-4 ${email.isStarred ? 'fill-yellow-500 text-yellow-500' : ''}`} />
                                </Button>
                                <Button variant="ghost" size="icon" className="h-8 w-8">
                                    <MoreHorizontal className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    ))}

                    {filteredEmails.length === 0 && (
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
