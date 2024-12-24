# Vue FastAPI Admin - Property Management System

A modern property management system based on Vue 3 and FastAPI.

## Features

- 🏠 Community Management
  - Filter communities by city
  - Maintain community basic information
  - Support multi-city data management

- 🏢 Second-hand Housing Management
  - Property information entry and management
  - Multi-dimensional filtering by community, price, area, etc.
  - Automatic unit price calculation

- 👥 User Permission Management
  - Role-based access control
  - Complete user management functionality
  - Operation audit logging

## Tech Stack

### Backend
- FastAPI
- Tortoise ORM
- SQLite
- Python 3.8+

### Frontend
- Vue 3
- Naive UI
- Pinia
- Vue Router

## Quick Start

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python fix_db.py

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 9999 --reload
```

### Frontend Setup

```bash
cd web

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Project Structure

```
.
├── app/                    # Backend code
│   ├── api/               # API routes
│   ├── models/            # Data models
│   ├── schemas/           # Data validation
│   └── core/             # Core functionality
├── web/                   # Frontend code
│   ├── src/              
│   │   ├── views/        # Page components
│   │   ├── components/   # Common components
│   │   ├── stores/       # State management
│   │   └── api/         # API calls
└── tests/                # Test code
```

## Development Guide

1. Adding a New Community:
   - Select city
   - Fill in community basic information
   - Submit and save

2. Adding a New Property:
   - Select the community
   - Fill in property details
   - System automatically calculates unit price

## License

[MIT License](LICENSE)