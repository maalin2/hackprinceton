"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { TrendingUp, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  saveUserPreferences,
  useUserPreferences,
} from "@/lib/useUserPreferences";
import {
  MAX_PREFERENCE_TOPICS,
  PREFERENCE_TOPICS,
} from "@/lib/preferenceTopics";

export default function OnboardingPage() {
  const router = useRouter();
  const { preferences, loading } = useUserPreferences();
  const [step, setStep] = useState(1);
  const [name, setName] = useState("");
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!loading && preferences) {
      // User already completed onboarding
      router.replace("/dashboard");
    }
  }, [loading, preferences, router]);

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

  const handleNameSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (name.trim()) {
      setStep(2);
    }
  };

  const handleComplete = async () => {
    if (selectedTopics.length !== MAX_PREFERENCE_TOPICS || !name.trim()) {
      return;
    }

    setIsSubmitting(true);

    const payload = {
      name: name.trim(),
      topics: selectedTopics,
      completedAt: new Date().toISOString(),
    } as const;

    try {
      await saveUserPreferences(payload);
      router.replace("/dashboard");
    } catch (error) {
      console.error("Error saving preferences:", error);
      setIsSubmitting(false);
    }
  };

  if (loading || preferences) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-secondary/20 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl p-8">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <TrendingUp className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold">Welcome to Magic Conch</h1>
          </div>
          <p className="text-muted-foreground">
            Let&apos;s personalize your trading experience
          </p>
        </div>

        <div className="flex justify-center gap-2 mb-8">
          <div
            className={cn(
              "h-2 w-24 rounded-full transition-colors",
              step >= 1 ? "bg-primary" : "bg-muted"
            )}
          />
          <div
            className={cn(
              "h-2 w-24 rounded-full transition-colors",
              step >= 2 ? "bg-primary" : "bg-muted"
            )}
          />
        </div>

        {step === 1 && (
          <form onSubmit={handleNameSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="name" className="text-lg">
                What should we call you?
              </Label>
              <Input
                id="name"
                type="text"
                placeholder="Enter your name"
                value={name}
                onChange={(event) => setName(event.target.value)}
                className="text-lg py-6"
                autoFocus
              />
              <p className="text-sm text-muted-foreground">
                This will be displayed at the top of your dashboard
              </p>
            </div>

            <Button
              type="submit"
              size="lg"
              className="w-full"
              disabled={!name.trim()}
            >
              Continue
            </Button>
          </form>
        )}

        {step === 2 && (
          <div className="space-y-6">
            <div className="space-y-2">
              <Label className="text-lg">
                Select your top {MAX_PREFERENCE_TOPICS} topics
              </Label>
              <p className="text-sm text-muted-foreground">
                We&apos;ll use these to tailor market recommendations
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3">
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
                      "relative p-4 rounded-lg border-2 transition-all text-left",
                      "hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed",
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
                      <CheckCircle2 className="absolute top-3 right-3 h-5 w-5 text-primary" />
                    )}
                  </button>
                );
              })}
            </div>

            <div className="text-center text-sm text-muted-foreground">
              {selectedTopics.length}/{MAX_PREFERENCE_TOPICS} topics selected
            </div>

            <div className="flex gap-3">
              <Button
                type="button"
                variant="outline"
                size="lg"
                className="w-full"
                onClick={() => setStep(1)}
              >
                Back
              </Button>
              <Button
                type="button"
                size="lg"
                className="w-full"
                disabled={
                  selectedTopics.length !== MAX_PREFERENCE_TOPICS ||
                  isSubmitting
                }
                onClick={handleComplete}
              >
                {isSubmitting ? "Saving..." : "Complete Setup"}
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
