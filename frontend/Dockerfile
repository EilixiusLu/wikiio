# =============================================================================
# 此 Dockerfile 仅用于本地容器化预览，不用于生产部署。
#
# 生产环境前端已改为纯静态托管（EdgeOne Pages）:
#   1. 本地/CI 执行 npm run build
#   2. 将 frontend/dist/ 上传至 EdgeOne Pages
#
# 本地预览用法:
#   docker build -t wikiio-frontend -f frontend/Dockerfile .
#   docker run -p 8080:80 wikiio-frontend
# =============================================================================

# ---- Build Stage ----
FROM node:22-alpine AS build

WORKDIR /app

# Install dependencies first (layer caching)
COPY frontend/package*.json ./
RUN npm ci

# Copy source and build
COPY frontend/ ./
RUN npm run build

# ---- Production Stage ----
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy Nginx configuration
COPY nginx/wikiio.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
