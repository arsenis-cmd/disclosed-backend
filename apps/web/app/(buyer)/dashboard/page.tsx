'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import { APIClient } from '@/lib/api';

export default function DashboardPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { getToken } = useAuth();
  const api = new APIClient(getToken);

  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showSuccess, setShowSuccess] = useState(false);

  useEffect(() => {
    // Check for payment success
    if (searchParams.get('payment') === 'success') {
      setShowSuccess(true);
      // Clear query params after 5 seconds
      setTimeout(() => {
        setShowSuccess(false);
        router.replace('/dashboard');
      }, 5000);
    }

    loadCampaigns();
  }, []);

  const loadCampaigns = async () => {
    try {
      setLoading(true);
      const data = await api.getCampaigns();
      setCampaigns(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case 'ACTIVE':
        return 'bg-success/20 text-success border-success/30';
      case 'PENDING':
        return 'bg-warning/20 text-warning border-warning/30';
      case 'PAUSED':
        return 'bg-warning/20 text-warning border-warning/30';
      case 'COMPLETED':
        return 'bg-accent-primary/20 text-accent-primary border-accent-primary/30';
      case 'DRAFT':
        return 'bg-text-tertiary/20 text-text-tertiary border-text-tertiary/30';
      default:
        return 'bg-background-tertiary text-text-secondary border-border';
    }
  };

  return (
    <div className="min-h-screen bg-background-primary relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 right-1/4 w-96 h-96 bg-accent-secondary/10 rounded-full filter blur-3xl animate-float" />
        <div className="absolute bottom-20 left-1/4 w-96 h-96 bg-accent-pink/10 rounded-full filter blur-3xl animate-float" style={{ animationDelay: '1s' }} />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 py-12">
        {/* Success Message */}
        {showSuccess && (
          <div className="mb-6 bg-success-muted border border-success/30 rounded-xl p-4 animate-fade-up">
            <div className="flex items-start gap-3">
              <svg className="w-6 h-6 text-success flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 className="font-semibold text-success-light mb-1">Payment Successful!</h3>
                <p className="text-success-light/80">Your campaign has been activated and is now live.</p>
              </div>
            </div>
          </div>
        )}

        {/* Header */}
        <div className="mb-12 animate-fade-up">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold gradient-text mb-2">Campaign Dashboard</h1>
              <p className="text-text-secondary text-lg">
                Manage your campaigns and track responses
              </p>
            </div>
            <button
              onClick={() => router.push('/campaigns/new')}
              className="btn-cyber flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Campaign
            </button>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent-primary mx-auto mb-4"></div>
            <p className="text-text-secondary">Loading campaigns...</p>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="bg-error-muted border border-error/30 rounded-xl p-4 animate-shake">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-error flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="text-error-light">{error}</div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && campaigns.length === 0 && (
          <div className="card-glass text-center py-16 animate-fade-up">
            <div className="w-20 h-20 rounded-full bg-accent-primary/20 flex items-center justify-center mx-auto mb-6">
              <svg className="w-10 h-10 text-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-text-primary mb-2">No Campaigns Yet</h2>
            <p className="text-text-secondary mb-6 max-w-md mx-auto">
              Get started by creating your first campaign to collect verified human responses.
            </p>
            <button
              onClick={() => router.push('/campaigns/new')}
              className="btn-cyber inline-flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Create Your First Campaign
            </button>
          </div>
        )}

        {/* Campaigns Grid */}
        {!loading && !error && campaigns.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {campaigns.map((campaign, index) => (
              <div
                key={campaign.id}
                className="card-glass hover:border-accent-primary/50 transition-all cursor-pointer group animate-fade-up"
                style={{ animationDelay: `${index * 50}ms` }}
                onClick={() => router.push(`/campaigns/${campaign.id}`)}
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-text-primary group-hover:text-accent-primary transition-colors mb-1">
                      {campaign.title}
                    </h3>
                    <p className="text-sm text-text-tertiary line-clamp-2">
                      {campaign.description}
                    </p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ml-2 ${getStatusColor(campaign.status)}`}>
                    {campaign.status}
                  </span>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 mb-4 pb-4 border-b border-border">
                  <div>
                    <p className="text-xs text-text-tertiary mb-1">Responses</p>
                    <p className="text-lg font-bold text-text-primary">
                      {campaign.currentResponses}/{campaign.maxResponses}
                    </p>
                    <div className="mt-1 w-full bg-background-tertiary rounded-full h-1">
                      <div
                        className="bg-accent-primary h-1 rounded-full transition-all"
                        style={{ width: `${(campaign.currentResponses / campaign.maxResponses) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-text-tertiary mb-1">Budget</p>
                    <p className="text-lg font-bold text-success">
                      ${campaign.budgetSpent.toFixed(2)}
                    </p>
                    <p className="text-xs text-text-tertiary">
                      of ${campaign.budgetTotal.toFixed(2)}
                    </p>
                  </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2 text-text-tertiary">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>${campaign.bountyAmount.toFixed(2)}/response</span>
                  </div>
                  <div className="text-accent-primary font-medium group-hover:text-accent-secondary transition-colors flex items-center gap-1">
                    View Details
                    <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
