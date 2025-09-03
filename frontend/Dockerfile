FROM node:18-alpine AS base
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json package-lock.json ./


FROM base AS deps
RUN npm ci

FROM base AS development
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]


FROM base AS builder
COPY --from=deps /app/node-modules ./node-modules
COPY . .
RUN npm run build


# Production stage
FROM base AS production
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 appuser --ingroup appgroup
COPY --from=builder /app/public ./public
RUN mkdir .next && chown appuser:appgroup .next
COPY --from=builder --chown=appuser:appgroup /app/.next/standalone ./
COPY --from=builder --chown=appuser:appgroup /app/.next/static ./.next/static
USER appuser
EXPOSE 3000
CMD ["node", "server.js"]

# ENV NODE_ENV=production
# ENV PORT=3000
# ENV HOSTNAME=0.0.0.0

# RUN addgroup --system --gid 1001  appgroup && \
#     adduser --system --uid 1001 appuser --ingroup appgroup

# COPY --from=builder /app/public ./public

# RUN mkdir .next 
# RUN chown appuser:appgroup .next

# COPY --from=builder --chown=appuser:appgroup /app/.next/standalone ./
# COPY --from=builder --chown=appuser:appgroup /app/.next/static ./.next/static

# EXPOSE 3000

# ENV PORT 3000

# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#   CMD curl -f http://localhost:3000/ || exit 1

# CMD ['node', 'server.js']
