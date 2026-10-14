import { DashboardPayload } from '../types';

const API_BASE = '/api';

export async function fetchDashboardData(
  scenario: string = 'baseline',
  refresh: boolean = false
): Promise<DashboardPayload> {
  const url = `${API_BASE}/dashboard?scenario=${encodeURIComponent(scenario)}${
    refresh ? '&refresh=true' : ''
  }`;

  const response = await fetch(url);
  if (!response.ok) {
    const errorText = await response.text().catch(() => 'Unknown server error');
    throw new Error(`API Request failed with status ${response.status}: ${errorText}`);
  }

  const data: DashboardPayload = await response.json();
  return data;
}
