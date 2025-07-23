# LinkedIn Agent Frontend

A React-based admin dashboard for managing LinkedIn scraping operations with authentication, team management, and credit tracking.

## Features

- **Authentication**: Secure login with Supabase Auth
- **Admin Protection**: Role-based access control for admin users
- **Teams Management**: View and paginate through teams
- **Credits Tracking**: Monitor remaining API credits
- **Responsive Design**: Modern UI with clean styling
- **Storybook**: Component documentation and testing

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```bash
VITE_SUPABASE_URL=your-supabase-project-url
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
VITE_API_BASE=http://localhost:8000
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

Create a production build:
```bash
npm run build
```

### Testing and Documentation

Run Storybook for component documentation:
```bash
npm run storybook
```

Run linting:
```bash
npm run lint
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Form.tsx        # Dynamic form component
│   ├── Table.tsx       # Generic table component
│   ├── Pagination.tsx  # Pagination controls
│   └── RequireAdmin.tsx # Auth guard component
├── pages/              # Route components
│   ├── Login.tsx       # Authentication page
│   ├── Teams.tsx       # Teams management
│   └── Credits.tsx     # Credits dashboard
├── App.tsx             # Main app component
├── App.css             # Global styles
└── supabaseClient.ts   # Supabase configuration
```

## Components

### Form
Generic form component that renders inputs based on field definitions.

### Table
Reusable table component with type-safe column definitions.

### Pagination
Pagination controls with previous/next navigation.

### RequireAdmin
Authentication guard that protects routes requiring admin access.

## Available Pages

- `/login` – Admin login page
- `/teams` – Team management (admin only)
- `/credits` – Credit balance tracking (admin only)

The admin pages require that the logged in user has the `admin` role in their Supabase account metadata.

## Recent Improvements

1. **Fixed Storybook Hook Error**: Resolved React hooks usage in Storybook stories
2. **Enhanced Styling**: Added comprehensive CSS with modern design patterns
3. **Improved UX**: Added loading states, error handling, and better navigation
4. **Type Safety**: Strengthened TypeScript usage throughout components
5. **Code Quality**: Fixed all linting issues and improved code organization
6. **Authentication Flow**: Enhanced auth state management and error handling

## Environment Configuration

The frontend requires the following environment variables:

- `VITE_SUPABASE_URL`: Your Supabase project URL
- `VITE_SUPABASE_ANON_KEY`: Your Supabase anonymous key
- `VITE_API_BASE`: Backend API base URL (default: http://localhost:8000)

## Technologies Used

- **React 19**: Modern React with hooks
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **React Router**: Client-side routing
- **Supabase**: Authentication and database
- **Storybook**: Component documentation
- **ESLint**: Code linting and quality

## Contributing

1. Follow the existing code style
2. Add Storybook stories for new components
3. Ensure all linting passes before committing
4. Update documentation for new features
