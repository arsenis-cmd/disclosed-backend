'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import { APIClient } from '@/lib/api';

export default function CreateCampaignPage() {
  const router = useRouter();
  const { getToken } = useAuth();
  const api = new APIClient(getToken);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    contentType: 'text',
    contentText: '',
    contentUrl: '',
    proofPrompt: '',
    proofMinLength: 100,
    proofMaxLength: 2000,
    proofGuidelines: '',
    minRelevance: 0.65,
    minNovelty: 0.70,
    minCoherence: 0.60,
    minCombinedScore: 0.60,
    bountyAmount: 5,
    maxResponses: 10,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      const campaign = await api.createCampaign(formData);
      router.push(`/campaigns/${campaign.id}`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const totalBudget = formData.bountyAmount * formData.maxResponses;

  return (
    <div className="min-h-screen bg-background-primary relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 right-1/4 w-96 h-96 bg-accent-secondary/10 rounded-full filter blur-3xl animate-float" />
        <div className="absolute bottom-20 left-1/4 w-96 h-96 bg-accent-pink/10 rounded-full filter blur-3xl animate-float" style={{ animationDelay: '1s' }} />
      </div>

      <div className="relative max-w-4xl mx-auto px-4 py-12">
        <div className="mb-12 animate-fade-up">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-secondary to-accent-pink flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <h1 className="text-4xl font-bold gradient-text">Create Campaign</h1>
          </div>
          <p className="text-text-secondary text-lg">
            Set up a new campaign to collect verified human responses
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Info */}
          <div className="card-glass space-y-4 animate-fade-up">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-accent-primary/20 flex items-center justify-center">
                <span className="text-accent-primary font-bold">1</span>
              </div>
              <h2 className="text-xl font-semibold text-text-primary">Basic Information</h2>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">Campaign Title</label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                required
                className="input w-full"
                placeholder="e.g., Share your thoughts on our new product"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                required
                rows={3}
                className="input w-full"
                placeholder="Describe what this campaign is about..."
              />
            </div>
          </div>

          {/* Content */}
          <div className="card-glass space-y-4 animate-fade-up" style={{ animationDelay: '100ms' }}>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-accent-cyan/20 flex items-center justify-center">
                <span className="text-accent-cyan font-bold">2</span>
              </div>
              <h2 className="text-xl font-semibold text-text-primary">Content to Review</h2>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">Content Type</label>
              <select
                name="contentType"
                value={formData.contentType}
                onChange={handleChange}
                className="input w-full"
              >
                <option value="text">Text</option>
                <option value="video">Video</option>
                <option value="image">Image</option>
                <option value="url">URL</option>
              </select>
            </div>

            {formData.contentType === 'text' ? (
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">Content Text</label>
                <textarea
                  name="contentText"
                  value={formData.contentText}
                  onChange={handleChange}
                  required={formData.contentType === 'text'}
                  rows={6}
                  className="input w-full font-mono text-sm"
                  placeholder="Enter the content you want people to consider..."
                />
              </div>
            ) : (
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">Content URL</label>
                <input
                  type="url"
                  name="contentUrl"
                  value={formData.contentUrl}
                  onChange={handleChange}
                  required={formData.contentType !== 'text'}
                  className="input w-full"
                  placeholder="https://..."
                />
              </div>
            )}
          </div>

          {/* Proof Requirements */}
          <div className="card-glass space-y-4 animate-fade-up" style={{ animationDelay: '200ms' }}>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-accent-secondary/20 flex items-center justify-center">
                <span className="text-accent-secondary font-bold">3</span>
              </div>
              <h2 className="text-xl font-semibold text-text-primary">Response Requirements</h2>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">Response Prompt</label>
              <textarea
                name="proofPrompt"
                value={formData.proofPrompt}
                onChange={handleChange}
                required
                rows={2}
                className="input w-full"
                placeholder="What should people respond to? e.g., 'What are your honest thoughts about this product?'"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">Min Length (chars)</label>
                <input
                  type="number"
                  name="proofMinLength"
                  value={formData.proofMinLength}
                  onChange={handleChange}
                  min={50}
                  className="input w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">Max Length (chars)</label>
                <input
                  type="number"
                  name="proofMaxLength"
                  value={formData.proofMaxLength}
                  onChange={handleChange}
                  max={5000}
                  className="input w-full"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">Additional Guidelines (optional)</label>
              <textarea
                name="proofGuidelines"
                value={formData.proofGuidelines}
                onChange={handleChange}
                rows={2}
                className="input w-full"
                placeholder="Any specific instructions for considerers..."
              />
            </div>
          </div>

          {/* Verification Thresholds */}
          <div className="card-glass space-y-4 animate-fade-up" style={{ animationDelay: '300ms' }}>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-accent-pink/20 flex items-center justify-center">
                <span className="text-accent-pink font-bold">4</span>
              </div>
              <h2 className="text-xl font-semibold text-text-primary">Verification Thresholds</h2>
            </div>
            <p className="text-sm text-text-tertiary">
              Set minimum scores required for responses to be accepted. Higher thresholds = stricter requirements.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-background-tertiary/50 rounded-lg p-4 border border-border">
                <label className="block text-sm font-medium text-text-secondary mb-2">Min Relevance</label>
                <input
                  type="number"
                  name="minRelevance"
                  value={formData.minRelevance}
                  onChange={handleChange}
                  min={0}
                  max={1}
                  step={0.05}
                  className="input w-full"
                />
                <div className="mt-2 flex gap-1">
                  {[...Array(20)].map((_, i) => (
                    <div
                      key={i}
                      className={`h-1 flex-1 rounded-full ${
                        i < formData.minRelevance * 20 ? 'bg-accent-primary' : 'bg-background-hover'
                      }`}
                    />
                  ))}
                </div>
              </div>

              <div className="bg-background-tertiary/50 rounded-lg p-4 border border-border">
                <label className="block text-sm font-medium text-text-secondary mb-2">Min Novelty</label>
                <input
                  type="number"
                  name="minNovelty"
                  value={formData.minNovelty}
                  onChange={handleChange}
                  min={0}
                  max={1}
                  step={0.05}
                  className="input w-full"
                />
                <div className="mt-2 flex gap-1">
                  {[...Array(20)].map((_, i) => (
                    <div
                      key={i}
                      className={`h-1 flex-1 rounded-full ${
                        i < formData.minNovelty * 20 ? 'bg-accent-cyan' : 'bg-background-hover'
                      }`}
                    />
                  ))}
                </div>
              </div>

              <div className="bg-background-tertiary/50 rounded-lg p-4 border border-border">
                <label className="block text-sm font-medium text-text-secondary mb-2">Min Coherence</label>
                <input
                  type="number"
                  name="minCoherence"
                  value={formData.minCoherence}
                  onChange={handleChange}
                  min={0}
                  max={1}
                  step={0.05}
                  className="input w-full"
                />
                <div className="mt-2 flex gap-1">
                  {[...Array(20)].map((_, i) => (
                    <div
                      key={i}
                      className={`h-1 flex-1 rounded-full ${
                        i < formData.minCoherence * 20 ? 'bg-accent-secondary' : 'bg-background-hover'
                      }`}
                    />
                  ))}
                </div>
              </div>

              <div className="bg-background-tertiary/50 rounded-lg p-4 border border-border">
                <label className="block text-sm font-medium text-text-secondary mb-2">Min Combined</label>
                <input
                  type="number"
                  name="minCombinedScore"
                  value={formData.minCombinedScore}
                  onChange={handleChange}
                  min={0}
                  max={1}
                  step={0.05}
                  className="input w-full"
                />
                <div className="mt-2 flex gap-1">
                  {[...Array(20)].map((_, i) => (
                    <div
                      key={i}
                      className={`h-1 flex-1 rounded-full ${
                        i < formData.minCombinedScore * 20 ? 'bg-accent-pink' : 'bg-background-hover'
                      }`}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Budget */}
          <div className="card-glass space-y-4 animate-fade-up" style={{ animationDelay: '400ms' }}>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-success/20 flex items-center justify-center">
                <span className="text-success font-bold">5</span>
              </div>
              <h2 className="text-xl font-semibold text-text-primary">Budget</h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">Bounty per Response ($)</label>
                <input
                  type="number"
                  name="bountyAmount"
                  value={formData.bountyAmount}
                  onChange={handleChange}
                  min={1}
                  step={0.5}
                  required
                  className="input w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">Max Responses</label>
                <input
                  type="number"
                  name="maxResponses"
                  value={formData.maxResponses}
                  onChange={handleChange}
                  min={1}
                  required
                  className="input w-full"
                />
              </div>
            </div>

            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-success/20 to-success-light/20 rounded-xl blur-xl"></div>
              <div className="relative bg-gradient-to-br from-success-muted to-success-muted border border-success/30 rounded-xl p-6">
                <div className="flex justify-between items-center">
                  <span className="font-medium text-text-primary">Total Budget:</span>
                  <span className="text-3xl font-bold gradient-text">${totalBudget.toFixed(2)}</span>
                </div>
                <p className="text-sm text-text-tertiary mt-2">
                  This is the maximum you'll spend if all {formData.maxResponses} responses pass verification.
                </p>
              </div>
            </div>
          </div>

          {error && (
            <div className="bg-error-muted border border-error/30 rounded-xl p-4 text-error-light animate-shake">
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>{error}</div>
              </div>
            </div>
          )}

          {/* Submit */}
          <div className="flex flex-col sm:flex-row gap-4 pt-4">
            <button
              type="button"
              onClick={() => router.back()}
              className="btn-secondary flex-1 py-4"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn-cyber flex-1 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                  Creating...
                </span>
              ) : (
                'Create Campaign →'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
