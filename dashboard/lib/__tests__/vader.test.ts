import { analyzeSentiment, compoundToProbability } from "../agents/sentiment/vader";

describe("VADER Sentiment Analysis", () => {
  describe("analyzeSentiment", () => {
    it("should detect positive sentiment", () => {
      const result = analyzeSentiment("This is great! Excellent opportunity.");
      expect(result.compound).toBeGreaterThan(0);
      expect(result.positive).toBeGreaterThan(0);
    });

    it("should detect negative sentiment", () => {
      const result = analyzeSentiment("This is terrible and awful. Very bad.");
      expect(result.compound).toBeLessThan(0);
      expect(result.negative).toBeGreaterThan(0);
    });

    it("should detect neutral sentiment", () => {
      const result = analyzeSentiment("The market is at 50 cents.");
      expect(Math.abs(result.compound)).toBeLessThan(0.2);
    });

    it("should handle intensifiers", () => {
      const normal = analyzeSentiment("This is good.");
      const intensified = analyzeSentiment("This is very good.");
      expect(Math.abs(intensified.compound)).toBeGreaterThan(Math.abs(normal.compound));
    });

    it("should handle negations", () => {
      const positive = analyzeSentiment("This is good.");
      const negated = analyzeSentiment("This is not good.");
      expect(negated.compound).toBeLessThan(positive.compound);
    });

    it("should handle bullish terms", () => {
      const result = analyzeSentiment("Bullish setup! Strong buy signal.");
      expect(result.compound).toBeGreaterThan(0.3);
    });

    it("should handle bearish terms", () => {
      const result = analyzeSentiment("Bearish pattern. Weak and losing.");
      expect(result.compound).toBeLessThan(-0.3);
    });

    it("should normalize compound score to [-1, 1]", () => {
      const result = analyzeSentiment("Extremely good great excellent fantastic amazing");
      expect(result.compound).toBeGreaterThanOrEqual(-1);
      expect(result.compound).toBeLessThanOrEqual(1);
    });
  });

  describe("compoundToProbability", () => {
    it("should map neutral sentiment to 0.5", () => {
      const prob = compoundToProbability(0);
      expect(prob).toBeCloseTo(0.5, 1);
    });

    it("should map positive sentiment to > 0.5", () => {
      const prob = compoundToProbability(0.5);
      expect(prob).toBeGreaterThan(0.5);
    });

    it("should map negative sentiment to < 0.5", () => {
      const prob = compoundToProbability(-0.5);
      expect(prob).toBeLessThan(0.5);
    });

    it("should cap extreme positive sentiment", () => {
      const prob = compoundToProbability(1.0);
      expect(prob).toBeLessThanOrEqual(0.8);
    });

    it("should cap extreme negative sentiment", () => {
      const prob = compoundToProbability(-1.0);
      expect(prob).toBeGreaterThanOrEqual(0.2);
    });

    it("should produce reasonable probabilities for typical sentiment", () => {
      const prob1 = compoundToProbability(0.3); // Mild positive
      const prob2 = compoundToProbability(-0.3); // Mild negative
      
      expect(prob1).toBeGreaterThan(0.5);
      expect(prob1).toBeLessThan(0.7);
      expect(prob2).toBeGreaterThan(0.3);
      expect(prob2).toBeLessThan(0.5);
    });
  });

  describe("end-to-end sentiment → probability", () => {
    it("should convert positive text to bullish probability", () => {
      const sentiment = analyzeSentiment("Strong bullish signal. Buy opportunity!");
      const prob = compoundToProbability(sentiment.compound);
      expect(prob).toBeGreaterThan(0.5);
    });

    it("should convert negative text to bearish probability", () => {
      const sentiment = analyzeSentiment("Bearish trend. Sell signal. Bad outlook.");
      const prob = compoundToProbability(sentiment.compound);
      expect(prob).toBeLessThan(0.5);
    });

    it("should handle mixed sentiment reasonably", () => {
      const sentiment = analyzeSentiment("Good setup but weak momentum. Uncertain.");
      const prob = compoundToProbability(sentiment.compound);
      expect(prob).toBeGreaterThan(0.4);
      expect(prob).toBeLessThan(0.6);
    });
  });
});

