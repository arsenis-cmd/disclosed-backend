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

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
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
        throw new Error(error.detail || `API Error: ${response.status}`);
      }

      return response.json();
    } catch (err: any) {
      // If it's a network error (can't reach server)
      if (err.message.includes('fetch')) {
        throw new Error(`Cannot connect to backend at ${this.baseUrl}. Please check if the backend is running.`);
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
    return this.request('/campaigns', {
      method: 'POST',
      body: JSON.stringify(campaignData),
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
}
