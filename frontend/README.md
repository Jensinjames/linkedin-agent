# Frontend Admin Dashboard

This React + TypeScript project provides an admin dashboard for the LinkedIn Agent backend.
It uses Supabase for authentication and fetches data from the FastAPI server.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```
2. Copy `.env.example` to `.env` and set your Supabase credentials and API base URL.
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Open `http://localhost:5173` in your browser.

## Storybook

Component previews are available via Storybook:

```bash
npm run storybook
```

## Available Pages

- `/login` – admin login
- `/teams` – team management (admin only)
- `/credits` – credit balance (admin only)

The admin pages require that the logged in user has the `admin` role in their Supabase account metadata.
