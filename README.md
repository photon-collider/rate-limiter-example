# FastAPI Rate Limiter Example

This project demonstrates the implementation of rate limiting in a FastAPI application using the token bucket algorithm and Redis for state management. The implementation provides practical insights into protecting API endpoints from excessive usage through a proven rate limiting approach.

For a detailed explanation of the implementation and concepts, please read the accompanying blog post: [Rate Limiting Basics with FastAPI and Redis](bryananthonio.com/blog/rate-limiting-basics)

## Overview

The application exposes a simple API endpoint (`/api/example`) that is protected by rate limiting. It uses Redis as a key-value store to track client usage and implements the token bucket algorithm for rate limiting decisions.

## Rate Limiting Configuration

The system implements a token bucket algorithm with the following parameters:

- Token replenishment rate: 2 tokens per second
- Maximum bucket capacity: 10 tokens
- Tokens required per request: 1 token

This configuration allows for brief bursts of up to 10 requests while maintaining a steady-state rate of 2 requests per second.

## Prerequisites

- Python 3.12 or higher
- Docker and Docker Compose
- uv package manager
- bash (for running the test script)

## Project Structure

```
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile           # FastAPI service container configuration
├── src/                 # Source code directory
│   ├── main.py         # FastAPI application code
│   └── request_rate_limiter.lua  # Redis Lua script for rate limiting
├── pyproject.toml       # Project dependencies and configuration
├── test_rate_limit.sh   # Test script
└── README.md           # This file
```

## Quick Start

1. Clone this repository:
   ```bash
   git clone git@github.com:photon-collider/rate-limiter-example.git
   cd rate-limiter-example
   ```

2. Start the application using Docker Compose:
   ```bash
   docker compose up
   ```

   This will start both the FastAPI application and Redis server. The service automatically configures the Redis connection using the following environment variables:
   - `REDIS_HOST=redis`
   - `REDIS_PORT=6379`

3. The API will be available at `http://localhost:8000`

## Testing the Rate Limiter

This project includes a test script that demonstrates the rate limiter in action. To run the test:

```bash
./test_rate_limit.sh
```

The script sends 20 consecutive requests to the API endpoint. You'll observe the rate limiter's behavior as requests begin to receive rejection responses (HTTP 429 status code) once they exceed the allowed rate.

Example output:
```bash
Testing rate limits on http://localhost:8000/api/example (20 requests, 0.01s delay)
----------------------------------------
Request 1: Status 200  # Successful request
...
Request 11: Status 429 # Rate limit exceeded
...
```

## Development

This project uses the uv package manager for dependency management. The dependencies and project configuration are specified in `pyproject.toml`.

## Stopping the Application

To stop the application and clean up Docker resources:

```bash
docker compose down
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.