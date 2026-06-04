import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { walletAPI } from '@/services/api';
import { useAuth } from '@/hooks/useAuth';
import { toast } from 'sonner';
import { 
  Wallet, 
  ArrowUpRight, 
  ArrowDownLeft, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Lock, 
  Unlock, 
  TrendingUp, 
  Building,
  RefreshCw,
  Search
} from 'lucide-react';

const WalletPage = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const isAdmin = user?.role === 'admin';

  // State
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [upiId, setUpiId] = useState('');
  const [bankAcc, setBankAcc] = useState('');
  const [bankIfsc, setBankIfsc] = useState('');
  const [withdrawMethod, setWithdrawMethod] = useState<'upi' | 'bank'>('upi');
  const [searchWorkerId, setSearchWorkerId] = useState('');
  const [rejectReasons, setRejectReasons] = useState<Record<string, string>>({});

  // Queries
  const { data: wallet, isLoading: loadingWallet, refetch: refetchWallet } = useQuery({
    queryKey: ['wallet'],
    queryFn: walletAPI.getWallet,
    enabled: !isAdmin,
  });

  const { data: transactions, isLoading: loadingTx } = useQuery({
    queryKey: ['wallet-transactions'],
    queryFn: walletAPI.getTransactions,
    enabled: !isAdmin,
  });

  const { data: withdrawals, isLoading: loadingWithdrawals } = useQuery({
    queryKey: ['wallet-withdrawals'],
    queryFn: walletAPI.getWithdrawals,
    enabled: !isAdmin,
  });

  // Admin Queries
  const { data: adminWallets, isLoading: loadingAdminWallets } = useQuery({
    queryKey: ['admin-wallets'],
    queryFn: walletAPI.getAdminWallets,
    enabled: isAdmin,
  });

  const { data: adminWithdrawals, isLoading: loadingAdminWithdrawals } = useQuery({
    queryKey: ['admin-withdrawals'],
    queryFn: walletAPI.getAdminWithdrawals,
    enabled: isAdmin,
  });

  const { data: walletAnalytics, isLoading: loadingAnalytics } = useQuery({
    queryKey: ['wallet-analytics'],
    queryFn: walletAPI.getWalletAnalytics,
    enabled: isAdmin,
  });

  // Mutations
  const withdrawMutation = useMutation({
    mutationFn: walletAPI.withdraw,
    onSuccess: (res) => {
      toast.success(res.message || 'Withdrawal requested successfully');
      setWithdrawAmount('');
      setUpiId('');
      setBankAcc('');
      setBankIfsc('');
      queryClient.invalidateQueries({ queryKey: ['wallet'] });
      queryClient.invalidateQueries({ queryKey: ['wallet-transactions'] });
      queryClient.invalidateQueries({ queryKey: ['wallet-withdrawals'] });
    },
    onError: (err: any) => {
      toast.error(err.message || 'Failed to request withdrawal');
    }
  });

  const approveMutation = useMutation({
    mutationFn: walletAPI.approveWithdrawal,
    onSuccess: () => {
      toast.success('Withdrawal request approved');
      queryClient.invalidateQueries({ queryKey: ['admin-withdrawals'] });
      queryClient.invalidateQueries({ queryKey: ['admin-wallets'] });
      queryClient.invalidateQueries({ queryKey: ['wallet-analytics'] });
    },
    onError: (err: any) => {
      toast.error(err.message || 'Failed to approve withdrawal');
    }
  });

  const rejectMutation = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) => walletAPI.rejectWithdrawal(id, reason),
    onSuccess: () => {
      toast.success('Withdrawal request rejected');
      queryClient.invalidateQueries({ queryKey: ['admin-withdrawals'] });
      queryClient.invalidateQueries({ queryKey: ['admin-wallets'] });
      queryClient.invalidateQueries({ queryKey: ['wallet-analytics'] });
    },
    onError: (err: any) => {
      toast.error(err.message || 'Failed to reject withdrawal');
    }
  });

  const freezeMutation = useMutation({
    mutationFn: ({ workerId, freeze }: { workerId: string; freeze: boolean }) => walletAPI.freezeWallet(workerId, freeze),
    onSuccess: (res) => {
      toast.success(`Wallet ${res.status === 'frozen' ? 'frozen' : 'unfrozen'} successfully`);
      queryClient.invalidateQueries({ queryKey: ['admin-wallets'] });
    },
    onError: (err: any) => {
      toast.error(err.message || 'Failed to update wallet status');
    }
  });

  // Handlers
  const handleWithdrawSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!withdrawAmount || isNaN(Number(withdrawAmount)) || Number(withdrawAmount) <= 0) {
      toast.error('Please enter a valid amount');
      return;
    }
    const destDetails = withdrawMethod === 'upi' 
      ? { upi_id: upiId } 
      : { bank_account: bankAcc, ifsc: bankIfsc };

    withdrawMutation.mutate({
      amount: Number(withdrawAmount),
      destination_details: destDetails
    });
  };

  const handleApprove = (id: string) => {
    approveMutation.mutate(id);
  };

  const handleReject = (id: string) => {
    const reason = rejectReasons[id] || 'Rejected by administrator';
    rejectMutation.mutate({ id, reason });
  };

  const handleFreezeToggle = (workerId: string, currentStatus: string) => {
    freezeMutation.mutate({
      workerId,
      freeze: currentStatus !== 'frozen'
    });
  };

  // Render Status Badge
  const renderStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
      case 'approved':
        return <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-medium text-emerald-500"><CheckCircle className="h-3.5 w-3.5" /> Approved</span>;
      case 'rejected':
      case 'failed':
        return <span className="inline-flex items-center gap-1 rounded-full bg-rose-500/10 px-2.5 py-0.5 text-xs font-medium text-rose-500"><XCircle className="h-3.5 w-3.5" /> Rejected</span>;
      case 'pending_approval':
        return <span className="inline-flex items-center gap-1 rounded-full bg-amber-500/10 px-2.5 py-0.5 text-xs font-medium text-amber-500"><Clock className="h-3.5 w-3.5" /> Review Required</span>;
      default:
        return <span className="inline-flex items-center gap-1 rounded-full bg-blue-500/10 px-2.5 py-0.5 text-xs font-medium text-blue-500"><AlertCircle className="h-3.5 w-3.5" /> {status}</span>;
    }
  };

  return (
    <div className="p-4 md:p-6 space-y-6 animate-fade-in">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">GigSurance Wallet</h1>
          <p className="text-sm text-muted-foreground">Manage your earnings, payouts, and withdrawals in real time.</p>
        </div>
        {wallet && wallet.status === 'frozen' && (
          <div className="flex items-center gap-2 rounded-lg bg-rose-500/15 border border-rose-500/35 px-4 py-2 text-rose-500 font-semibold animate-pulse">
            <Lock className="h-5 w-5" /> Wallet Frozen by Admin
          </div>
        )}
      </div>

      {/* ========================================================= */}
      {/* WORKER VIEW */}
      {/* ========================================================= */}
      {!isAdmin && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left panel: Balance + Withdraw */}
          <div className="lg:col-span-2 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Available Balance Card */}
              <div className="relative overflow-hidden rounded-xl border bg-card p-6 shadow-md bg-gradient-to-br from-indigo-500/10 via-transparent to-primary/5">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Available for Withdrawal</p>
                    <h3 className="text-3xl font-bold mt-1 text-foreground">
                      ₹{loadingWallet ? '...' : wallet?.available_balance?.toLocaleString('en-IN') || '0.00'}
                    </h3>
                  </div>
                  <div className="rounded-lg bg-primary/10 p-2 text-primary">
                    <Wallet className="h-6 w-6" />
                  </div>
                </div>
                <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
                  <span className="text-emerald-500 font-medium inline-flex items-center gap-1">
                    <ArrowUpRight className="h-3 w-3" /> Auto-Approved
                  </span>
                  for requests ≤ ₹10,000
                </div>
              </div>

              {/* Pending Balance Card */}
              <div className="relative overflow-hidden rounded-xl border bg-card p-6 shadow-md">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Pending Security Lock</p>
                    <h3 className="text-3xl font-bold mt-1 text-foreground">
                      ₹{loadingWallet ? '...' : wallet?.pending_balance?.toLocaleString('en-IN') || '0.00'}
                    </h3>
                  </div>
                  <div className="rounded-lg bg-amber-500/10 p-2 text-amber-500">
                    <Clock className="h-6 w-6" />
                  </div>
                </div>
                <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
                  <span className="text-amber-500 font-medium">24h Review Window</span>
                  before funds move to available balance.
                </div>
              </div>
            </div>

            {/* Withdrawal request form */}
            <div className="rounded-xl border bg-card p-6 shadow-md">
              <h2 className="text-lg font-semibold mb-4 text-foreground flex items-center gap-2">
                <ArrowUpRight className="h-5 w-5 text-primary" /> Request Withdrawal
              </h2>
              <form onSubmit={handleWithdrawSubmit} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-foreground">Amount (₹)</label>
                  <input
                    type="number"
                    value={withdrawAmount}
                    onChange={(e) => setWithdrawAmount(e.target.value)}
                    placeholder="Enter amount to withdraw"
                    disabled={wallet?.status === 'frozen' || withdrawMutation.isPending}
                    className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-foreground">Transfer Method</label>
                  <div className="flex gap-4">
                    <button
                      type="button"
                      onClick={() => setWithdrawMethod('upi')}
                      className={`flex-1 rounded-lg py-2 text-sm font-medium border transition-colors ${withdrawMethod === 'upi' ? 'bg-primary/10 border-primary text-primary' : 'bg-background border-input text-muted-foreground'}`}
                    >
                      UPI ID
                    </button>
                    <button
                      type="button"
                      onClick={() => setWithdrawMethod('bank')}
                      className={`flex-1 rounded-lg py-2 text-sm font-medium border transition-colors ${withdrawMethod === 'bank' ? 'bg-primary/10 border-primary text-primary' : 'bg-background border-input text-muted-foreground'}`}
                    >
                      Bank Account
                    </button>
                  </div>
                </div>

                {withdrawMethod === 'upi' ? (
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-muted-foreground">UPI ID</label>
                    <input
                      type="text"
                      value={upiId}
                      onChange={(e) => setUpiId(e.target.value)}
                      placeholder="e.g. worker@ybl"
                      required={withdrawMethod === 'upi'}
                      disabled={wallet?.status === 'frozen' || withdrawMutation.isPending}
                      className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    />
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">Account Number</label>
                      <input
                        type="text"
                        value={bankAcc}
                        onChange={(e) => setBankAcc(e.target.value)}
                        placeholder="Bank account number"
                        required={withdrawMethod === 'bank'}
                        disabled={wallet?.status === 'frozen' || withdrawMutation.isPending}
                        className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">IFSC Code</label>
                      <input
                        type="text"
                        value={bankIfsc}
                        onChange={(e) => setBankIfsc(e.target.value)}
                        placeholder="IFSC code"
                        required={withdrawMethod === 'bank'}
                        disabled={wallet?.status === 'frozen' || withdrawMutation.isPending}
                        className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none"
                      />
                    </div>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={wallet?.status === 'frozen' || withdrawMutation.isPending}
                  className="w-full rounded-lg bg-primary py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {withdrawMutation.isPending ? 'Processing...' : 'Request Cashout'}
                </button>
              </form>
            </div>
          </div>

          {/* Right panel: Transactions */}
          <div className="space-y-6">
            <div className="rounded-xl border bg-card p-6 shadow-md flex flex-col h-[525px]">
              <h2 className="text-lg font-semibold mb-4 text-foreground flex items-center gap-2">
                <ArrowDownLeft className="h-5 w-5 text-emerald-500" /> Recent Wallet Activity
              </h2>
              <div className="overflow-y-auto flex-1 pr-1 space-y-4">
                {loadingTx ? (
                  <p className="text-sm text-muted-foreground">Loading transaction logs...</p>
                ) : transactions?.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No recent transaction history found.</p>
                ) : (
                  transactions?.map((tx: any) => (
                    <div key={tx.id} className="flex justify-between items-center p-3 rounded-lg bg-muted/40 border border-muted/70 hover:bg-muted/65 transition-colors">
                      <div className="space-y-1">
                        <p className="text-xs font-semibold text-foreground capitalize">
                          {tx.type.replace(/_/g, ' ')}
                        </p>
                        <p className="text-[10px] text-muted-foreground">{tx.description}</p>
                        <p className="text-[9px] text-muted-foreground/80">
                          {new Date(tx.created_at).toLocaleString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className={`text-sm font-bold ${tx.type.includes('credit') || tx.type.includes('refund') || tx.type.includes('release') ? 'text-emerald-500' : 'text-rose-500'}`}>
                          {tx.type.includes('credit') || tx.type.includes('refund') || tx.type.includes('release') ? '+' : '-'}₹{tx.amount}
                        </p>
                        <p className="text-[9px] text-muted-foreground/80">Bal: ₹{tx.running_available}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================= */}
      {/* ADMIN VIEW */}
      {/* ========================================================= */}
      {isAdmin && (
        <div className="space-y-6">
          {/* KPI Analytics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="rounded-xl border bg-card p-6 shadow-md">
              <p className="text-sm font-medium text-muted-foreground">Total Available Funds</p>
              <h3 className="text-3xl font-bold mt-1 text-foreground">
                ₹{loadingAnalytics ? '...' : walletAnalytics?.total_available_all_wallets?.toLocaleString('en-IN') || '0.00'}
              </h3>
              <p className="text-xs text-muted-foreground mt-2">Available across all wallets</p>
            </div>
            <div className="rounded-xl border bg-card p-6 shadow-md">
              <p className="text-sm font-medium text-muted-foreground">Total Locked Funds</p>
              <h3 className="text-3xl font-bold mt-1 text-foreground">
                ₹{loadingAnalytics ? '...' : walletAnalytics?.total_pending_all_wallets?.toLocaleString('en-IN') || '0.00'}
              </h3>
              <p className="text-xs text-muted-foreground mt-2">Currently locked under 24h fraud review</p>
            </div>
            <div className="rounded-xl border bg-card p-6 shadow-md">
              <p className="text-sm font-medium text-muted-foreground">Pending Approvals</p>
              <h3 className="text-3xl font-bold mt-1 text-foreground">
                {loadingAnalytics ? '...' : walletAnalytics?.pending_approvals_count || '0'}
              </h3>
              <p className="text-xs text-muted-foreground mt-2">Cashout requests exceeding ₹10,000</p>
            </div>
            <div className="rounded-xl border bg-card p-6 shadow-md">
              <p className="text-sm font-medium text-muted-foreground">Frozen Wallets</p>
              <h3 className="text-3xl font-bold mt-1 text-foreground">
                {loadingAnalytics ? '...' : walletAnalytics?.total_frozen_wallets || '0'}
              </h3>
              <p className="text-xs text-muted-foreground mt-2">Wallets currently locked by operations</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Pending Approvals Table */}
            <div className="lg:col-span-2 rounded-xl border bg-card p-6 shadow-md space-y-4">
              <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <Clock className="h-5 w-5 text-amber-500 animate-pulse" /> Pending Cashout Reviews (&gt; ₹10,000)
              </h2>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm border-collapse">
                  <thead>
                    <tr className="border-b text-muted-foreground font-semibold">
                      <th className="py-2">Worker ID</th>
                      <th className="py-2">Amount</th>
                      <th className="py-2">Method Details</th>
                      <th className="py-2 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {loadingAdminWithdrawals ? (
                      <tr><td colSpan={4} className="py-4 text-center text-muted-foreground">Loading pending reviews...</td></tr>
                    ) : adminWithdrawals?.length === 0 ? (
                      <tr><td colSpan={4} className="py-4 text-center text-muted-foreground">No pending withdrawal approvals.</td></tr>
                    ) : (
                      adminWithdrawals?.map((req: any) => (
                        <tr key={req.id} className="border-b hover:bg-muted/20">
                          <td className="py-3 font-medium text-foreground">{req.user_id}</td>
                          <td className="py-3 font-semibold text-primary">₹{req.amount}</td>
                          <td className="py-3 text-xs text-muted-foreground">
                            {req.destination_details?.upi_id ? (
                              <span>UPI: {req.destination_details.upi_id}</span>
                            ) : (
                              <span>Bank: {req.destination_details.bank_account} (IFSC: {req.destination_details.ifsc})</span>
                            )}
                          </td>
                          <td className="py-3 text-right">
                            <div className="flex flex-col gap-2 justify-end">
                              <div className="flex gap-2 justify-end">
                                <button
                                  onClick={() => handleApprove(req.id)}
                                  className="rounded bg-emerald-500 px-3 py-1 text-xs font-semibold text-white hover:bg-emerald-600 transition-colors"
                                >
                                  Approve
                                </button>
                                <button
                                  onClick={() => handleReject(req.id)}
                                  className="rounded bg-rose-500 px-3 py-1 text-xs font-semibold text-white hover:bg-rose-600 transition-colors"
                                >
                                  Reject
                                </button>
                              </div>
                              <input
                                type="text"
                                placeholder="Rejection reason..."
                                value={rejectReasons[req.id] || ''}
                                onChange={(e) => setRejectReasons({...rejectReasons, [req.id]: e.target.value})}
                                className="rounded border border-input bg-background px-2 py-0.5 text-[10px] w-48 ml-auto focus:outline-none focus:ring-1 focus:ring-primary"
                              />
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Wallets Control List */}
            <div className="rounded-xl border bg-card p-6 shadow-md space-y-4">
              <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <Search className="h-5 w-5 text-primary" /> Wallet Operations Controls
              </h2>
              <input
                type="text"
                placeholder="Search by worker ID..."
                value={searchWorkerId}
                onChange={(e) => setSearchWorkerId(e.target.value)}
                className="w-full rounded-lg border border-input bg-background px-3 py-1.5 text-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary"
              />
              <div className="space-y-4 max-h-[350px] overflow-y-auto pr-1">
                {loadingAdminWallets ? (
                  <p className="text-xs text-muted-foreground">Loading user wallets...</p>
                ) : (
                  adminWallets
                    ?.filter((w: any) => !searchWorkerId || w.user_id.toLowerCase().includes(searchWorkerId.toLowerCase()))
                    ?.map((w: any) => (
                      <div key={w.user_id} className="flex justify-between items-center p-3 rounded-lg bg-muted/40 border border-muted/60">
                        <div className="space-y-1">
                          <p className="text-xs font-semibold text-foreground truncate w-40">{w.user_id}</p>
                          <p className="text-[10px] text-muted-foreground">Available: ₹{w.available_balance} | Locked: ₹{w.pending_balance}</p>
                        </div>
                        <button
                          onClick={() => handleFreezeToggle(w.user_id, w.status)}
                          className={`rounded px-2.5 py-1 text-[10px] font-semibold flex items-center gap-1 transition-colors ${w.status === 'frozen' ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 hover:bg-emerald-500/20' : 'bg-rose-500/10 text-rose-500 border border-rose-500/20 hover:bg-rose-500/20'}`}
                        >
                          {w.status === 'frozen' ? (
                            <><Unlock className="h-3 w-3" /> Unfreeze</>
                          ) : (
                            <><Lock className="h-3 w-3" /> Freeze</>
                          )}
                        </button>
                      </div>
                    ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WalletPage;
