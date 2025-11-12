# Quick Start Guide

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pnpm install
```

### 2. Set Up Environment Variables

Create a `.env.local` file in the root directory:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

**Get your OpenAI API key:**
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste it into `.env.local`

### 3. Run the Development Server

```bash
pnpm dev
```

The app will be available at http://localhost:3000

### 4. Create Your First Video

1. Click "Create New Video" or navigate to `/create`
2. Enter your video topic (e.g., "How to build a React app")
3. Select video style and tone
4. Set duration and target audience
5. Click "Generate Script"
6. Review and edit the script
7. Configure voice and visual settings
8. Generate your video

## 📁 Project Structure

- `/app` - Next.js app directory (pages and API routes)
- `/app/components` - React components
- `/app/components/ui` - Reusable UI components
- `/lib` - Utility functions
- `/public` - Static assets

## 🔑 API Keys Needed

### Required
- **OpenAI API Key** - For script generation

### Optional (for future features)
- **ElevenLabs API Key** - For high-quality voice synthesis
- **DALL-E API Key** - For image generation (or use OpenAI API)

## 🛠️ Development Commands

- `pnpm dev` - Start development server
- `pnpm build` - Build for production
- `pnpm start` - Start production server
- `pnpm lint` - Run ESLint

## 📝 Current Status

✅ **Completed:**
- Project setup and configuration
- UI components and layout
- Dashboard page
- Video creation wizard UI
- Script generation API

🚧 **In Progress:**
- Voice synthesis integration
- Video assembly
- Export functionality

## 🐛 Troubleshooting

### Script generation not working?
- Check that `OPENAI_API_KEY` is set in `.env.local`
- Verify your API key is valid and has credits
- Check the browser console for errors

### Port 3000 already in use?
- Change the port: `pnpm dev -- -p 3001`
- Or stop the process using port 3000

### Build errors?
- Delete `.next` folder and `node_modules`
- Run `pnpm install` again
- Run `pnpm dev`

## 📚 Next Steps

1. Test script generation with your OpenAI API key
2. Review the generated scripts
3. Wait for voice synthesis and video assembly features
4. Customize the UI to your preferences

For detailed implementation status, see `IMPLEMENTATION.md`

