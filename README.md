# YouTube Video Generator

AI-powered YouTube video generation application built with Next.js, TypeScript, and Tailwind CSS.

## Features

- 🤖 AI-powered script generation
- 🎙️ High-quality voice synthesis
- 🎨 Visual content generation
- 🎬 Automated video assembly
- 📊 Project management
- 🎯 SEO-optimized content

## Getting Started

### Prerequisites

- Node.js 18+ 
- pnpm (package manager)

### Installation

1. Install dependencies:
```bash
pnpm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
```

Edit `.env.local` and add your API keys:
- `OPENAI_API_KEY` - Required for script generation

3. Run the development server:
```bash
pnpm dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
/app
  /api              - API routes
  /components       - React components
    /ui             - Reusable UI components
    /dashboard      - Dashboard components
    /video-creation - Video creation components
  /lib              - Utility functions
  /app              - Next.js pages
```

## Usage

1. Navigate to the Dashboard
2. Click "Create New Video"
3. Enter your topic and configure settings
4. Review and edit the generated script
5. Generate your video with voice and visuals
6. Download or export your video

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI + Custom components
- **AI**: OpenAI GPT-4
- **Voice**: OpenAI TTS / ElevenLabs (optional)
- **Video Processing**: FFmpeg (to be integrated)

## Development

- `pnpm dev` - Start development server
- `pnpm build` - Build for production
- `pnpm start` - Start production server
- `pnpm lint` - Run ESLint

## Roadmap

- [x] Project setup and UI foundation
- [x] Script generation
- [ ] Voice synthesis integration
- [ ] Image/video generation
- [ ] Video assembly with FFmpeg
- [ ] Thumbnail generation
- [ ] Project persistence
- [ ] Export functionality
- [ ] YouTube API integration

## License

MIT
