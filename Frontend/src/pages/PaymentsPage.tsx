import { useState, useEffect } from 'react';
import { transactionAPI, razorpayAPI } from '@/services/api';
import MetricCard from '@/components/shared/MetricCard';
import { CreditCard, Wallet, ArrowDownRight, Smartphone } from 'lucide-react';

const PaymentsPage = () => {
const [transactions, setTransactions] = useState<any[]>([]);
const [loading, setLoading] = useState(true);
const [isProcessing, setIsProcessing] = useState(false);

const RAZORPAY_KEY = import.meta.env.VITE_RAZORPAY_KEY_ID;

const loadTransactions = async () => {
try {
const t = await transactionAPI.getAll();
setTransactions(t || []);
} catch (e) {
console.error(e);
} finally {
setLoading(false);
}
};

useEffect(() => {
loadTransactions();
}, []);

const loadRazorpayScript = () =>
new Promise((resolve) => {
const script = document.createElement('script');
script.src = 'https://checkout.razorpay.com/v1/checkout.js';
script.onload = () => resolve(true);
script.onerror = () => resolve(false);
document.body.appendChild(script);
});

const handlePayment = async () => {
try {
setIsProcessing(true);


  const loaded = await loadRazorpayScript();
  if (!loaded) throw new Error("Razorpay SDK failed");

  // ✅ FIXED API CALL
  const order = await razorpayAPI.createOrder({
    amount: 49
  });

  const options = {
    key: RAZORPAY_KEY || (order as any).key,
    amount: order.amount,
    currency: "INR",
    name: "GigSurance",
    description: "Weekly Premium",
    order_id: (order as any).order_id, // ✅ FIXED

    handler: async (response: any) => {
      await razorpayAPI.verifyPayment(response);
      alert("✅ Payment Successful");
      loadTransactions();
    },

    prefill: {
      name: "User",
      email: "user@example.com",
    },

    theme: {
      color: "#2563eb",
    },
  };

  const rzp = new (window as any).Razorpay(options);
  rzp.open();

} catch (err) {
  console.error(err);
  alert("❌ Payment failed");
} finally {
  setIsProcessing(false);
}


};

// ✅ FIXED calculation
const totalPremiums = transactions
.filter(t => t.type === 'debit')
.reduce((s, t) => s + Math.abs(t.amount), 0);

const weeklyCount = transactions.filter(t => t.type === 'debit').length;

return ( <div className="p-6 space-y-6">

  <h1 className="text-2xl font-bold">Payments</h1>

  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
    <MetricCard title="Subscription Status" value="Active" icon={CreditCard} />
    <MetricCard title="Total Premiums Paid" value={`₹${totalPremiums}`} subtitle={`${weeklyCount} weeks`} icon={Wallet} />
    <MetricCard title="Weekly Premium" value="₹49" icon={CreditCard} />
  </div>

  <div className="rounded-lg border p-6 flex justify-between items-center">
    <div>
      <p className="font-semibold">UPI Auto Deduction</p>
      <p className="text-sm text-muted-foreground">Pay weekly premium</p>
    </div>

    <button
      onClick={handlePayment}
      disabled={isProcessing}
      className="bg-blue-600 text-white px-4 py-2 rounded"
    >
      {isProcessing ? "Processing..." : "Pay ₹49"}
    </button>
  </div>

  <div>
    <h2 className="font-semibold mb-3">History</h2>

    {transactions.map(tx => (
      <div key={tx.id} className="flex justify-between border p-3 rounded mb-2">
        <span>{tx.description}</span>
        <span>₹{Math.abs(tx.amount)}</span>
      </div>
    ))}
  </div>

</div>


);
};

export default PaymentsPage;
