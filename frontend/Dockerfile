# =============================================================================
# Dita AI Assistant - Frontend Dockerfile (Multi-stage)
# React 19 + Vite + Tailwind CSS + Nginx
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Build React application
# -----------------------------------------------------------------------------
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --silent

# Copy application code
COPY . .

# Build arguments for environment variables
ARG VITE_WEBSOCKET_URL=ws://localhost:8000/ws/dashboard
ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_RECONNECT_INTERVAL=3000
ARG VITE_PING_INTERVAL=30000

# Set environment variables for build
ENV VITE_WEBSOCKET_URL=$VITE_WEBSOCKET_URL \
    VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_RECONNECT_INTERVAL=$VITE_RECONNECT_INTERVAL \
    VITE_PING_INTERVAL=$VITE_PING_INTERVAL

# Build the application
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Nginx server for production
# -----------------------------------------------------------------------------
FROM nginx:alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create nginx user for security
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Add health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
