"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { useUIStore } from "@/store/ui";
import { useTheme } from "next-themes";
import { Settings as SettingsIcon, Moon, Sun, Save } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

export default function SettingsPage() {
  const { settings, updateSettings } = useUIStore();
  const { theme, setTheme } = useTheme();
  const { toast } = useToast();

  const handleSave = () => {
    toast({
      title: "Settings Saved",
      description: "Your preferences have been updated successfully.",
    });
  };

  return (
    <div className="container py-6 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
          <SettingsIcon className="h-8 w-8" />
          Settings
        </h1>
        <p className="text-muted-foreground">
          Configure your trading parameters and preferences
        </p>
      </div>

      <div className="space-y-6">
        {/* Strategy Weights */}
        <Card>
          <CardHeader>
            <CardTitle>Strategy Weights</CardTitle>
            <CardDescription>
              Adjust the balance between quantitative and sentiment analysis
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <Label htmlFor="quant-weight">Quantitative Model Weight</Label>
                <span className="text-sm font-mono font-semibold">
                  {Math.round(settings.quantWeight * 100)}%
                </span>
              </div>
              <input
                id="quant-weight"
                type="range"
                min="0"
                max="100"
                step="5"
                value={settings.quantWeight * 100}
                onChange={(e) =>
                  updateSettings({ quantWeight: Number(e.target.value) / 100 })
                }
                className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
              />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <Label htmlFor="sentiment-weight">
                  Sentiment Analysis Weight
                </Label>
                <span className="text-sm font-mono font-semibold">
                  {Math.round(settings.sentimentWeight * 100)}%
                </span>
              </div>
              <input
                id="sentiment-weight"
                type="range"
                min="0"
                max="100"
                step="5"
                value={settings.sentimentWeight * 100}
                onChange={(e) =>
                  updateSettings({
                    sentimentWeight: Number(e.target.value) / 100,
                  })
                }
                className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
              />
            </div>

            <p className="text-xs text-muted-foreground">
              Note: Weights are normalized automatically. Higher weight means
              more influence on final decision.
            </p>
          </CardContent>
        </Card>

        {/* Risk Parameters */}
        <Card>
          <CardHeader>
            <CardTitle>Risk Parameters</CardTitle>
            <CardDescription>
              Set thresholds for trade entry and position sizing
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="min-edge">Minimum Edge Threshold (%)</Label>
                <Input
                  id="min-edge"
                  type="number"
                  min="0"
                  max="100"
                  step="1"
                  value={settings.minEdgeThreshold * 100}
                  onChange={(e) =>
                    updateSettings({
                      minEdgeThreshold: Number(e.target.value) / 100,
                    })
                  }
                  className="font-mono"
                />
                <p className="text-xs text-muted-foreground">
                  Only enter trades with edge above this threshold
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="max-spread">Maximum Spread (¢)</Label>
                <Input
                  id="max-spread"
                  type="number"
                  min="0"
                  max="100"
                  step="1"
                  value={settings.maxSpread}
                  onChange={(e) =>
                    updateSettings({ maxSpread: Number(e.target.value) })
                  }
                  className="font-mono"
                />
                <p className="text-xs text-muted-foreground">
                  Avoid markets with spreads wider than this
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="max-position">Maximum Position Size</Label>
                <Input
                  id="max-position"
                  type="number"
                  min="100"
                  max="10000"
                  step="100"
                  value={settings.maxPositionSize}
                  onChange={(e) =>
                    updateSettings({ maxPositionSize: Number(e.target.value) })
                  }
                  className="font-mono"
                />
                <p className="text-xs text-muted-foreground">
                  Maximum contracts per position
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Appearance */}
        <Card>
          <CardHeader>
            <CardTitle>Appearance</CardTitle>
            <CardDescription>
              Customize the look and feel of the dashboard
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="theme">Dark Mode</Label>
                <p className="text-sm text-muted-foreground">
                  Toggle between light and dark themes
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Sun className="h-4 w-4" />
                <Switch
                  id="theme"
                  checked={theme === "dark"}
                  onCheckedChange={(checked) =>
                    setTheme(checked ? "dark" : "light")
                  }
                />
                <Moon className="h-4 w-4" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* API Keys (Placeholder) */}
        <Card>
          <CardHeader>
            <CardTitle>API Configuration</CardTitle>
            <CardDescription>
              Connect your Kalshi account for live trading
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="api-key">API Key ID</Label>
              <Input
                id="api-key"
                type="text"
                placeholder="Enter your Kalshi API Key ID"
                className="font-mono"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="api-secret">Private Key</Label>
              <Input
                id="api-secret"
                type="password"
                placeholder="Enter your private key (RSA format)"
                className="font-mono"
              />
            </div>
            <p className="text-xs text-muted-foreground">
              Currently in paper trading mode. API keys are not saved or
              transmitted.
            </p>
          </CardContent>
        </Card>

        {/* Save Button */}
        <div className="flex justify-end">
          <Button onClick={handleSave} size="lg">
            <Save className="h-4 w-4 mr-2" />
            Save Settings
          </Button>
        </div>
      </div>
    </div>
  );
}
