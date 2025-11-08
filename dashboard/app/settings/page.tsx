"use client";

import { useEffect, useRef, useState } from "react";
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
import { Settings as SettingsIcon, Moon, Sun, Save, CheckCircle2 } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { useRouter } from "next/navigation";
import {
  consumeSkipOnboardingRedirect,
  saveUserPreferences,
  useUserPreferences,
} from "@/lib/useUserPreferences";
import { PREFERENCE_TOPICS, MAX_PREFERENCE_TOPICS } from "@/lib/preferenceTopics";
import { cn } from "@/lib/utils";

export default function SettingsPage() {
  const router = useRouter();
  const { settings, updateSettings } = useUIStore();
  const { theme, setTheme } = useTheme();
  const { toast } = useToast();
  const { preferences, loading, refreshPreferences } = useUserPreferences();
  const skipRedirectRef = useRef(false);
  const [name, setName] = useState("");
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (preferences) {
      setName(preferences.name ?? "");
      setSelectedTopics(
        Array.isArray(preferences.topics)
          ? preferences.topics.slice(0, MAX_PREFERENCE_TOPICS)
          : []
      );
    }
  }, [preferences]);

  useEffect(() => {
    if (!loading && !preferences) {
      if (!skipRedirectRef.current) {
        const shouldSkip = consumeSkipOnboardingRedirect();
        if (shouldSkip) {
          skipRedirectRef.current = true;
          return;
        }
      } else {
        return;
      }
      router.replace("/onboarding");
    }
  }, [loading, preferences, router]);

  useEffect(() => {
    if (preferences) {
      skipRedirectRef.current = false;
    }
  }, [preferences]);

  if (loading || !preferences) {
    return (
      <div className="container py-6">
        <div className="flex items-center justify-center h-96">
          <p className="text-muted-foreground">Loading your settings...</p>
        </div>
      </div>
    );
  }

  const toggleTopic = (topicId: string) => {
    setSelectedTopics((current) => {
      if (current.includes(topicId)) {
        return current.filter((id) => id !== topicId);
      }

      if (current.length >= MAX_PREFERENCE_TOPICS) {
        return current;
      }

      return [...current, topicId];
    });
  };

  const trimmedName = name.trim();
  const originalTopics = preferences?.topics ?? [];
  const topicsMatch =
    originalTopics.length === selectedTopics.length &&
    originalTopics.every((topic, index) => topic === selectedTopics[index]);
  const nameChanged = !!preferences && trimmedName !== preferences.name;
  const hasChanges = !!preferences && (nameChanged || !topicsMatch);
  const hasValidTopics = selectedTopics.length === MAX_PREFERENCE_TOPICS;
  const canSave =
    !!preferences && !!trimmedName && hasValidTopics && hasChanges && !isSaving && !loading;

  const handleSave = async () => {
    if (!preferences) {
      return;
    }

    if (!trimmedName) {
      toast({
        variant: "destructive",
        title: "Name required",
        description: "Please enter a display name before saving.",
      });
      return;
    }

    if (!hasValidTopics) {
      toast({
        variant: "destructive",
        title: "Select topics",
        description: `Choose ${MAX_PREFERENCE_TOPICS} topics to personalize your dashboard.`,
      });
      return;
    }

    if (!hasChanges) {
      toast({
        title: "No changes detected",
        description: "Update your profile details before saving again.",
      });
      return;
    }

    setIsSaving(true);

    try {
      await saveUserPreferences({
        name: trimmedName,
        topics: selectedTopics,
        completedAt:
          preferences.completedAt ||
          new Date().toISOString(),
      });

      await refreshPreferences();

      toast({
        title: "Settings saved",
        description: "Your preferences have been updated successfully.",
      });
    } catch (error) {
      console.error("Error saving user preferences:", error);
      toast({
        variant: "destructive",
        title: "Save failed",
        description: "We couldn’t update your preferences. Please try again.",
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="container py-6 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
          <SettingsIcon className="h-8 w-8" />
          Settings
        </h1>
        <p className="text-muted-foreground">
          Configure your trading parameters and preferences. Don't forget to scroll to the bottom and save!
        </p>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Profile</CardTitle>
            <CardDescription>
              Update your display name and preferred market topics
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="display-name">Display Name</Label>
              <Input
                id="display-name"
                type="text"
                placeholder="Enter your name"
                value={name}
                onChange={(event) => setName(event.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                This appears at the top of your dashboard.
              </p>
            </div>

            <div className="space-y-3">
              <div className="flex items-start justify-between gap-4 flex-wrap">
                <div>
                  <Label>Select {MAX_PREFERENCE_TOPICS} preferred topics</Label>
                  <p className="text-sm text-muted-foreground">
                    We use these to tailor market recommendations.
                  </p>
                </div>
                <span className="text-sm text-muted-foreground">
                  {selectedTopics.length}/{MAX_PREFERENCE_TOPICS} selected
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {PREFERENCE_TOPICS.map((topic) => {
                  const isSelected = selectedTopics.includes(topic.id);
                  const canSelect =
                    isSelected || selectedTopics.length < MAX_PREFERENCE_TOPICS;

                  return (
                    <button
                      key={topic.id}
                      type="button"
                      disabled={!canSelect}
                      onClick={() => toggleTopic(topic.id)}
                      className={cn(
                        "relative flex items-center justify-between gap-3 rounded-lg border-2 p-3 text-left transition-all",
                        "hover:shadow-md disabled:cursor-not-allowed disabled:opacity-50",
                        isSelected
                          ? "border-primary bg-primary/10"
                          : "border-border hover:border-primary/50"
                      )}
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-2xl" aria-hidden>
                          {topic.emoji}
                        </span>
                        <span className="font-medium">{topic.name}</span>
                      </div>
                      {isSelected && (
                        <CheckCircle2 className="h-5 w-5 text-primary" />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          </CardContent>
        </Card>

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
          <Button onClick={handleSave} size="lg" disabled={!canSave}>
            <Save className="h-4 w-4 mr-2" />
            {isSaving ? "Saving..." : "Save Settings"}
          </Button>
        </div>
      </div>
    </div>
  );
}
