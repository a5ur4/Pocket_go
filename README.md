# Pocket GO 🏨

A comprehensive hotel and accommodation finder application with a RESTful API and Telegram bot interface. Pocket GO helps users discover hotels, hostels, pousadas, resorts, and other accommodations near their location.

> **Note**: The project repository is named `Pocket_go` (with underscore) while the application is branded as "Pocket GO" (with space).

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Telegram Bot](#telegram-bot)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [License](#license)
- [Contributing](#contributing)

## ✨ Features

- **Location-based Search**: Find accommodations near your location using geographic coordinates
- **Multiple Accommodation Types**: Support for hotels, hostels, pousadas, resorts, apartments, and motels
- **RESTful API**: Comprehensive FastAPI-based API for managing accommodations, users, and evaluations
- **Telegram Bot**: User-friendly Telegram interface for searching accommodations
- **Multi-language Support**: Available in Portuguese and English
- **User Reviews**: Evaluation and rating system for accommodations
- **Search History**: Track user searches and preferences
- **Detailed Hotel Information**: Access comprehensive details about each accommodation
- **City Management**: Organize accommodations by cities
- **Request Logging**: Middleware for logging API requests and errors

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with PostGIS extension
- **Bot**: python-telegram-bot
- **ORM**: SQLAlchemy with GeoAlchemy2 for geographic data
- **Testing**: pytest
- **Containerization**: Docker & Docker Compose
- **Web Server**: Uvicorn

## 📦 Prerequisites

- Python 3.8+
- PostgreSQL 16+ with PostGIS 3.4+
- Docker and Docker Compose (optional, for containerized setup)
- Telegram Bot Token (for bot functionality)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/a5ur4/Pocket_go.git
cd Pocket_go
```

### 2. Set Up Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Database

#### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

This will start a PostgreSQL database with PostGIS extension on the port specified in your environment variables.

#### Manual Setup

If you prefer to set up PostgreSQL manually:

1. Install PostgreSQL 16+ and PostGIS 3.4+
2. Create a database for the application
3. Enable the PostGIS extension:

```sql
CREATE EXTENSION postgis;
```

## ⚙️ Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_NAME=pocket_go

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# API Configuration
API_BASE_URL=http://localhost:8000
```

## 🏃 Running the Application

### Start the API Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Access API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Start the Telegram Bot

```bash
python bot/telegram_bot.py
```

## 📚 API Documentation

### Main Endpoints

#### Health Check
- `GET /` - Welcome message
- `GET /health` - Health status

#### Users
- Managed through `/users` routes
- User registration and management

#### Cities
- `GET /cities` - List all cities
- `POST /cities` - Create a new city
- Additional CRUD operations available

#### Hotels
- `GET /hotels` - List all hotels
- `POST /hotels` - Create a new hotel
- `GET /hotels/{id}` - Get hotel details
- Additional filtering and search options

#### Hotel Details
- Extended information about accommodations
- Amenities, photos, and additional metadata

#### Evaluations
- User reviews and ratings for hotels
- `POST /evaluations` - Submit a review
- `GET /evaluations` - List evaluations

#### User Searches
- Track and manage user search history
- Analytics and preferences

#### Logs
- System logs and request history
- Monitoring and debugging

### Request Logging

All API requests are automatically logged through the `LoggingMiddleware`, which captures:
- Request details (method, path, headers)
- Response information
- Error tracking
- Timestamps

## 🤖 Telegram Bot

### Features

- **Location Sharing**: Send your location to find nearby accommodations
- **Accommodation Type Filter**: Choose specific types (hotel, hostel, etc.)
- **Multi-language**: Supports Portuguese and English
- **Interactive Buttons**: User-friendly keyboard navigation
- **Detailed Results**: View accommodation information directly in Telegram

### Bot Commands

- `/start` - Initialize the bot and get instructions
- `/help` - Get help on how to use the bot
- `/lang` - Set your preferred language (pt/en)
- `/type` - Choose a specific accommodation type

### Usage

1. Start a chat with your bot on Telegram
2. Send `/start` to initialize
3. Share your location or use commands to search
4. Browse results and get details

## 🧪 Testing

The project uses pytest for testing.

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Exclude slow tests
pytest -m "not slow"
```

### Test Configuration

Test settings are configured in `pytest.ini`. Tests are organized in the `tests/` directory.

## 📁 Project Structure

```
Pocket_go/
├── bot/                    # Telegram bot implementation
│   ├── telegram_bot.py    # Main bot logic
│   └── lang_texts.py      # Multi-language text resources
├── database/              # Database configuration
│   └── engine_db.py       # SQLAlchemy engine setup
├── middleware/            # API middleware
│   └── logging_middleware.py
├── models/                # SQLAlchemy models
│   ├── users_model.py
│   ├── cities_model.py
│   ├── hotels_model.py
│   ├── hotel_details_model.py
│   ├── evaluations_model.py
│   ├── user_searches_model.py
│   └── logs_model.py
├── routes/                # API route handlers
│   ├── users_routes.py
│   ├── cities_routes.py
│   ├── hotels_routes.py
│   ├── hotel_details_routes.py
│   ├── evaluations_routes.py
│   ├── user_searches_routes.py
│   └── logs_routes.py
├── services/              # Business logic layer
│   ├── users_service.py
│   ├── cities_service.py
│   ├── hotels_service.py
│   ├── hotel_details_service.py
│   ├── evaluations_service.py
│   ├── user_searches_service.py
│   └── logs_service.py
├── tests/                 # Test suite
├── utils/                 # Utility functions
├── main.py               # FastAPI application entry point
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker configuration
├── pytest.ini           # Pytest configuration
└── .env                 # Environment variables (create this)
```

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For support, please open an issue in the GitHub repository.

---

**Version**: 1.0.1