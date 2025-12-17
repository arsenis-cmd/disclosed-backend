'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import { APIClient } from '@/lib/api';
import { formatCurrency, formatDateTime } from '@/lib/utils';

export default function EarningsPage() {
  const router = useRouter();
  const { userId } = useAuth();
  const api = new APIClient(() => userId);

  const [balance, setBalance] = useState<any>(null);
  const [payments, setPayments] = useState<any[]>([]);
  const [stripeStatus, setStripeStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (userId) {
      loadData();
    }
  }, [userId]);

  const loadData = async () => {
    try {
      const [balanceData, paymentsData, statusData] = await Promise.all([
        api.getBalance(),
        api.getMyPayments(),
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/payments/connect/status?clerk_id=${userId}`)
          .then(res => res.json())
      ]);

      setBalance(balanceData);
      setPayments(paymentsData);
      setStripeStatus(statusData);
    } catch (error) {
      console.error('Failed to load earnings data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSetupPayouts = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/payments/connect/onboard?clerk_id=${userId}`,
        { method: 'POST' }
      );
      const data = await response.json();

      if (data.url) {
        window.location.href = data.url;
      }
    } catch (error: any) {
      alert(`Failed to start setup: ${error.message}`);
    }
  };

  const handleViewDashboard = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/payments/connect/dashboard?clerk_id=${userId}`,
        { method: 'POST' }
      );
      const data = await response.json();

      if (data.url) {
        window.open(data.url, '_blank');
      }
    } catch (error: any) {
      alert(`Failed to load dashboard: ${error.message}`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Earnings</h1>
          <p className="text-gray-600">Track your payments and manage payouts</p>
        </div>

        {/* Stripe Connect Status */}
        {!stripeStatus?.connected || !stripeStatus?.payouts_enabled ? (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
            <div className="flex items-start gap-4">
              <svg className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div className="flex-1">
                <h3 className="font-semibold text-yellow-900 mb-2">
                  Set up payouts to receive your earnings
                </h3>
                <p className="text-sm text-yellow-700 mb-4">
                  Connect your Stripe account to receive payments directly to your bank account.
                </p>
                <button
                  onClick={handleSetupPayouts}
                  className="bg-yellow-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-yellow-700 transition"
                >
                  Connect with Stripe
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-green-800 font-medium">Stripe account connected</span>
            </div>
            <button
              onClick={handleViewDashboard}
              className="text-green-700 hover:text-green-800 font-medium text-sm"
            >
              View Dashboard →
            </button>
          </div>
        )}

        {/* Balance Cards */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="text-sm text-gray-500 mb-1">Total Earned</div>
            <div className="text-3xl font-bold text-gray-900">
              {formatCurrency(balance?.total || 0)}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="text-sm text-gray-500 mb-1">Pending</div>
            <div className="text-3xl font-bold text-yellow-600">
              {formatCurrency(balance?.pending || 0)}
            </div>
            <div className="text-xs text-gray-500 mt-1">Not yet paid out</div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="text-sm text-gray-500 mb-1">Paid Out</div>
            <div className="text-3xl font-bold text-green-600">
              {formatCurrency(balance?.available || 0)}
            </div>
            <div className="text-xs text-gray-500 mt-1">Sent to your account</div>
          </div>
        </div>

        {/* Payment History */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">Payment History</h2>
          </div>

          <div className="divide-y">
            {payments.length === 0 ? (
              <div className="p-12 text-center text-gray-500">
                No payments yet. Complete tasks to start earning!
              </div>
            ) : (
              payments.map((payment) => (
                <div key={payment.id} className="p-6 hover:bg-gray-50 transition">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{payment.campaign_title}</h3>
                      <p className="text-sm text-gray-600 mt-1 line-clamp-1">
                        {payment.response_text}
                      </p>
                      <div className="flex gap-4 mt-2 text-xs text-gray-500">
                        <span>{formatDateTime(payment.created_at)}</span>
                        <span className="flex items-center gap-1">
                          <span className={`inline-block w-2 h-2 rounded-full ${
                            payment.status === 'COMPLETED' ? 'bg-green-500' :
                            payment.status === 'PENDING' ? 'bg-yellow-500' :
                            'bg-gray-400'
                          }`}></span>
                          {payment.status}
                        </span>
                      </div>
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-xl font-bold text-green-600">
                        {formatCurrency(payment.net_amount)}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {formatCurrency(payment.gross_amount)} gross
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
          <h3 className="font-semibold text-blue-900 mb-2">About Payments</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Payments are processed automatically when your response is verified</li>
            <li>• Platform fee: 7% + Stripe fee: 0.25%</li>
            <li>• Payouts are sent to your Stripe account within 1-2 business days</li>
            <li>• You can view full payout history in your Stripe Dashboard</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
