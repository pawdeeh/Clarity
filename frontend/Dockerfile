FROM node:18-alpine

WORKDIR /app

# Install dependencies at build time for faster startup; use npm ci for reproducible installs
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

EXPOSE 5173

# Start Vite dev server and listen on all interfaces for container access
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
