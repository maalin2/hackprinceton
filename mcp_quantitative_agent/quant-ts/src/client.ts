/**
 * External API client for Kalshi markets
 */

import axios, { AxiosInstance } from 'axios';
import { config } from './config.js';
import type { KalshiMarket } from './types.js';

export class KalshiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: config.kalshiBaseUrl,
      timeout: config.requestTimeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Fetch markets by series ticker
   */
  async getMarketsBySeries(seriesTicker: string, status: string = 'open'): Promise<KalshiMarket[]> {
    try {
      const response = await this.client.get('/markets', {
        params: {
          series_ticker: seriesTicker,
          status,
          limit: 200,
        },
      });
      return response.data.markets || [];
    } catch (error) {
      console.error(`Error fetching markets for series ${seriesTicker}:`, error);
      return [];
    }
  }

  /**
   * Fetch all series
   */
  async getSeries(limit: number = 200): Promise<any[]> {
    try {
      const response = await this.client.get('/series', {
        params: { limit },
      });
      return response.data.series || [];
    } catch (error) {
      console.error('Error fetching series:', error);
      return [];
    }
  }

  /**
   * Fetch single market by ticker
   */
  async getMarket(ticker: string): Promise<KalshiMarket | null> {
    try {
      const response = await this.client.get(`/markets/${ticker}`);
      return response.data.market || null;
    } catch (error) {
      console.error(`Error fetching market ${ticker}:`, error);
      return null;
    }
  }

  /**
   * Fetch market trades history
   */
  async getMarketTrades(ticker: string, limit: number = 100): Promise<any[]> {
    try {
      const response = await this.client.get(`/markets/${ticker}/trades`, {
        params: { limit },
      });
      return response.data.trades || [];
    } catch (error) {
      console.error(`Error fetching trades for ${ticker}:`, error);
      return [];
    }
  }

  /**
   * Calculate implied probability from market prices
   */
  impliedProb(yesBid?: number, yesAsk?: number, lastPrice?: number): number | null {
    if (yesBid !== undefined && yesAsk !== undefined && yesAsk > 0) {
      return ((yesBid + yesAsk) / 2) / 100.0;
    }
    if (lastPrice !== undefined) {
      return lastPrice / 100.0;
    }
    return null;
  }

  /**
   * Calculate confidence from bid-ask spread
   */
  spreadConfidence(yesBid?: number, yesAsk?: number): number {
    if (yesBid === undefined || yesAsk === undefined) {
      return 0.0;
    }
    const spread = yesAsk - yesBid;
    return Math.max(0.0, 1.0 - (spread / 100.0));
  }
}

export const kalshiClient = new KalshiClient();
