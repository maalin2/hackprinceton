import { DecisionEngine } from "../agents/decision";
import { MarketLite, QuantSignal, SentimentSignal } from "../types";

describe("DecisionEngine", () => {
  let engine: DecisionEngine;
  let mockMarket: MarketLite;
  let mockQuantSignal: QuantSignal;
  let mockSentimentSignal: SentimentSignal;

  beforeEach(() => {
    engine = new DecisionEngine(
      { quantWeight: 0.8, sentimentWeight: 0.2 },
      0.08 // edge threshold
    );

    mockMarket = {
      id: "1",
      ticker: "TEST-MARKET",
      title: "Test Market",
      series: "TEST",
      domain: "Weather",
      yesBid: 40,
      yesAsk: 50,
      lastPrice: 45,
    };

    mockQuantSignal = {
      pQuant: 0.7,
      confidence: 0.85,
      sources: [
        { source: "Source1", probability: 0.7, confidence: 0.85 },
        { source: "Source2", probability: 0.68, confidence: 0.80 },
      ],
      timestamp: new Date(),
    };

    mockSentimentSignal = {
      pSent: 0.6,
      confidence: 0.75,
      nSamples: 25,
      sources: { kalshi: 15, twitter: 10 },
      timestamp: new Date(),
    };
  });

  describe("computeMarketProbability", () => {
    it("should compute mid price from bid/ask", () => {
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      // (40 + 50) / 200 = 0.45
      expect(decision.pMarket).toBe(0.45);
    });

    it("should fallback to lastPrice when bid/ask are zero", () => {
      mockMarket.yesBid = 0;
      mockMarket.yesAsk = 0;
      mockMarket.lastPrice = 60;
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      // 60 / 100 = 0.6
      expect(decision.pMarket).toBe(0.6);
    });

    it("should default to 0.5 when no price data", () => {
      mockMarket.yesBid = 0;
      mockMarket.yesAsk = 0;
      mockMarket.lastPrice = 0;
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      expect(decision.pMarket).toBe(0.5);
    });
  });

  describe("combine signals", () => {
    it("should compute weighted combination (80% quant, 20% sentiment)", () => {
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      // 0.8 * 0.7 + 0.2 * 0.6 = 0.56 + 0.12 = 0.68
      expect(decision.pCombined).toBeCloseTo(0.68, 2);
    });

    it("should downweight sentiment when nSamples < 20", () => {
      mockSentimentSignal.nSamples = 10; // Half of threshold
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      // Sentiment weight reduced by 50%: ws = 0.2 * 0.5 = 0.1, wq = 0.9
      // 0.9 * 0.7 + 0.1 * 0.6 = 0.63 + 0.06 = 0.69
      expect(decision.pCombined).toBeCloseTo(0.69, 2);
    });
  });

  describe("edge calculation and action", () => {
    it("should emit BUY_YES when edge >= threshold", () => {
      mockQuantSignal.pQuant = 0.8; // Combined will be ~0.76
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      // pMarket = 0.45, pCombined = 0.76, edge = 0.31 > 0.08
      expect(decision.action).toBe("BUY_YES");
      expect(decision.edge).toBeGreaterThan(0.08);
    });

    it("should emit BUY_NO when edge <= -threshold", () => {
      mockQuantSignal.pQuant = 0.2; // Combined will be ~0.28
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      // pMarket = 0.45, pCombined = 0.28, edge = -0.17 < -0.08
      expect(decision.action).toBe("BUY_NO");
      expect(decision.edge).toBeLessThan(-0.08);
    });

    it("should emit HOLD when edge is within threshold", () => {
      mockQuantSignal.pQuant = 0.48;
      mockSentimentSignal.pSent = 0.45;
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      // pMarket = 0.45, pCombined ≈ 0.474, edge ≈ 0.024 (within ±0.08)
      expect(decision.action).toBe("HOLD");
      expect(Math.abs(decision.edge)).toBeLessThan(0.08);
    });
  });

  describe("confidence calculation", () => {
    it("should increase confidence with higher edge", () => {
      mockQuantSignal.pQuant = 0.9; // Large edge
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      expect(decision.confidence).toBeGreaterThan(0.7);
    });

    it("should incorporate signal confidences", () => {
      mockQuantSignal.confidence = 0.95;
      mockSentimentSignal.confidence = 0.90;
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      // High signal confidences should boost overall confidence
      expect(decision.confidence).toBeGreaterThan(0.7);
    });
  });

  describe("rationale generation", () => {
    it("should include edge magnitude", () => {
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      expect(decision.rationale).toContain("edge");
    });

    it("should mention top quant source", () => {
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      expect(decision.rationale).toContain("Source1"); // Highest confidence
    });

    it("should include sentiment sample count", () => {
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      expect(decision.rationale).toContain("25 samples");
    });

    it("should include source breakdown", () => {
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      expect(decision.rationale).toContain("Kalshi");
      expect(decision.rationale).toContain("Twitter");
    });
  });

  describe("source collection", () => {
    it("should collect all quant sources", () => {
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      expect(decision.sources).toContain("Source1");
      expect(decision.sources).toContain("Source2");
    });

    it("should include sentiment sources", () => {
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      expect(decision.sources).toContain("Kalshi Comments");
      expect(decision.sources).toContain("Twitter");
    });
  });

  describe("weight updates", () => {
    it("should allow dynamic weight changes", () => {
      engine.setWeights({ quantWeight: 0.5, sentimentWeight: 0.5 });
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      // Equal weights: 0.5 * 0.7 + 0.5 * 0.6 = 0.65
      expect(decision.pCombined).toBeCloseTo(0.65, 2);
    });

    it("should allow edge threshold changes", () => {
      engine.setEdgeThreshold(0.5); // Very high threshold
      mockQuantSignal.pQuant = 0.6;
      const decision = engine.decide(mockMarket, mockQuantSignal, mockSentimentSignal);
      // Even with moderate edge, should be HOLD due to high threshold
      expect(decision.action).toBe("HOLD");
    });
  });
});

