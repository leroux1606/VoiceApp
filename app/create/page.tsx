"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Button } from "@/app/components/ui/button";
import { Input } from "@/app/components/ui/input";
import { Label } from "@/app/components/ui/label";
import { Textarea } from "@/app/components/ui/textarea";
import { Progress } from "@/app/components/ui/progress";
import { Navbar } from "@/app/components/navbar";
import { ChevronRight, ChevronLeft, Loader2 } from "lucide-react";

type VideoStyle = "educational" | "entertainment" | "tutorial" | "review" | "news";
type Tone = "professional" | "casual" | "energetic" | "calm";

interface VideoConfig {
  topic: string;
  style: VideoStyle;
  duration: number;
  tone: Tone;
  targetAudience: string;
}

export default function CreateVideoPage() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState<VideoConfig>({
    topic: "",
    style: "educational",
    duration: 5,
    tone: "professional",
    targetAudience: "",
  });
  const [script, setScript] = useState("");
  const [generating, setGenerating] = useState(false);

  const handleNext = () => {
    if (step < 4) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleGenerateScript = async () => {
    setGenerating(true);
    try {
      const response = await fetch("/api/generate/script", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      const data = await response.json();
      setScript(data.script || "");
      setStep(3);
    } catch (error) {
      console.error("Error generating script:", error);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className="container py-8 max-w-4xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Create New Video</h1>
          <p className="text-muted-foreground">
            Step {step} of 4: {["Topic & Style", "Configuration", "Script Review", "Generate Video"][step - 1]}
          </p>
          <Progress value={(step / 4) * 100} className="mt-4" />
        </div>

        {step === 1 && (
          <Card>
            <CardHeader>
              <CardTitle>Topic & Style</CardTitle>
              <CardDescription>
                Tell us what your video is about
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="topic">Video Topic *</Label>
                <Textarea
                  id="topic"
                  placeholder="e.g., How to build a React application..."
                  value={config.topic}
                  onChange={(e) => setConfig({ ...config, topic: e.target.value })}
                  rows={4}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="style">Video Style *</Label>
                <select
                  id="style"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  value={config.style}
                  onChange={(e) => setConfig({ ...config, style: e.target.value as VideoStyle })}
                >
                  <option value="educational">Educational</option>
                  <option value="entertainment">Entertainment</option>
                  <option value="tutorial">Tutorial</option>
                  <option value="review">Review</option>
                  <option value="news">News</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="tone">Tone *</Label>
                <select
                  id="tone"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  value={config.tone}
                  onChange={(e) => setConfig({ ...config, tone: e.target.value as Tone })}
                >
                  <option value="professional">Professional</option>
                  <option value="casual">Casual</option>
                  <option value="energetic">Energetic</option>
                  <option value="calm">Calm</option>
                </select>
              </div>

              <div className="flex justify-end">
                <Button onClick={handleNext} disabled={!config.topic}>
                  Next <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {step === 2 && (
          <Card>
            <CardHeader>
              <CardTitle>Configuration</CardTitle>
              <CardDescription>
                Set video duration and target audience
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="duration">Duration (minutes) *</Label>
                <Input
                  id="duration"
                  type="number"
                  min="1"
                  max="30"
                  value={config.duration}
                  onChange={(e) => setConfig({ ...config, duration: parseInt(e.target.value) || 5 })}
                />
                <p className="text-sm text-muted-foreground">
                  Recommended: 5-15 minutes for best engagement
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="audience">Target Audience</Label>
                <Input
                  id="audience"
                  placeholder="e.g., Developers, Students, General audience..."
                  value={config.targetAudience}
                  onChange={(e) => setConfig({ ...config, targetAudience: e.target.value })}
                />
              </div>

              <div className="flex justify-between">
                <Button variant="outline" onClick={handleBack}>
                  <ChevronLeft className="mr-2 h-4 w-4" /> Back
                </Button>
                <Button onClick={handleGenerateScript} disabled={generating}>
                  {generating ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    "Generate Script"
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {step === 3 && (
          <Card>
            <CardHeader>
              <CardTitle>Script Review</CardTitle>
              <CardDescription>
                Review and edit the generated script
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="script">Script</Label>
                <Textarea
                  id="script"
                  value={script}
                  onChange={(e) => setScript(e.target.value)}
                  rows={20}
                  className="font-mono text-sm"
                />
              </div>

              <div className="flex justify-between">
                <Button variant="outline" onClick={handleBack}>
                  <ChevronLeft className="mr-2 h-4 w-4" /> Back
                </Button>
                <Button onClick={handleNext} disabled={!script}>
                  Continue to Video Generation <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {step === 4 && (
          <Card>
            <CardHeader>
              <CardTitle>Generate Video</CardTitle>
              <CardDescription>
                Configure voice and visual settings, then generate your video
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="voice">Voice Selection</Label>
                <select
                  id="voice"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  defaultValue="default"
                >
                  <option value="default">Default Voice</option>
                  <option value="male-professional">Male Professional</option>
                  <option value="female-professional">Female Professional</option>
                  <option value="male-casual">Male Casual</option>
                  <option value="female-casual">Female Casual</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="visual-style">Visual Style</Label>
                <select
                  id="visual-style"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  defaultValue="modern"
                >
                  <option value="modern">Modern</option>
                  <option value="minimalist">Minimalist</option>
                  <option value="dynamic">Dynamic</option>
                  <option value="cinematic">Cinematic</option>
                </select>
              </div>

              <div className="flex justify-between">
                <Button variant="outline" onClick={handleBack}>
                  <ChevronLeft className="mr-2 h-4 w-4" /> Back
                </Button>
                <Button onClick={() => setLoading(true)} disabled={loading}>
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating Video...
                    </>
                  ) : (
                    "Generate Video"
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
}

