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
    const contextStr = Object.keys(context).length > 0
      ? ` ${JSON.stringify(context)}`
      : '';
    return `[${timestamp}] ${level.toUpperCase()} ${event}${contextStr}`;
  }

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
  debug: (event: string, context?: LogContext) => log('debug', event, context),
  info: (event: string, context?: LogContext) => log('info', event, context),
  warn: (event: string, context?: LogContext) => log('warn', event, context),
  error: (event: string, context?: LogContext) => log('error', event, context),
};
