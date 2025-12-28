'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import { APIClient } from '@/lib/api';

export default function CampaignDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { getToken } = useAuth();
  const api = new APIClient(getToken);

  const [campaign, setCampaign] = useState<any>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [responses, setResponses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'overview' | 'responses' | 'analytics'>('overview');

  useEffect(() => {
    loadCampaignData();
  }, [params.id]);

  const loadCampaignData = async () => {
    try {
      setLoading(true);
      const [campaignData, analyticsData, responsesData] = await Promise.all([
        api.getCampaign(params.id as string),
        api.getCampaignAnalytics(params.id as string).catch(() => null),
        api.getCampaignResponses(params.id as string).catch(() => []),
      ]);

      setCampaign(campaignData);
      setAnalytics(analyticsData);
      setResponses(responsesData);
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

  if (loading) {
    return (
      <div className="min-h-screen bg-background-primary flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent-primary mx-auto mb-4"></div>
          <p className="text-text-secondary">Loading campaign...</p>
        </div>
      </div>
    );
  }

  if (error || !campaign) {
    return (
      <div className="min-h-screen bg-background-primary flex items-center justify-center">
        <div className="card-glass max-w-md text-center">
          <div className="w-16 h-16 rounded-full bg-error/20 flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-text-primary mb-2">Campaign Not Found</h2>
          <p className="text-text-secondary mb-6">{error || 'This campaign does not exist or you do not have access to it.'}</p>
          <button onClick={() => router.push('/dashboard')} className="btn-secondary">
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background-primary relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 right-1/4 w-96 h-96 bg-accent-secondary/10 rounded-full filter blur-3xl animate-float" />
        <div className="absolute bottom-20 left-1/4 w-96 h-96 bg-accent-pink/10 rounded-full filter blur-3xl animate-float" style={{ animationDelay: '1s' }} />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-8 animate-fade-up">
          <button onClick={() => router.push('/dashboard')} className="text-accent-primary hover:text-accent-secondary mb-4 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Dashboard
          </button>

          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold text-text-primary">{campaign.title}</h1>
                <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(campaign.status)}`}>
                  {campaign.status}
                </span>
              </div>
              <p className="text-text-secondary">{campaign.description}</p>
            </div>

            <div className="flex gap-2">
              {campaign.status === 'ACTIVE' && (
                <button className="btn-secondary">
                  Pause Campaign
                </button>
              )}
              {campaign.status === 'PAUSED' && (
                <button className="btn-cyber">
                  Resume Campaign
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-border">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'overview'
                ? 'border-accent-primary text-accent-primary'
                : 'border-transparent text-text-secondary hover:text-text-primary'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('responses')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'responses'
                ? 'border-accent-primary text-accent-primary'
                : 'border-transparent text-text-secondary hover:text-text-primary'
            }`}
          >
            Responses ({responses.length})
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'analytics'
                ? 'border-accent-primary text-accent-primary'
                : 'border-transparent text-text-secondary hover:text-text-primary'
            }`}
          >
            Analytics
          </button>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="card-glass">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-accent-primary/20 flex items-center justify-center">
                    <svg className="w-5 h-5 text-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm text-text-tertiary">Total Responses</p>
                    <p className="text-2xl font-bold text-text-primary">{campaign.currentResponses}/{campaign.maxResponses}</p>
                  </div>
                </div>
              </div>

              <div className="card-glass">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-success/20 flex items-center justify-center">
                    <svg className="w-5 h-5 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm text-text-tertiary">Budget Spent</p>
                    <p className="text-2xl font-bold text-text-primary">${campaign.budgetSpent.toFixed(2)}</p>
                  </div>
                </div>
              </div>

              <div className="card-glass">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-accent-cyan/20 flex items-center justify-center">
                    <svg className="w-5 h-5 text-accent-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm text-text-tertiary">Budget Remaining</p>
                    <p className="text-2xl font-bold text-text-primary">${(campaign.budgetTotal - campaign.budgetSpent).toFixed(2)}</p>
                  </div>
                </div>
              </div>

              <div className="card-glass">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-accent-pink/20 flex items-center justify-center">
                    <svg className="w-5 h-5 text-accent-pink" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm text-text-tertiary">Bounty/Response</p>
                    <p className="text-2xl font-bold text-text-primary">${campaign.bountyAmount.toFixed(2)}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="card-glass">
              <h2 className="text-xl font-semibold text-text-primary mb-4">Content to Review</h2>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-text-tertiary mb-1">Type</p>
                  <p className="text-text-primary capitalize">{campaign.contentType}</p>
                </div>
                {campaign.contentText && (
                  <div>
                    <p className="text-sm text-text-tertiary mb-1">Content</p>
                    <div className="bg-background-tertiary/50 rounded-lg p-4 border border-border">
                      <p className="text-text-primary whitespace-pre-wrap">{campaign.contentText}</p>
                    </div>
                  </div>
                )}
                {campaign.contentUrl && (
                  <div>
                    <p className="text-sm text-text-tertiary mb-1">URL</p>
                    <a href={campaign.contentUrl} target="_blank" rel="noopener noreferrer" className="text-accent-primary hover:text-accent-secondary">
                      {campaign.contentUrl}
                    </a>
                  </div>
                )}
              </div>
            </div>

            {/* Response Requirements */}
            <div className="card-glass">
              <h2 className="text-xl font-semibold text-text-primary mb-4">Response Requirements</h2>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-text-tertiary mb-1">Prompt</p>
                  <p className="text-text-primary">{campaign.proofPrompt}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-text-tertiary mb-1">Min Length</p>
                    <p className="text-text-primary">{campaign.proofMinLength} characters</p>
                  </div>
                  <div>
                    <p className="text-sm text-text-tertiary mb-1">Max Length</p>
                    <p className="text-text-primary">{campaign.proofMaxLength} characters</p>
                  </div>
                </div>
                {campaign.proofGuidelines && (
                  <div>
                    <p className="text-sm text-text-tertiary mb-1">Guidelines</p>
                    <p className="text-text-primary">{campaign.proofGuidelines}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Verification Thresholds */}
            <div className="card-glass">
              <h2 className="text-xl font-semibold text-text-primary mb-4">Verification Thresholds</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-background-tertiary/50 rounded-lg p-4 border border-border">
                  <p className="text-sm text-text-tertiary mb-2">Relevance</p>
                  <p className="text-2xl font-bold text-accent-primary mb-2">{(campaign.minRelevance * 100).toFixed(0)}%</p>
                  <div className="flex gap-1">
                    {[...Array(20)].map((_, i) => (
                      <div
                        key={i}
                        className={`h-1 flex-1 rounded-full ${
                          i < campaign.minRelevance * 20 ? 'bg-accent-primary' : 'bg-background-hover'
                        }`}
                      />
                    ))}
                  </div>
                </div>

                <div className="bg-background-tertiary/50 rounded-lg p-4 border border-border">
                  <p className="text-sm text-text-tertiary mb-2">Novelty</p>
                  <p className="text-2xl font-bold text-accent-cyan mb-2">{(campaign.minNovelty * 100).toFixed(0)}%</p>
                  <div className="flex gap-1">
                    {[...Array(20)].map((_, i) => (
                      <div
                        key={i}
                        className={`h-1 flex-1 rounded-full ${
                          i < campaign.minNovelty * 20 ? 'bg-accent-cyan' : 'bg-background-hover'
                        }`}
                      />
                    ))}
                  </div>
                </div>

                <div className="bg-background-tertiary/50 rounded-lg p-4 border border-border">
                  <p className="text-sm text-text-tertiary mb-2">Coherence</p>
                  <p className="text-2xl font-bold text-accent-secondary mb-2">{(campaign.minCoherence * 100).toFixed(0)}%</p>
                  <div className="flex gap-1">
                    {[...Array(20)].map((_, i) => (
                      <div
                        key={i}
                        className={`h-1 flex-1 rounded-full ${
                          i < campaign.minCoherence * 20 ? 'bg-accent-secondary' : 'bg-background-hover'
                        }`}
                      />
                    ))}
                  </div>
                </div>

                <div className="bg-background-tertiary/50 rounded-lg p-4 border border-border">
                  <p className="text-sm text-text-tertiary mb-2">Combined Score</p>
                  <p className="text-2xl font-bold text-accent-pink mb-2">{(campaign.minCombinedScore * 100).toFixed(0)}%</p>
                  <div className="flex gap-1">
                    {[...Array(20)].map((_, i) => (
                      <div
                        key={i}
                        className={`h-1 flex-1 rounded-full ${
                          i < campaign.minCombinedScore * 20 ? 'bg-accent-pink' : 'bg-background-hover'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Responses Tab */}
        {activeTab === 'responses' && (
          <div className="space-y-4">
            {responses.length === 0 ? (
              <div className="card-glass text-center py-12">
                <div className="w-16 h-16 rounded-full bg-accent-primary/20 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-text-primary mb-2">No Responses Yet</h3>
                <p className="text-text-secondary">Responses will appear here once people start submitting them.</p>
              </div>
            ) : (
              responses.map((response) => (
                <div key={response.id} className="card-glass">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <p className="text-sm text-text-tertiary">Response ID: {response.id}</p>
                      <p className="text-sm text-text-tertiary">Submitted: {new Date(response.createdAt).toLocaleDateString()}</p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${
                      response.status === 'VERIFIED' ? 'bg-success/20 text-success border-success/30' :
                      response.status === 'REJECTED' ? 'bg-error/20 text-error border-error/30' :
                      'bg-warning/20 text-warning border-warning/30'
                    }`}>
                      {response.status}
                    </span>
                  </div>
                  <p className="text-text-primary mb-4">{response.text}</p>
                  {response.scores && (
                    <div className="grid grid-cols-4 gap-2 pt-4 border-t border-border">
                      <div>
                        <p className="text-xs text-text-tertiary">Relevance</p>
                        <p className="text-sm font-semibold text-accent-primary">{(response.scores.relevance * 100).toFixed(0)}%</p>
                      </div>
                      <div>
                        <p className="text-xs text-text-tertiary">Novelty</p>
                        <p className="text-sm font-semibold text-accent-cyan">{(response.scores.novelty * 100).toFixed(0)}%</p>
                      </div>
                      <div>
                        <p className="text-xs text-text-tertiary">Coherence</p>
                        <p className="text-sm font-semibold text-accent-secondary">{(response.scores.coherence * 100).toFixed(0)}%</p>
                      </div>
                      <div>
                        <p className="text-xs text-text-tertiary">Combined</p>
                        <p className="text-sm font-semibold text-accent-pink">{(response.scores.combined * 100).toFixed(0)}%</p>
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            {analytics ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="card-glass">
                    <h3 className="text-sm text-text-tertiary mb-2">Total Responses</h3>
                    <p className="text-3xl font-bold text-text-primary">{analytics.totalResponses}</p>
                  </div>
                  <div className="card-glass">
                    <h3 className="text-sm text-text-tertiary mb-2">Verified</h3>
                    <p className="text-3xl font-bold text-success">{analytics.verifiedResponses}</p>
                  </div>
                  <div className="card-glass">
                    <h3 className="text-sm text-text-tertiary mb-2">Rejected</h3>
                    <p className="text-3xl font-bold text-error">{analytics.rejectedResponses}</p>
                  </div>
                </div>

                <div className="card-glass">
                  <h2 className="text-xl font-semibold text-text-primary mb-4">Average Scores</h2>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-text-secondary">Relevance</span>
                        <span className="text-accent-primary font-semibold">{(analytics.averageRelevanceScore * 100).toFixed(0)}%</span>
                      </div>
                      <div className="w-full bg-background-tertiary rounded-full h-2">
                        <div className="bg-accent-primary h-2 rounded-full" style={{ width: `${analytics.averageRelevanceScore * 100}%` }}></div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-text-secondary">Novelty</span>
                        <span className="text-accent-cyan font-semibold">{(analytics.averageNoveltyScore * 100).toFixed(0)}%</span>
                      </div>
                      <div className="w-full bg-background-tertiary rounded-full h-2">
                        <div className="bg-accent-cyan h-2 rounded-full" style={{ width: `${analytics.averageNoveltyScore * 100}%` }}></div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-text-secondary">Coherence</span>
                        <span className="text-accent-secondary font-semibold">{(analytics.averageCoherenceScore * 100).toFixed(0)}%</span>
                      </div>
                      <div className="w-full bg-background-tertiary rounded-full h-2">
                        <div className="bg-accent-secondary h-2 rounded-full" style={{ width: `${analytics.averageCoherenceScore * 100}%` }}></div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-text-secondary">Combined</span>
                        <span className="text-accent-pink font-semibold">{(analytics.averageCombinedScore * 100).toFixed(0)}%</span>
                      </div>
                      <div className="w-full bg-background-tertiary rounded-full h-2">
                        <div className="bg-accent-pink h-2 rounded-full" style={{ width: `${analytics.averageCombinedScore * 100}%` }}></div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="card-glass">
                  <h2 className="text-xl font-semibold text-text-primary mb-4">Budget</h2>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-text-tertiary mb-1">Spent</p>
                      <p className="text-2xl font-bold text-success">${analytics.budgetSpent.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-text-tertiary mb-1">Remaining</p>
                      <p className="text-2xl font-bold text-accent-primary">${analytics.budgetRemaining.toFixed(2)}</p>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="card-glass text-center py-12">
                <p className="text-text-secondary">No analytics data available yet.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
