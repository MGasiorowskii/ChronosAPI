# Chronos API

Chronos API is a simple yet efficient RESTful application for managing calendar events and conference room availability. 
The system operates in a multi-tenant model, allowing multiple companies to store their data on a central server.

## Features
- Create and retrieve conference rooms
- Create and retrieve calendar events
- Filter events by date, location, or content
- Time zone support for users
- Restrict meeting duration to a maximum of 8 hours
- Privacy protection: events are visible only to participants and room managers

## Requirements
- Python 3.10+
- Django Rest Framework
- PostgreSQL 

## Installation
To quickly set up the application, simply run the `setup.sh` script, which will install dependencies and configure the database:

```bash
chmod +x setup.sh
./setup.sh
```

## API Endpoints

| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/conference-rooms/` | Create a new conference room |
| `GET` | `/conference-rooms/` | List all conference rooms |
| `POST` | `/calendar-events/` | Create a new event |
| `GET` | `/calendar-events/?day=YYYY-MM-DD` | Retrieve events on a specific day |
| `GET` | `/calendar-events/?location_id=ID` | Retrieve events in a specific conference room |
| `GET` | `/calendar-events/?query=TEXT` | Search for events by name or agenda |

## Testing
To run unit tests:
```bash
pytest
```

## Author
This project was created as part of a recruitment task.
