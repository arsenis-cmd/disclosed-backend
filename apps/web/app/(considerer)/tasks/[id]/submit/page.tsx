'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import { APIClient } from '@/lib/api';
import { getScoreBgColor } from '@/lib/utils';

interface Task {
  id: string;
  campaign: {
    title: string;
    contentType: string;
    contentText?: string;
    contentUrl?: string;
    proofPrompt: string;
    proofMinLength: number;
    proofMaxLength: number;
    proofGuidelines?: string;
    bountyAmount: number;
  };
}

export default function SubmitProofPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const { isLoaded, isSignedIn, getToken } = useAuth();
  const api = new APIClient(getToken);
  const [task, setTask] = useState<Task | null>(null);
  const [response, setResponse] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<any>(null);

  // Track metadata for effort estimation
  const startTime = useRef(Date.now());
  const revisionCount = useRef(0);
  const lastText = useRef('');

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      fetchTask();
    }
  }, [params.id, isLoaded, isSignedIn]);

  useEffect(() => {
    // Track revisions (significant changes)
    if (response && lastText.current) {
      const diff = Math.abs(response.length - lastText.current.length);
      if (diff > 20) {
        revisionCount.current += 1;
      }
    }
    lastText.current = response;
  }, [response]);

  const fetchTask = async () => {
    try {
      const data = await api.getTask(params.id);
      setTask(data);
    } catch (error) {
      console.error('Failed to load task:', error);
    }
  };

  const handleSubmit = async () => {
    if (!task) return;

    if (response.length < task.campaign.proofMinLength) {
      setError(`Response must be at least ${task.campaign.proofMinLength} characters`);
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const res = await api.submitProof({
        taskId: task.id,
        responseText: response,
        metadata: {
          timeSpentSeconds: Math.floor((Date.now() - startTime.current) / 1000),
          revisionCount: revisionCount.current,
          startedAt: new Date(startTime.current).toISOString(),
        }
      });

      setResult(res);

    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!task) {
    return (
      <div className="flex justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (result) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="bg-white rounded-lg shadow-lg border">
          <div className="p-6 border-b">
            <h2 className="text-2xl font-bold flex items-center gap-2">
              {result.passed ? (
                <>
                  <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Proof Verified!
                </>
              ) : (
                <>
                  <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Verification Failed
                </>
              )}
            </h2>
          </div>

          <div className="p-6 space-y-6">
            {result.passed && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-lg font-semibold text-green-900">
                  You earned ${result.net_amount?.toFixed(2)}!
                </p>
              </div>
            )}

            <div className="space-y-3">
              <h3 className="font-semibold text-lg">Your Scores:</h3>
              <ScoreBar label="Relevance" score={result.relevance_score} />
              <ScoreBar label="Novelty" score={result.novelty_score} />
              <ScoreBar label="Coherence" score={result.coherence_score} />
              <ScoreBar label="Effort" score={result.effort_score} />
              <ScoreBar label="AI Detection" score={result.ai_detection_score} />
              <ScoreBar label="Combined" score={result.combined_score} highlight />
            </div>

            {result.verification_notes && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-900">{result.verification_notes}</p>
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={() => router.push('/tasks')}
                className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition"
              >
                Find More Tasks
              </button>
              <button
                onClick={() => router.push('/history')}
                className="flex-1 border border-gray-300 py-3 rounded-lg font-medium hover:bg-gray-50 transition"
              >
                View History
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      {/* Content to consider */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-4 border-b flex justify-between items-center">
          <h2 className="text-xl font-bold">{task.campaign.title}</h2>
          <div className="bg-green-100 text-green-800 px-3 py-1 rounded font-semibold">
            ${task.campaign.bountyAmount.toFixed(2)}
          </div>
        </div>
        <div className="p-6">
          {task.campaign.contentType === 'text' && (
            <div className="prose max-w-none bg-gray-50 p-4 rounded">
              {task.campaign.contentText}
            </div>
          )}
          {task.campaign.contentType === 'video' && (
            <video
              src={task.campaign.contentUrl}
              controls
              className="w-full rounded"
            />
          )}
        </div>
      </div>

      {/* Proof submission */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-4 border-b">
          <h2 className="text-xl font-bold">Your Response</h2>
        </div>
        <div className="p-6 space-y-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="font-medium text-blue-900">{task.campaign.proofPrompt}</p>
            {task.campaign.proofGuidelines && (
              <p className="text-sm text-blue-700 mt-2">{task.campaign.proofGuidelines}</p>
            )}
          </div>

          <textarea
            value={response}
            onChange={(e) => setResponse(e.target.value)}
            placeholder="Write your thoughtful response here..."
            rows={8}
            className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          />

          <div className="flex justify-between text-sm text-gray-600">
            <span>{response.length} / {task.campaign.proofMaxLength} characters</span>
            <span className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {Math.floor((Date.now() - startTime.current) / 1000 / 60)}m elapsed
            </span>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-900">
              {error}
            </div>
          )}

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm text-yellow-900">
            <strong>Tip:</strong> Specific personal details and genuine opinions score higher than generic responses.
          </div>

          <button
            onClick={handleSubmit}
            disabled={isSubmitting || response.length < task.campaign.proofMinLength}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isSubmitting ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Verifying...
              </>
            ) : (
              'Submit Response'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

function ScoreBar({ label, score, highlight = false }: { label: string; score: number; highlight?: boolean }) {
  const percentage = Math.round(score * 100);
  const colorClass = getScoreBgColor(score);

  return (
    <div className={`${highlight ? 'bg-gray-100 p-3 rounded-lg' : ''}`}>
      <div className="flex justify-between text-sm mb-1">
        <span className={highlight ? 'font-semibold' : ''}>{label}</span>
        <span className="font-medium">{percentage}%</span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className={`h-full ${colorClass} transition-all duration-500`} style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
}
