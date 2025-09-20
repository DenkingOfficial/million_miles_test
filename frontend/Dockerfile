FROM oven/bun AS build
WORKDIR /app
COPY package*.json ./
RUN bun install
COPY . .
RUN bun run build
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
