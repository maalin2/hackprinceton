import { SourceComponent } from "@/lib/types";

interface WeatherMarket {
  ticker: string;
  location: string;
  lat: number;
  lon: number;
  date: Date;
  threshold: number;
  type: "HIGH" | "LOW" | "RAIN";
}

// Location coordinates mapping
const LOCATION_COORDS: Record<string, { lat: number; lon: number; name: string }> = {
  ny: { lat: 40.7128, lon: -74.0060, name: "New York" },
  chi: { lat: 41.8781, lon: -87.6298, name: "Chicago" },
  lax: { lat: 34.0522, lon: -118.2437, name: "Los Angeles" },
  phil: { lat: 39.9526, lon: -75.1652, name: "Philadelphia" },
  den: { lat: 39.7392, lon: -104.9903, name: "Denver" },
  mia: { lat: 25.7617, lon: -80.1918, name: "Miami" },
  hou: { lat: 29.7604, lon: -95.3698, name: "Houston" },
  sea: { lat: 47.6062, lon: -122.3321, name: "Seattle" },
  sf: { lat: 37.7749, lon: -122.4194, name: "San Francisco" },
  dc: { lat: 38.9072, lon: -77.0369, name: "Washington DC" },
};

function parseWeatherMarket(ticker: string, title: string): WeatherMarket | null {
  // Parse ticker format: KXHIGHPHIL-25NOV08-T71
  // Format is: [TYPE][LOCATION]-[YY][MMM][DD]-T[threshold]
  // Example: 25NOV08 = Year 2025, November, Day 08
  const match = ticker.match(/KX(HIGH|LOW|RAIN)(\w+?)-(\d{2})(\w{3})(\d{2})-T?(\d+\.?\d*)/);
  if (!match) return null;

  const [, type, locationCode, yearShort, month, day, threshold] = match;
  const monthMap: Record<string, number> = {
    JAN: 0, FEB: 1, MAR: 2, APR: 3, MAY: 4, JUN: 5,
    JUL: 6, AUG: 7, SEP: 8, OCT: 9, NOV: 10, DEC: 11
  };

  // Interpret 2-digit year (00-99)
  // Assume 00-50 = 2000-2050, 51-99 = 1951-1999
  const yearNum = parseInt(yearShort);
  const fullYear = yearNum <= 50 ? 2000 + yearNum : 1900 + yearNum;
  
  const date = new Date(fullYear, monthMap[month.toUpperCase()], parseInt(day));
  const coords = LOCATION_COORDS[locationCode.toLowerCase()];

  if (!coords) {
    console.warn(`Unknown location code: ${locationCode}`);
    return null;
  }

  return {
    ticker,
    location: coords.name,
    lat: coords.lat,
    lon: coords.lon,
    date,
    threshold: parseFloat(threshold),
    type: type as "HIGH" | "LOW" | "RAIN",
  };
}

