/** Fetch data only after HTTP success; malformed provider results are explicit errors. */
export async function requestJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`Gateway returned HTTP ${response.status}`);
  return response.status === 204 ? null : response.json();
}
export function readSignals(payload) {
  if (!Array.isArray(payload)) throw new Error('Gateway signals response must be an array');
  for (const signal of payload) {
    if (!signal || typeof signal.signal_id !== 'string' || !signal.signal_id ||
        typeof signal.description !== 'string' || typeof signal.agent_name !== 'string' ||
        typeof signal.signal_type !== 'string' || typeof signal.timestamp !== 'string' ||
        !Number.isFinite(Date.parse(signal.timestamp)) ||
        !Number.isFinite(signal.confidence_score) || signal.confidence_score < 0 || signal.confidence_score > 1 ||
        !['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].includes(signal.severity)) {
      throw new Error('Gateway returned an invalid signal');
    }
  }
  return payload;
}
export function severityColor(severity) {
  return ({CRITICAL:'red',HIGH:'orange',MEDIUM:'yellow',LOW:'green'})[severity] || 'gray';
}

export function readHealth(payload) {
  if (!payload || !['ingestion_rate','processing_latency','active_agents','signal_accuracy'].every(key => Number.isFinite(payload[key]) && payload[key] >= 0) || payload.signal_accuracy > 1) {
    throw new Error('Gateway returned invalid system health');
  }
  return payload;
}
