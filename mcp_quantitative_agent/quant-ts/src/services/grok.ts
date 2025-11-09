/**
 * Grok sentiment analysis integration
 */

import axios from 'axios';
import type { SentimentAnalysisResult } from '../types.js';

const DEFAULT_MODEL = process.env.GROK_MODEL ?? 'grok-2-latest';
const API_BASE = process.env.X_API_BASE ?? 'https://api.x.ai/v1/chat/completions';

const SYSTEM_PROMPT = `You are a sentiment analysis expert with access to X (Twitter) data.
Your job is to analyze what people are saying on X about specific topics related to prediction markets.

When given a market topic, you should search X for relevant posts and discussions, then respond ONLY with a JSON object in this exact format:
{
  "sentiment_score": <number 0-100>,
  "sentiment_label": "<positive/negative/neutral>",
  "key_themes": ["theme1", "theme2", "theme3"],
  "notable_trends": ["trend1", "trend2"],
  "market_impact": "<brief analysis of how sentiment affects market>",
  "confidence": "<high/medium/low>"
}

Do not include any text outside the JSON object.`;

export async function analyzeSentimentWithGrok(marketTitle: string, marketTicker?: string): Promise<SentimentAnalysisResult> {
  const apiKey = process.env.X_API_KEY;

  if (!apiKey) {
    return {
      status: 'error',
      error: 'missing_api_key',
      message: 'X_API_KEY environment variable is not set',
      requirements: 'Set X_API_KEY to your Grok API key to enable sentiment analysis.',
      ticker: marketTicker ?? null,
      title: marketTitle,
    };
  }

  try {
    const userPrompt = marketTicker
      ? `Search X (Twitter) for sentiment about this Kalshi prediction market:\n\nMarket: ${marketTitle}\nTicker: ${marketTicker}\n\nReturn ONLY a JSON object with sentiment analysis.`
      : `Search X (Twitter) for sentiment about this Kalshi prediction market:\n\nMarket: ${marketTitle}\n\nReturn ONLY a JSON object with sentiment analysis.`;

    const response = await axios.post(
      API_BASE,
      {
        model: DEFAULT_MODEL,
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          { role: 'user', content: userPrompt },
        ],
        temperature: 0.3,
      },
      {
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        timeout: 20000,
      },
    );

    const content: string | undefined =
      response.data?.choices?.[0]?.message?.content ??
      response.data?.output ?? // fallback if API changes structure
      undefined;

    if (!content) {
      return {
        status: 'error',
        error: 'empty_response',
        message: 'Grok API returned no content',
        ticker: marketTicker ?? null,
        title: marketTitle,
      };
    }

    try {
      const parsed = JSON.parse(content);
      return {
        status: 'success',
        ...parsed,
        ticker: marketTicker ?? null,
        title: marketTitle,
      };
    } catch (parseError) {
      return {
        status: 'error',
        error: 'invalid_json',
        message: 'Grok response was not valid JSON',
        raw_response: content,
        ticker: marketTicker ?? null,
        title: marketTitle,
      };
    }
  } catch (error: any) {
    return {
      status: 'error',
      error: error?.response?.data?.error ?? error?.message ?? 'unknown_error',
      message: 'Error calling Grok API',
      ticker: marketTicker ?? null,
      title: marketTitle,
    };
  }
}
