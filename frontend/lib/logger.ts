/**
 * Server-side logger for Next.js
 * Outputs JSON logs for CloudWatch in staging/production
 * Pretty console logs in development
 *
 * Usage:
 *   import { logger } from '@/lib/logger';
 *   logger.info('user_action', { userId: '123', action: 'created_task' });
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogContext {
  [key: string]: unknown;
}

const ENVIRONMENT = process.env.ENVIRONMENT || process.env.NODE_ENV || 'development';
const SERVICE_NAME = 'kaban-frontend';

// Only log debug in development
const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

const MIN_LOG_LEVEL = ENVIRONMENT === 'development' ? 'debug' : 'info';

function shouldLog(level: LogLevel): boolean {
  return LOG_LEVELS[level] >= LOG_LEVELS[MIN_LOG_LEVEL];
}

function formatLogEntry(level: LogLevel, event: string, context: LogContext = {}) {
  const timestamp = new Date().toISOString();

  if (ENVIRONMENT === 'development') {
    // Pretty console output for development
    const contextStr = Object.keys(context).length > 0
      ? ` ${JSON.stringify(context)}`
      : '';
    return `[${timestamp}] ${level.toUpperCase()} ${event}${contextStr}`;
  }

  // JSON output for CloudWatch (staging/production)
  return JSON.stringify({
    timestamp,
    level,
    event,
    service: SERVICE_NAME,
    environment: ENVIRONMENT,
    ...context,
  });
}

function log(level: LogLevel, event: string, context: LogContext = {}) {
  if (!shouldLog(level)) return;

  const message = formatLogEntry(level, event, context);

  switch (level) {
    case 'debug':
      console.debug(message);
      break;
    case 'info':
      console.info(message);
      break;
    case 'warn':
      console.warn(message);
      break;
    case 'error':
      console.error(message);
      break;
  }
}

export const logger = {
  /**
   * Debug level - only shown in development
   * Use for detailed debugging info
   */
  debug: (event: string, context?: LogContext) => log('debug', event, context),

  /**
   * Info level - shown in staging and production
   * Use for: user actions, API calls, business events
   */
  info: (event: string, context?: LogContext) => log('info', event, context),

  /**
   * Warning level - shown in staging and production
   * Use for: slow operations, retry attempts, deprecation notices
   */
  warn: (event: string, context?: LogContext) => log('warn', event, context),

  /**
   * Error level - shown in staging and production
   * Use for: exceptions, failed API calls, auth failures
   */
  error: (event: string, context?: LogContext) => log('error', event, context),
};

// What to log in the frontend:
//
// INFO:
//   - auth_login_success, auth_logout
//   - api_call_success (action name, duration)
//   - page_rendered (for server components)
//
// WARN:
//   - api_call_slow (>2s)
//   - auth_session_refresh
//
// ERROR:
//   - api_call_failed (action name, error code, message)
//   - auth_error
//   - unhandled_error
