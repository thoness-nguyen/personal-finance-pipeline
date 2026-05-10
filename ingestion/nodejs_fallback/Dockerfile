# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM node:22-alpine AS builder
WORKDIR /app

# Install all deps (including devDeps needed for tsc)
COPY package*.json tsconfig.json ./
RUN npm ci

# Copy source and compile TypeScript → dist/
COPY src/ ./src/
RUN npm run build

# ── Stage 2: Production ───────────────────────────────────────────────────────
FROM node:22-alpine
WORKDIR /app

# Install production deps only
COPY package*.json ./
RUN npm ci --omit=dev

# Copy compiled output from builder stage
COPY --from=builder /app/dist ./dist

EXPOSE 3000
CMD ["node", "dist/App.js"]