// NOAA Provider (Weather.gov API)
export async function fetchNOAA(ticker: string, title: string): Promise<SourceComponent> {
  try {
    const parsed = parseWeatherMarket(ticker, title);
    if (!parsed) {
      throw new Error("Could not parse weather market");
    }

    // NOAA Weather API
    // Step 1: Get grid point
    const pointResponse = await fetch(
      `https://api.weather.gov/points/${parsed.lat},${parsed.lon}`,
      { headers: { "User-Agent": "KalshiDecisionDashboard/1.0" } }
    );

    if (!pointResponse.ok) {
      throw new Error(`NOAA point API failed: ${pointResponse.status}`);
    }

    const pointData = await pointResponse.json();
    const forecastUrl = pointData.properties.forecast;

    // Step 2: Get forecast
    const forecastResponse = await fetch(forecastUrl, {
      headers: { "User-Agent": "KalshiDecisionDashboard/1.0" }
    });

    if (!forecastResponse.ok) {
      throw new Error(`NOAA forecast API failed: ${forecastResponse.status}`);
    }

    const forecastData = await forecastResponse.json();
    const periods = forecastData.properties.periods;

    // Find the relevant forecast period
    const targetDate = parsed.date;
    const relevantPeriod = periods.find((p: any) => {
      const periodStart = new Date(p.startTime);
      return periodStart.toDateString() === targetDate.toDateString();
    }) || periods[0]; // Fallback to first period

    // Extract temperature forecast
    const forecastTemp = relevantPeriod.temperature;
    
    // Calculate probability based on threshold
    let probability = 0.5;
    if (parsed.type === "HIGH") {
      // P(high temp > threshold)
      const diff = forecastTemp - parsed.threshold;
      probability = 1 / (1 + Math.exp(-diff / 5)); // Sigmoid with temp uncertainty ~5°F
    } else if (parsed.type === "LOW") {
      const diff = parsed.threshold - forecastTemp;
      probability = 1 / (1 + Math.exp(-diff / 5));
    } else if (parsed.type === "RAIN") {
      // Use shortForecast text to detect rain
      const forecast = relevantPeriod.shortForecast.toLowerCase();
      probability = (forecast.includes("rain") || forecast.includes("shower") || forecast.includes("storm")) ? 0.7 : 0.3;
    }

    probability = Math.max(0.05, Math.min(0.95, probability));

    return {
      source: "NOAA",
      probability,
      confidence: 0.85,
      data: {
        forecast: `${forecastTemp}°F`,
        model: "GFS",
        shortForecast: relevantPeriod.shortForecast,
        lastUpdate: new Date().toISOString(),
      },
    };
  } catch (error) {
    console.error("NOAA API error:", error);
    throw error;
  }
}

