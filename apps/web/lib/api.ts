// Ensure API_URL has protocol
const getApiUrl = () => {
  const url = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  // Add https:// if no protocol is specified
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    return `https://${url}`;
  }
  return url;
};

const API_URL = getApiUrl();

export class APIClient {
  private baseUrl: string;
  private getToken: () => Promise<string | null>;

  constructor(getToken: () => Promise<string | null>) {
    this.baseUrl = `${API_URL}/api/v1`;
    this.getToken = getToken;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    // Get Clerk session token
    const token = await this.getToken();

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    // Add Authorization header if token exists
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          detail: `API Error: ${response.status} ${response.statusText}`
        }));

        // Handle validation errors (array of error objects)
        if (Array.isArray(error.detail)) {
          const errors = error.detail.map((err: any) =>
            `${err.loc?.join('.') || 'Field'}: ${err.msg}`
          ).join(', ');
          throw new Error(errors);
        }

        throw new Error(error.detail || `API Error: ${response.status}`);
      }

      return response.json();
    } catch (err: any) {
      // Log the actual error for debugging
      console.error('API Request Error:', {
        url,
        error: err,
        message: err.message,
        type: err.name,
      });

      // If it's a network error (can't reach server)
      if (err.message && (err.message.includes('fetch') || err.message.includes('Failed to fetch'))) {
        throw new Error(`Cannot connect to backend at ${this.baseUrl}. Error: ${err.message}`);
      }
      throw err;
    }
  }

  // Users
  async syncUser(userData: any): Promise<any> {
    return this.request('/users/sync', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getCurrentUser(): Promise<any> {
    return this.request('/users/me');
  }

  async updateUser(userData: any): Promise<any> {
    return this.request('/users/me', {
      method: 'PATCH',
      body: JSON.stringify(userData),
    });
  }

  async getUserStats(): Promise<any> {
    return this.request('/users/me/stats');
  }

  // Campaigns
  async createCampaign(campaignData: any): Promise<{ id: string; [key: string]: any }> {
    // Transform camelCase to snake_case for backend
    const transformedData = {
      title: campaignData.title,
      description: campaignData.description,
      content_type: campaignData.contentType,
      content_text: campaignData.contentText,
      content_url: campaignData.contentUrl,
      proof_prompt: campaignData.proofPrompt,
      proof_min_length: campaignData.proofMinLength,
      proof_max_length: campaignData.proofMaxLength,
      proof_guidelines: campaignData.proofGuidelines,
      min_relevance: campaignData.minRelevance,
      min_novelty: campaignData.minNovelty,
      min_coherence: campaignData.minCoherence,
      min_combined_score: campaignData.minCombinedScore,
      bounty_amount: campaignData.bountyAmount,
      max_responses: campaignData.maxResponses,
      target_audience: campaignData.targetAudience,
      start_date: campaignData.startDate,
      end_date: campaignData.endDate,
    };

    return this.request('/campaigns', {
      method: 'POST',
      body: JSON.stringify(transformedData),
    });
  }

  async getCampaigns(): Promise<any[]> {
    return this.request('/campaigns');
  }

  async getCampaign(id: string): Promise<any> {
    return this.request(`/campaigns/${id}`);
  }

  async updateCampaign(id: string, data: any): Promise<any> {
    return this.request(`/campaigns/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async createCheckoutSession(id: string): Promise<{ checkout_url: string; session_id: string }> {
    return this.request(`/campaigns/${id}/checkout`, {
      method: 'POST',
    });
  }

  async activateCampaign(id: string): Promise<any> {
    return this.request(`/campaigns/${id}/activate`, {
      method: 'POST',
    });
  }

  async pauseCampaign(id: string): Promise<any> {
    return this.request(`/campaigns/${id}/pause`, {
      method: 'POST',
    });
  }

  async getCampaignResponses(id: string): Promise<any[]> {
    return this.request(`/campaigns/${id}/responses`);
  }

  async getCampaignAnalytics(id: string): Promise<any> {
    return this.request(`/campaigns/${id}/analytics`);
  }

  // Tasks
  async getTasks(): Promise<any[]> {
    return this.request('/tasks');
  }

  async getTask(id: string): Promise<any> {
    return this.request(`/tasks/${id}`);
  }

  async acceptTask(id: string): Promise<any> {
    return this.request(`/tasks/${id}/accept`, {
      method: 'POST',
    });
  }

  async getMyTasks(): Promise<any[]> {
    return this.request('/tasks/my/tasks');
  }

  // Proofs
  async submitProof(proofData: any): Promise<any> {
    return this.request('/proofs', {
      method: 'POST',
      body: JSON.stringify(proofData),
    });
  }

  async getProof(id: string): Promise<any> {
    return this.request(`/proofs/${id}`);
  }

  async getMyProofs(): Promise<any[]> {
    return this.request('/proofs/my/proofs');
  }

  // Payments
  async getMyPayments(): Promise<any[]> {
    return this.request('/payments/my');
  }

  async getBalance(): Promise<any> {
    return this.request('/payments/balance');
  }

  async requestWithdrawal(amount: number): Promise<any> {
    return this.request(`/payments/withdraw?amount=${amount}`, {
      method: 'POST',
    });
  }

  async getStripeConnectStatus(): Promise<any> {
    return this.request('/payments/connect/status');
  }

  async createStripeConnectOnboarding(): Promise<any> {
    return this.request('/payments/connect/onboard', {
      method: 'POST',
    });
  }

  async getStripeConnectDashboard(): Promise<any> {
    return this.request('/payments/connect/dashboard', {
      method: 'POST',
    });
  }

  // Detection
  async detectText(text: string, detailed: boolean = true): Promise<{
    id: string;
    score: number;
    verdict: string;
    confidence: number;
    word_count: number;
    analysis?: any;
    can_verify: boolean;
    created_at: string;
  }> {
    return this.request('/detect', {
      method: 'POST',
      body: JSON.stringify({ text, detailed }),
    });
  }

  async getDetections(limit: number = 20, offset: number = 0): Promise<any[]> {
    return this.request(`/detections?limit=${limit}&offset=${offset}`);
  }
}
