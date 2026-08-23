const API_BASE = '/api';

class ApiClient {
  private token: string = '';

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('applyiq_token', token);
    }
  }

  getToken(): string {
    if (!this.token && typeof window !== 'undefined') {
      this.token = localStorage.getItem('applyiq_token') || '';
    }
    return this.token;
  }

  clearToken() {
    this.token = '';
    if (typeof window !== 'undefined') {
      localStorage.removeItem('applyiq_token');
    }
  }

  private async request(method: string, path: string, data?: any, isFile?: boolean): Promise<any> {
    const headers: Record<string, string> = {};
    const token = this.getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (!isFile) headers['Content-Type'] = 'application/json';

    const res = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: isFile ? data : data ? JSON.stringify(data) : undefined,
    });

    const json = await res.json().catch(() => ({ ok: false, error: { message: res.statusText } }));

    if (!res.ok) {
      if (res.status === 401) {
        this.clearToken();
        if (typeof window !== 'undefined') window.location.href = '/login';
      }
      throw new Error(json.detail || json.error?.message || 'Request failed');
    }
    return json;
  }

  get(path: string) { return this.request('GET', path); }
  post(path: string, data?: any) { return this.request('POST', path, data); }
  put(path: string, data?: any) { return this.request('PUT', path, data); }
  patch(path: string, data?: any) { return this.request('PATCH', path, data); }
  del(path: string) { return this.request('DELETE', path); }

  async upload(path: string, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.request('POST', path, formData, true);
  }

  // Auth
  async signup(name: string, email: string, password: string) {
    const res = await this.post('/auth/signup', { name, email, password });
    if (res.data?.access_token) this.setToken(res.data.access_token);
    return res;
  }
  async login(email: string, password: string) {
    const res = await this.post('/auth/login', { email, password });
    if (res.data?.access_token) this.setToken(res.data.access_token);
    return res;
  }
  async me() { return this.get('/auth/me'); }
  logout() { this.clearToken(); }

  // Profile
  getProfile() { return this.get('/profile'); }
  updateProfile(data: any) { return this.put('/profile', data); }

  // Resumes
  listResumes() { return this.get('/resumes'); }
  uploadResume(file: File) { return this.upload('/resumes/upload', file); }
  deleteResume(id: string) { return this.del(`/resumes/${id}`); }
  setDefaultResume(id: string) { return this.post(`/resumes/${id}/default`); }

  // Resume Versions
  listVersions() { return this.get('/resume-versions'); }

  // Job Searches
  listSearches() { return this.get('/job-searches'); }
  createSearch(data: any) { return this.post('/job-searches', data); }
  getSearch(id: string) { return this.get(`/job-searches/${id}`); }
  updateSearch(id: string, data: any) { return this.put(`/job-searches/${id}`, data); }
  deleteSearch(id: string) { return this.del(`/job-searches/${id}`); }
  duplicateSearch(id: string) { return this.post(`/job-searches/${id}/duplicate`); }

  // Applications
  listApplications(params?: string) { return this.get(`/applications${params ? '?' + params : ''}`); }
  getApplication(id: string) { return this.get(`/applications/${id}`); }
  updateAppStatus(id: string, status: string) { return this.patch(`/applications/${id}/status?status=${status}`); }
  approveApp(id: string, approved: boolean) { return this.post(`/applications/${id}/approve`, { approved }); }

  // Jobs
  listJobs(params?: string) { return this.get(`/jobs${params ? '?' + params : ''}`); }
  getJob(id: string) { return this.get(`/jobs/${id}`); }
  saveJob(id: string) { return this.post(`/jobs/${id}/save`); }

  // Dashboard
  getDashboard() { return this.get('/dashboard/stats'); }

  // Analytics
  getAnalytics() { return this.get('/analytics'); }

  // Automation
  startAutomation(searchId: string) { return this.post('/automation/start', { searchId }); }
  stopAutomation(runId: string) { return this.post(`/automation/stop/${runId}`); }
  pauseAutomation(runId: string) { return this.post(`/automation/pause/${runId}`); }
  resumeAutomation(runId: string) { return this.post(`/automation/resume/${runId}`); }
  getAutomationStatus() { return this.get('/automation/status'); }
  listRuns() { return this.get('/automation/runs'); }
  getLogs(runId: string) { return this.get(`/automation/logs/${runId}`); }

  // Notifications
  listNotifications() { return this.get('/notifications'); }
  markRead(id: string) { return this.post(`/notifications/${id}/read`); }
  markAllRead() { return this.post('/notifications/read-all'); }

  // Settings
  getSettings() { return this.get('/settings'); }
  updateSettings(data: any) { return this.put('/settings', data); }

  // AI
  evaluateJob(data: any) { return this.post('/ai/evaluate', data); }
  customizeResume(data: any) { return this.post('/ai/customize-resume', data); }
  generateMessage(data: any) { return this.post('/ai/generate-message', data); }
}

export const api = new ApiClient();
export default api;