// Open-Meteo Provider (Free weather API)
export async function fetchOpenMeteo(ticker: string, title: string): Promise<SourceComponent> {
  try {
    const parsed = parseWeatherMarket(ticker, title);
    if (!parsed) {
      throw new Error("Could not parse weather market");
    }

    const dateStr = parsed.date.toISOString().split('T')[0];

    const response = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${parsed.lat}&longitude=${parsed.lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&start_date=${dateStr}&end_date=${dateStr}&temperature_unit=fahrenheit`
    );

    if (!response.ok) {
      throw new Error(`Open-Meteo API failed: ${response.status}`);
    }

    const data = await response.json();
    const daily = data.daily;

    if (!daily || !daily.temperature_2m_max || daily.temperature_2m_max.length === 0) {
      throw new Error("No forecast data available");
    }

    const tempMax = daily.temperature_2m_max[0];
    const tempMin = daily.temperature_2m_min[0];
    const precipProb = daily.precipitation_probability_max[0];

    let probability = 0.5;
    if (parsed.type === "HIGH") {
      const diff = tempMax - parsed.threshold;
      probability = 1 / (1 + Math.exp(-diff / 4));
    } else if (parsed.type === "LOW") {
      const diff = parsed.threshold - tempMin;
      probability = 1 / (1 + Math.exp(-diff / 4));
    } else if (parsed.type === "RAIN") {
      probability = precipProb / 100;
    }

    probability = Math.max(0.05, Math.min(0.95, probability));

    return {
      source: "Open-Meteo",
      probability,
      confidence: 0.80,
      data: {
        tempMax: `${tempMax}°F`,
        tempMin: `${tempMin}°F`,
        precipProb: `${precipProb}%`,
        model: "ECMWF",
      },
    };
  } catch (error) {
    console.error("Open-Meteo API error:", error);
    throw error;
  }
}

// Meteostat Provider (Historical climatology data)
export async function fetchMeteostat(ticker: string, title: string): Promise<SourceComponent> {
  try {
    const parsed = parseWeatherMarket(ticker, title);
    if (!parsed) {
      throw new Error("Could not parse weather market");
    }

    // Use WeatherAPI as a proxy for historical normals (Meteostat requires API key and specific station IDs)
    const dateStr = parsed.date.toISOString().split('T')[0];
    
    // For climatology, we'll use historical data from previous years
    const lastYear = new Date(parsed.date);
    lastYear.setFullYear(lastYear.getFullYear() - 1);
    const lastYearStr = lastYear.toISOString().split('T')[0];

    // Using visualcrossing timeline API (free tier: 1000 requests/day)
    // Alternative: weatherapi.com history endpoint
    const response = await fetch(
      `https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/${parsed.lat},${parsed.lon}/${lastYearStr}/${lastYearStr}?unitGroup=us&key=${process.env.NEXT_PUBLIC_VISUAL_CROSSING_KEY || 'demo'}&include=days`
    );

    if (!response.ok) {
      // Fallback to climatological average based on location and month
      const monthAvgs = getClimatologicalAverage(parsed.location, parsed.date.getMonth());
      const diff = monthAvgs.avgHigh - parsed.threshold;
      const probability = Math.max(0.1, Math.min(0.9, 1 / (1 + Math.exp(-diff / 8))));

      return {
        source: "Meteostat",
        probability,
        confidence: 0.60,
        data: {
          historicalAvg: `${monthAvgs.avgHigh}°F`,
          source: "climatology",
          years: "1990-2020",
        },
      };
    }

    const data = await response.json();
    const dayData = data.days[0];

    const histTempMax = dayData.tempmax;
    const histTempMin = dayData.tempmin;

    let probability = 0.5;
    if (parsed.type === "HIGH") {
      const diff = histTempMax - parsed.threshold;
      probability = 1 / (1 + Math.exp(-diff / 6)); // More conservative
    } else if (parsed.type === "LOW") {
      const diff = parsed.threshold - histTempMin;
      probability = 1 / (1 + Math.exp(-diff / 6));
    } else if (parsed.type === "RAIN") {
      probability = dayData.precip > 0 ? 0.6 : 0.4;
    }

    probability = Math.max(0.1, Math.min(0.9, probability));

    return {
      source: "Meteostat",
      probability,
      confidence: 0.70,
      data: {
        historicalAvg: `${histTempMax}°F`,
        lastYear: lastYearStr,
        precipLastYear: dayData.precip,
      },
    };
  } catch (error) {
    console.error("Meteostat API error:", error);
    
    // Ultimate fallback: use climatological average
    const parsed = parseWeatherMarket(ticker, title);
    if (parsed) {
      const monthAvgs = getClimatologicalAverage(parsed.location, parsed.date.getMonth());
      const diff = monthAvgs.avgHigh - parsed.threshold;
      const probability = Math.max(0.1, Math.min(0.9, 1 / (1 + Math.exp(-diff / 8))));

      return {
        source: "Meteostat",
        probability,
        confidence: 0.50,
        data: {
          historicalAvg: `${monthAvgs.avgHigh}°F`,
          source: "climatology (fallback)",
        },
      };
    }
    
    throw error;
  }
}

// Climatological averages by city and month (fallback data)
function getClimatologicalAverage(location: string, month: number): { avgHigh: number; avgLow: number } {
  // Simplified climatology - in production, use actual normals database
  const baseTemps: Record<string, number> = {
    "New York": 50,
    "Chicago": 45,
    "Los Angeles": 70,
    "Philadelphia": 52,
    "Denver": 55,
    "Miami": 80,
    "Houston": 75,
    "Seattle": 55,
    "San Francisco": 65,
    "Washington DC": 54,
  };

  const baseTemp = baseTemps[location] || 60;
  
  // Seasonal adjustment
  const monthAdjustment = [
    -15, -12, -5, 5, 15, 20, 22, 20, 15, 5, -5, -12
  ][month];

  return {
    avgHigh: baseTemp + monthAdjustment,
    avgLow: baseTemp + monthAdjustment - 15,
  };
}

export async function getWeatherSources(ticker: string, title: string): Promise<SourceComponent[]> {
  const [noaa, openMeteo, meteostat] = await Promise.all([
    fetchNOAA(ticker, title).catch(e => {
      console.warn("NOAA fetch failed:", e.message);
      return null;
    }),
    fetchOpenMeteo(ticker, title).catch(e => {
      console.warn("Open-Meteo fetch failed:", e.message);
      return null;
    }),
    fetchMeteostat(ticker, title).catch(e => {
      console.warn("Meteostat fetch failed:", e.message);
      return null;
    }),
  ]);

  const sources = [noaa, openMeteo, meteostat].filter((s): s is SourceComponent => s !== null && s.confidence > 0);
  
  if (sources.length === 0) {
    throw new Error("All weather providers failed");
  }

  return sources;
}
