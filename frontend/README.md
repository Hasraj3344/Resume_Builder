# ResumeAI Frontend

AI-powered resume optimization platform built with React 19.

## Features

- 🎨 Modern, responsive UI with Tailwind CSS
- 🔐 JWT-based authentication
- 🤖 AI-powered resume optimization
- 📊 Real-time job matching with Adzuna API
- 📄 ATS-friendly resume export (DOCX)
- ⚡ Fast and optimized with code splitting

## Tech Stack

- **React 19.1.0** - UI library
- **React Router DOM 7.5.0** - Routing
- **Tailwind CSS 4.1.4** - Styling
- **Material-UI** - Component library
- **Axios** - HTTP client
- **Framer Motion** - Animations
- **React Hot Toast** - Notifications

## Getting Started

### Prerequisites

- Node.js 14+ and npm/yarn
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Update .env with your API URL
REACT_APP_API_URL=http://localhost:8000

# Start development server
npm start
```

The app will run on http://localhost:3000

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── components/
│   │   ├── Layout/         # Navbar, Footer, Layout
│   │   ├── Home/           # Landing page sections
│   │   ├── Auth/           # Login, Register
│   │   ├── Dashboard/      # User dashboard
│   │   ├── Profile/        # User profile
│   │   ├── Workflows/      # Manual & Adzuna workflows
│   │   ├── JobSearch/      # Job search components
│   │   ├── Generation/     # Resume generation
│   │   └── Shared/         # Reusable components
│   ├── context/
│   │   └── AuthContext.jsx # Auth state management
│   ├── services/
│   │   ├── api.js          # Axios instance
│   │   └── authService.js  # Auth API calls
│   ├── styles/
│   │   ├── global.css      # Global styles
│   │   ├── animations.css  # Animations
│   │   └── theme.js        # Design system
│   ├── App.js              # Main app with routing
│   └── index.js            # Entry point
├── package.json
├── tailwind.config.js
└── README.md
```

## Design System

### Color Palette

- **Primary**: #2563EB (Royal Blue)
- **Success**: #10B981 (Green)
- **Warning**: #F59E0B (Amber)
- **Error**: #EF4444 (Red)

### Typography

- **Headings**: Poppins (bold, semibold)
- **Body**: Inter (400, 500, 600, 700)

### Components

All reusable components are in `src/components/Shared/`:
- Button
- Card
- LoadingSpinner
- Transition

## Environment Variables

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENABLE_ANALYTICS=false
```

## Deployment

### Build for Production

```bash
npm run build
```

Output will be in `build/` directory.

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

## Contributing

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## License

Private project - All rights reserved
