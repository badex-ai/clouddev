FROM node:18-alpine AS base
RUN apk add --no-cache libc6-compat curl
WORKDIR /app
COPY package.json package-lock.json ./


FROM base AS deps
RUN npm ci

FROM base AS dev
COPY --from=deps /app/node_modules ./node_modules
COPY . .

EXPOSE 3000
HEALTHCHECK --interval=60s --timeout=30s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1
CMD ["npm", "run", "dev"]


FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM base AS devk8s

RUN apk add --no-cache curl

RUN addgroup --system --gid 1001 appgroup && \
  adduser --system --uid 1001 appuser --ingroup appgroup

COPY --from=builder /app/public ./public

RUN mkdir .next && chown appuser:appgroup .next

COPY --from=builder --chown=appuser:appgroup /app/.next/standalone ./
COPY --from=builder --chown=appuser:appgroup /app/.next/static ./.next/static

USER appuser
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://frontend.local/ || exit 1

CMD ["node", "server.js"]

FROM base AS staging

RUN apk add --no-cache curl

RUN addgroup --system --gid 1001 appgroup && \
  adduser --system --uid 1001 appuser --ingroup appgroup

COPY --from=builder /app/public ./public

RUN mkdir .next && chown appuser:appgroup .next

COPY --from=builder --chown=appuser:appgroup /app/.next/standalone ./
COPY --from=builder --chown=appuser:appgroup /app/.next/static ./.next/static

USER appuser
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1

CMD ["node", "server.js"]

# Production stage
FROM base AS production

RUN apk add --no-cache curl

RUN addgroup --system --gid 1001 appgroup && \
  adduser --system --uid 1001 appuser --ingroup appgroup

COPY --from=builder /app/public ./public

RUN mkdir .next && chown appuser:appgroup .next

COPY --from=builder --chown=appuser:appgroup /app/.next/standalone ./
COPY --from=builder --chown=appuser:appgroup /app/.next/static ./.next/static

USER appuser
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1

CMD ["node", "server.js"]

