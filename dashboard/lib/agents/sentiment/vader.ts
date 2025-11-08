/**
 * Simplified VADER-like sentiment analyzer
 * Returns compound score between -1 (negative) and +1 (positive)
 */

const POSITIVE_WORDS = new Set([
  "good", "great", "excellent", "amazing", "awesome", "fantastic", "positive",
  "bullish", "buy", "strong", "win", "winning", "success", "up", "high",
  "best", "love", "perfect", "brilliant", "outstanding", "superb",
]);

const NEGATIVE_WORDS = new Set([
  "bad", "terrible", "awful", "horrible", "poor", "negative", "bearish",
  "sell", "weak", "lose", "losing", "fail", "down", "low", "worst",
  "hate", "disappointing", "disaster", "crash", "dump",
]);

const INTENSIFIERS = new Set(["very", "extremely", "really", "absolutely", "totally"]);
const NEGATIONS = new Set(["not", "no", "never", "neither", "nobody", "nothing"]);

export interface SentimentScore {
  compound: number; // -1 to +1
  positive: number;
  negative: number;
  neutral: number;
}

export function analyzeSentiment(text: string): SentimentScore {
  const words = text.toLowerCase().split(/\s+/);
  let score = 0;
  let positiveCount = 0;
  let negativeCount = 0;
  
  for (let i = 0; i < words.length; i++) {
    const word = words[i].replace(/[^\w]/g, "");
    let wordScore = 0;
    
    if (POSITIVE_WORDS.has(word)) {
      wordScore = 1;
      positiveCount++;
    } else if (NEGATIVE_WORDS.has(word)) {
      wordScore = -1;
      negativeCount++;
    }
    
    // Apply intensifier
    if (i > 0 && INTENSIFIERS.has(words[i - 1])) {
      wordScore *= 1.5;
    }
    
    // Apply negation
    if (i > 0 && NEGATIONS.has(words[i - 1])) {
      wordScore *= -1;
    }
    
    score += wordScore;
  }
  
  // Normalize
  const totalWords = words.length || 1;
  const compound = Math.max(-1, Math.min(1, score / Math.sqrt(totalWords)));
  
  const total = positiveCount + negativeCount || 1;
  return {
    compound,
    positive: positiveCount / total,
    negative: negativeCount / total,
    neutral: 1 - (positiveCount + negativeCount) / total,
  };
}

/**
 * Convert VADER compound score to probability using sigmoid
 */
export function compoundToProbability(compound: number): number {
  // Sigmoid transform: compound in [-1, 1] → probability in [0.2, 0.8]
  // P = 0.5 + 0.3 * compound
  // This gives a reasonable mapping without extreme values
  return Math.max(0.2, Math.min(0.8, 0.5 + 0.3 * compound));
}

