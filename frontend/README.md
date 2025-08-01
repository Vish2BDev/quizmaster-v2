# Quiz Master V2 - Frontend

This directory contains the Vue 3 CLI application for the Quiz Master V2 frontend.

## Setup Instructions

1. Install Node.js (v16 or higher)
2. Install Vue CLI: `npm install -g @vue/cli`
3. Navigate to this directory: `cd frontend`
4. Install dependencies: `npm install`
5. Start development server: `npm run serve`
6. Build for production: `npm run build`

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/                    # Source code
│   ├── components/         # Vue components
│   ├── views/             # Page components
│   ├── router/            # Vue Router configuration
│   ├── store/             # Vuex store
│   ├── assets/            # Images, styles, etc.
│   └── main.js            # Application entry point
├── package.json           # Dependencies and scripts
└── vue.config.js          # Vue CLI configuration
```

## Development

- Development server runs on: http://localhost:8080
- API backend should be running on: http://localhost:5000 