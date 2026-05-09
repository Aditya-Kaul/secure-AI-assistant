/**
 * All backend calls in one place.
 * Components never import axios directly.
 */
import axios from 'axios';

const BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: BASE, timeout: 60000 });

export const sendChat    = (message, conversation_history = []) =>
  api.post('/chat', { message, conversation_history }).then(r => r.data);

export const getAnalytics = () =>
  api.get('/analytics').then(r => r.data);

export const getHistory   = (limit = 20) =>
  api.get('/history', { params: { limit } }).then(r => r.data);

export const runIngest    = () =>
  api.post('/ingest').then(r => r.data);

export const querySQL     = (sql_query) =>
  api.post('/query/sql', { sql_query }).then(r => r.data);

export const searchDocs   = (query, top_k = 3) =>
  api.post('/query/docs', { query, top_k }).then(r => r.data);