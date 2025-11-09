/**
 * API Test Utility
 * 
 * Call this from browser console to test the Python backend connection
 * 
 * Usage:
 *   import { testAPIConnection } from '@/lib/testAPI';
 *   testAPIConnection();
 * 
 * Or from browser console:
 *   window.testAPI()
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function testAPIConnection() {
  console.log("\n" + "=".repeat(100));
  console.log("🧪 TESTING PYTHON API CONNECTION");
  console.log("=".repeat(100));
  console.log(`API Base URL: ${API_BASE_URL}`);
  console.log(`Time: ${new Date().toLocaleString()}`);
  console.log("=".repeat(100) + "\n");

  try {
    // Test 1: Health check
    console.log("📡 Test 1: Health Check");
    console.log("   Calling: GET /");
    
    const healthResponse = await fetch(`${API_BASE_URL}/`);
    const healthData = await healthResponse.json();
    
    console.log("   ✅ Status:", healthResponse.status);
    console.log("   📦 Response:", JSON.stringify(healthData, null, 2));
    console.log();

    // Test 2: Status check
    console.log("📡 Test 2: Status Check");
    console.log("   Calling: GET /api/status");
    
    const statusResponse = await fetch(`${API_BASE_URL}/api/status`);
    const statusData = await statusResponse.json();
    
    console.log("   ✅ Status:", statusResponse.status);
    console.log("   📦 Response:", JSON.stringify(statusData, null, 2));
    console.log();

    // Test 3: Get recommendations
    console.log("📡 Test 3: Get Recommendations");
    console.log("   Calling: GET /api/recommendations");
    
    const recsResponse = await fetch(`${API_BASE_URL}/api/recommendations`);
    const recsData = await recsResponse.json();
    
    console.log("   ✅ Status:", recsResponse.status);
    console.log("   📊 Response Status:", recsData.status);
    console.log("   📦 Opportunities Count:", recsData.opportunities?.length || 0);
    
    if (recsData.opportunities && recsData.opportunities.length > 0) {
      console.log("\n   🎯 SAMPLE RECOMMENDATION:");
      const sample = recsData.opportunities[0];
      console.log("   " + "-".repeat(80));
      console.log("   Ticker:", sample.ticker);
      console.log("   Title:", sample.title);
      console.log("   Category:", sample.category);
      console.log("   Action:", sample.action);
      console.log("   Quant Edge:", (sample.quant_edge * 100).toFixed(1) + "%");
      console.log("   Market Prob:", (sample.market_prob * 100).toFixed(1) + "%");
      console.log("   Combined Confidence:", (sample.combined_confidence * 100).toFixed(1) + "%");
      
      if (sample.grok_sentiment) {
        console.log("\n   🤖 GROK SENTIMENT:");
        console.log("   Label:", sample.grok_sentiment.label);
        console.log("   Score:", sample.grok_sentiment.score + "%");
        console.log("   Confidence:", sample.grok_sentiment.confidence);
        if (sample.grok_sentiment.key_themes) {
          console.log("   Key Themes:", sample.grok_sentiment.key_themes.join(", "));
        }
      }
      
      console.log("\n   💡 REASONING:");
      console.log("   " + sample.reasoning);
      console.log("   " + "-".repeat(80));
      
      console.log("\n   📊 ALL RECOMMENDATIONS:");
      recsData.opportunities.forEach((opp: any, i: number) => {
        console.log(`   ${i + 1}. ${opp.ticker} - ${opp.action} (Edge: ${(opp.quant_edge * 100).toFixed(1)}%)`);
      });
    } else if (recsData.status === "analyzing") {
      console.log("\n   ⏳ Backend is currently analyzing markets");
      console.log("   💡 Wait 30-60 seconds and try again");
    } else if (recsData.status === "empty") {
      console.log("\n   ⚠️  No recommendations available yet");
      console.log("   💡 Wait for first analysis to complete (usually 30-60 seconds)");
    }
    
    console.log("\n" + "=".repeat(100));
    console.log("✅ API CONNECTION TEST COMPLETE");
    console.log("=".repeat(100));
    
    return {
      success: true,
      health: healthData,
      status: statusData,
      recommendations: recsData
    };
    
  } catch (error: any) {
    console.log("\n" + "=".repeat(100));
    console.log("❌ API CONNECTION TEST FAILED");
    console.log("=".repeat(100));
    console.error("\n🔥 Error:", error.message);
    console.error("\n💡 Troubleshooting:");
    console.error("   1. Is Python backend running? (python3 api_server.py)");
    console.error("   2. Is it running on port 8000?");
    console.error("   3. Check Terminal 1 for backend errors");
    console.error("   4. Try: curl http://localhost:8000/api/status");
    console.log("=".repeat(100) + "\n");
    
    return {
      success: false,
      error: error.message
    };
  }
}

// Make it available globally for easy browser console access
if (typeof window !== "undefined") {
  (window as any).testAPI = testAPIConnection;
}

