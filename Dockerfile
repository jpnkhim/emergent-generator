# Multi-stage build for Koyeb deployment

FROM node:18 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install
COPY frontend/ ./
RUN yarn build

FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY backend/ /app/backend/
WORKDIR /app/backend

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend build
COPY --from=frontend-build /app/frontend/build /app/frontend/build

# Create nginx config
RUN echo 'server {\n\
    listen 8000;\n\
    server_name _;\n\
    \n\
    # Frontend\n\
    location / {\n\
        root /app/frontend/build;\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    \n\
    # Backend API\n\
    location /api {\n\
        proxy_pass http://localhost:8001;\n\
        proxy_http_version 1.1;\n\
        proxy_set_header Upgrade $http_upgrade;\n\
        proxy_set_header Connection "upgrade";\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
    }\n\
}' > /etc/nginx/sites-available/default

# Create supervisor config
RUN echo '[supervisord]\n\
nodaemon=true\n\
\n\
[program:backend]\n\
command=uvicorn server:app --host 0.0.0.0 --port 8001\n\
directory=/app/backend\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
\n\
[program:nginx]\n\
command=nginx -g "daemon off;"\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
' > /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
