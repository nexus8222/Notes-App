

# Anonymous Chat – Real-Time Matchmaking App

A scalable, production-ready, 1-on-1 anonymous chat web app. Match instantly with a random stranger, chat in real time, and move on when you wish. Powered by Django, Channels, Redis, Docker, and Nginx.

---

## Features

- Anonymous, instant 1-on-1 matching — no registration required
- Real-time chat using WebSockets (Django Channels)
- Scalable matchmaking and chat logic with Redis
- "Next" button to get a new match at any time
- Responsive, minimal and modern UI
- Status messages for connection, disconnection, and queue events
- Secure, production-ready by default (SSL, rate limiting, secure cookies)
- Health check endpoints and Sentry-ready error tracking
- Dockerized for fast local or cloud setup

---

## Quick Start (with Docker Compose)

Clone and run with your settings:

```bash 
git clone https://github.com/nexus8222/Anonymous-Chat-App.git
cd Anonymous-Chat-App
cp .env.example .env # Edit .env to set secrets and domains
docker-compose up --build
```


- Application runs behind Nginx; visit https://localhost/ or your configured domain.
- Immediately start chatting with a stranger.

---

## Tech Stack

- Django 4+, Django Channels, ASGI
- Redis (as queue and channel layer)
- Frontend: HTML, JavaScript, CSS (with Tailwind CSS or minimalist SASS)
- Nginx (reverse proxy and static files)
- Docker, Docker Compose

---

## Production and Security

- Runs securely behind Nginx (with SSL and secure headers)
- Redis-backed for scalable queueing and channel layers
- HTTPS enforced
- CSRF and cookie security in Django settings
- Connection rate limiting configured at web/proxy layer
- Sentry or equivalent error monitoring can be added

---

## User Experience

- Responsive mobile and desktop UI
- Modern chat bubbles with timestamps
- Typing indicators (optional, see code)
- Automatic scroll to latest messages
- Intuitive status cues and reconnection handling

---

## Configuration
Copy and edit `.env.example` to `.env` with your settings:

```
DJANGO_SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
REDIS_URL=redis://redis:6379/0
```
Refer to `.env.example` for all configuration options.

---

## Deployment

- Deploy via Docker Compose, a standard VPS, or any PaaS that supports WebSockets
- To scale, increase Daphne/Uvicorn workers behind Nginx, use a managed Redis instance
- For domain/SSL, point DNS to your server and configure Nginx
- Load balancer support is available; backend is stateless except for Redis

---

## Monitoring and Logs

- Exposes health endpoints for readiness/liveness probes (for Docker/K8s)
- Logs to STDOUT (Docker compatible)
- Sentry integration via environment variable (optional)

---

## Local Development
```
pip install -r requirements.txt

Ensure local Redis is running (default port: 6379)
python manage.py migrate # If using any models
python manage.py runserver
```
Visit http://localhost:8000
text

---

## Contributing

Pull requests, feature ideas, and bug reports are welcome. Please submit via GitHub issues or PRs. Code style: Black for Python, ESLint for JS.
