import { NextResponse } from "next/server";
import OpenAI from "openai";

const openai = process.env.OPENAI_API_KEY
  ? new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    })
  : null;

export async function POST(request: Request) {
  try {
    if (!openai) {
      return NextResponse.json(
        { error: "OpenAI API key is not configured. Please set OPENAI_API_KEY in your environment variables." },
        { status: 500 }
      );
    }

    const body = await request.json();
    const { topic, style, duration, tone, targetAudience } = body;

    if (!topic) {
      return NextResponse.json(
        { error: "Topic is required" },
        { status: 400 }
      );
    }

    const prompt = `Create a high-quality YouTube video script for the following requirements:

Topic: ${topic}
Style: ${style}
Duration: ${duration} minutes
Tone: ${tone}
${targetAudience ? `Target Audience: ${targetAudience}` : ""}

The script should:
1. Start with an engaging hook (first 15 seconds)
2. Have a clear introduction explaining what the video covers
3. Break down the main content into logical sections
4. Include smooth transitions between sections
5. End with a strong conclusion and call-to-action
6. Be optimized for YouTube SEO

Format the script with clear section markers and natural pauses indicated. Make it engaging, informative, and suitable for the specified tone and audience.

Script:`;

    const completion = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content:
            "You are an expert YouTube script writer. Create engaging, well-structured scripts that are optimized for viewer retention and YouTube SEO.",
        },
        {
          role: "user",
          content: prompt,
        },
      ],
      temperature: 0.7,
      max_tokens: 2000,
    });

    const script = completion.choices[0]?.message?.content || "";

    return NextResponse.json({ script });
  } catch (error) {
    console.error("Error generating script:", error);
    return NextResponse.json(
      { error: "Failed to generate script" },
      { status: 500 }
    );
  }
}

