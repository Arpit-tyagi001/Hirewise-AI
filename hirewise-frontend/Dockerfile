# ── Stage 1: Builder ──────────────────────────────────────────────────────────
# Install dependencies and build the static assets.
# Rebuilds only re-run npm install when package-lock.json changes.
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests first — maximises Docker layer cache hits
COPY package.json package-lock.json ./

RUN npm ci

# Copy the rest of the source and compile
COPY . .

RUN npm run build


# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
# Serve the compiled dist/ with a lightweight nginx image.
# No Node.js runtime, no source code, no devDependencies in the final image.
FROM nginx:1.27-alpine AS runtime

# Remove the default nginx placeholder page
RUN rm -rf /usr/share/nginx/html/*

# Copy the compiled assets from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy a custom nginx config that handles React client-side routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
