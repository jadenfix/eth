/** HTTP client for the local graph gateway. No provider credentials or funded calls. */
export class OnchainClient {
  constructor(baseURL = 'http://127.0.0.1:8080', {token} = {}) {
    this.baseURL = baseURL.replace(/\/$/, '');
    this.token = token;
  }
  async request(path, options = {}) {
    const response = await fetch(this.baseURL + path, {
      ...options,
      headers: {'Content-Type': 'application/json', ...(this.token ? {Authorization: `Bearer ${this.token}`} : {}), ...options.headers},
      signal: options.signal || AbortSignal.timeout(10000),
    });
    const data = await response.json();
    if (!response.ok) {
      const error = new Error(data.error || `HTTP ${response.status}`);
      error.status = response.status;
      throw error;
    }
    return data;
  }
  createEntity(entity) { return this.request('/v1/entities', {method: 'POST', body: JSON.stringify(entity)}); }
  searchEntities(query = '') { return this.request(`/v1/entities/search?query=${encodeURIComponent(query)}`); }
  createRelationship(relationship) { return this.request('/v1/relationships', {method: 'POST', body: JSON.stringify(relationship)}); }
  getNetwork(id, depth = 2) { return this.request(`/v1/entities/${encodeURIComponent(id)}/network?depth=${depth}`); }
  getHealth() { return this.request('/v1/health'); }
  submitFeedback(feedback) { return this.request('/v1/feedback', {method: 'POST', body: JSON.stringify(feedback)}); }
}
