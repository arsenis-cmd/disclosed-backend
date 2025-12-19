'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import { APIClient } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';

export default function TasksPage() {
  const router = useRouter();
  const { isLoaded, isSignedIn, getToken } = useAuth();
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const api = new APIClient(getToken);

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      loadTasks();
    }
  }, [isLoaded, isSignedIn]);

  const loadTasks = async () => {
    try {
      const data = await api.getTasks();
      setTasks(data);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptTask = async (taskId: string) => {
    try {
      await api.acceptTask(taskId);
      router.push(`/tasks/${taskId}/submit`);
    } catch (error: any) {
      alert(error.message);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background-primary flex items-center justify-center">
        <div className="relative">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-accent-primary"></div>
          <div className="absolute inset-0 rounded-full bg-accent-primary/20 blur-xl animate-pulse"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background-primary relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 right-1/4 w-96 h-96 bg-accent-primary/10 rounded-full filter blur-3xl animate-float" />
        <div className="absolute bottom-20 left-1/4 w-96 h-96 bg-accent-cyan/10 rounded-full filter blur-3xl animate-float" style={{ animationDelay: '1s' }} />
      </div>

      <div className="relative max-w-6xl mx-auto px-4 py-12">
        <div className="mb-12 animate-fade-up">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <h1 className="text-4xl font-bold gradient-text">Available Tasks</h1>
          </div>
          <p className="text-text-secondary text-lg">
            Browse tasks and earn money by providing thoughtful responses
          </p>
        </div>

        {tasks.length === 0 ? (
          <div className="card-glass p-16 text-center animate-scale-in">
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-accent-primary/20 to-accent-cyan/20 flex items-center justify-center">
              <svg className="w-10 h-10 text-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <p className="text-text-primary text-xl mb-2">No tasks available at the moment</p>
            <p className="text-text-tertiary">Check back soon for new opportunities!</p>
          </div>
        ) : (
          <div className="grid gap-6">
            {tasks.map((task, index) => (
              <div
                key={task.id}
                className="card-glass hover:-translate-y-1 hover:border-accent-primary/30 transition-all duration-300 group animate-fade-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex flex-col md:flex-row justify-between gap-6 mb-6">
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold text-text-primary mb-3 group-hover:gradient-text transition-all">
                      {task.campaign?.title}
                    </h3>
                    <p className="text-text-secondary leading-relaxed">
                      {task.campaign?.description}
                    </p>
                  </div>
                  <div className="flex-shrink-0">
                    <div className="relative">
                      <div className="absolute inset-0 bg-gradient-to-br from-success to-success-light rounded-xl blur-lg opacity-50 group-hover:opacity-75 transition-opacity"></div>
                      <div className="relative bg-gradient-to-br from-success to-success-light text-white px-6 py-3 rounded-xl font-bold text-xl text-center min-w-[140px]">
                        {formatCurrency(task.campaign?.bounty_amount)}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="divider-gradient mb-6"></div>

                <div className="bg-background-secondary/50 backdrop-blur-sm border border-accent-primary/20 rounded-lg p-4 mb-6">
                  <p className="text-sm font-semibold text-accent-primary mb-2 uppercase tracking-wider">Task Prompt:</p>
                  <p className="text-text-primary leading-relaxed">{task.campaign?.proof_prompt}</p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                  <div className="bg-background-tertiary/50 rounded-lg p-3 border border-border">
                    <p className="text-xs text-text-tertiary uppercase tracking-wider mb-1">Type</p>
                    <p className="text-text-primary font-semibold capitalize">{task.campaign?.content_type}</p>
                  </div>
                  <div className="bg-background-tertiary/50 rounded-lg p-3 border border-border">
                    <p className="text-xs text-text-tertiary uppercase tracking-wider mb-1">Min Length</p>
                    <p className="text-text-primary font-semibold">{task.campaign?.proof_min_length} chars</p>
                  </div>
                  <div className="bg-background-tertiary/50 rounded-lg p-3 border border-border">
                    <p className="text-xs text-text-tertiary uppercase tracking-wider mb-1">Max Length</p>
                    <p className="text-text-primary font-semibold">{task.campaign?.proof_max_length} chars</p>
                  </div>
                </div>

                {task.campaign?.proof_guidelines && (
                  <div className="bg-warning-muted border border-warning/30 rounded-lg p-4 mb-6">
                    <div className="flex items-start gap-3">
                      <svg className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div>
                        <p className="font-semibold text-warning-light mb-1">Guidelines</p>
                        <p className="text-text-secondary text-sm">{task.campaign?.proof_guidelines}</p>
                      </div>
                    </div>
                  </div>
                )}

                <button
                  onClick={() => handleAcceptTask(task.id)}
                  className="btn-cyber w-full text-base py-4"
                >
                  Accept Task & Start →
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
