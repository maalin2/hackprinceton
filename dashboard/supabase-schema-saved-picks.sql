-- Create saved_picks table to store user's saved trading picks
-- Run this in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS saved_picks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  ticker TEXT NOT NULL,
  market_question TEXT,
  decision TEXT NOT NULL CHECK (decision IN ('BUY', 'SHORT', 'PASS')),
  technical_direction TEXT CHECK (technical_direction IN ('buy', 'short') OR technical_direction IS NULL),
  market_p NUMERIC NOT NULL CHECK (market_p >= 0 AND market_p <= 1),
  volatility_confidence NUMERIC NOT NULL CHECK (volatility_confidence >= 0 AND volatility_confidence <= 1),
  volume_confidence NUMERIC NOT NULL CHECK (volume_confidence >= 0 AND volume_confidence <= 1),
  momentum TEXT NOT NULL CHECK (momentum IN ('bullish', 'bearish', 'neutral')),
  final_confidence NUMERIC NOT NULL CHECK (final_confidence >= 0 AND final_confidence <= 1),
  reasoning TEXT NOT NULL,
  sentiment_label TEXT NOT NULL CHECK (sentiment_label IN ('positive', 'negative', 'neutral')),
  sentiment_score INTEGER NOT NULL CHECK (sentiment_score >= 0 AND sentiment_score <= 100),
  sentiment_confidence TEXT NOT NULL CHECK (sentiment_confidence IN ('high', 'medium', 'low')),
  key_themes TEXT[] DEFAULT '{}',
  market_impact TEXT,
  saved_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, ticker, saved_at) -- Prevent duplicate saves of same pick
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_saved_picks_user_id ON saved_picks(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_picks_saved_at ON saved_picks(saved_at DESC);

-- Enable Row Level Security
ALTER TABLE saved_picks ENABLE ROW LEVEL SECURITY;

-- Create policy to allow users to read their own saved picks
CREATE POLICY "Users can view own saved picks"
  ON saved_picks
  FOR SELECT
  USING (auth.uid() = user_id);

-- Create policy to allow users to insert their own saved picks
CREATE POLICY "Users can insert own saved picks"
  ON saved_picks
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Create policy to allow users to delete their own saved picks
CREATE POLICY "Users can delete own saved picks"
  ON saved_picks
  FOR DELETE
  USING (auth.uid() = user_id);

