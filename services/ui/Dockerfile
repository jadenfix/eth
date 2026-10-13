FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
COPY services/ui/nextjs-app/package.json services/ui/nextjs-app/package.json
COPY services/api_gateway/package.json services/api_gateway/package.json
COPY sdk/js/package.json sdk/js/package.json
RUN npm ci --ignore-scripts
COPY services/ui/nextjs-app services/ui/nextjs-app
RUN mkdir -p services/ui/nextjs-app/public && npm --workspace services/ui/nextjs-app run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production PORT=3000 HOSTNAME=0.0.0.0
RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs
COPY --from=builder --chown=nextjs:nodejs /app/services/ui/nextjs-app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/services/ui/nextjs-app/public ./services/ui/nextjs-app/public
COPY --from=builder --chown=nextjs:nodejs /app/services/ui/nextjs-app/.next/static ./services/ui/nextjs-app/.next/static
USER nextjs
EXPOSE 3000
CMD ["node", "services/ui/nextjs-app/server.js"]
