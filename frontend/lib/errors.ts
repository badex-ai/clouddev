/**
 * Error handling utilities for the frontend.
 *
 * Toast messages: ALWAYS show consumer-friendly messages (all environments)
 * Console logs: Show technical details in development only
 */

// Environment check - dev shows technical errors in console
const ENVIRONMENT = process.env.ENVIRONMENT || process.env.NODE_ENV || 'development';
const IS_DEVELOPMENT = ENVIRONMENT === 'development' || ENVIRONMENT === 'dev';

/**
 * Application error with both consumer and technical messages.
 * Use this for all API and application errors.
 */
export class AppError extends Error {
  /** Consumer-friendly message (shown in staging/production) */
  public readonly userMessage: string;
  /** Technical message for developers (shown in development) */
  public readonly technicalMessage: string;
  /** Error title for toast */
  public readonly title: string;

  constructor(options: {
    title: string;
    userMessage: string;
    technicalMessage?: string;
  }) {
    // In dev, show technical message; otherwise show user message
    const displayMessage = IS_DEVELOPMENT
      ? (options.technicalMessage || options.userMessage)
      : options.userMessage;

    super(displayMessage);

    this.name = 'AppError';
    this.title = options.title;
    this.userMessage = options.userMessage;
    this.technicalMessage = options.technicalMessage || options.userMessage;
  }
}

/**
 * Get user-friendly error message for toast display.
 * ALWAYS returns consumer-friendly messages (in all environments).
 * Technical details are logged to console in development only.
 */
export function getErrorMessage(error: unknown): string {
  // Log technical details to console in development
  if (IS_DEVELOPMENT) {
    console.error('[Error Details]', error);
  }

  // Handle AppError - return user-friendly message
  if (error instanceof AppError) {
    return error.userMessage;
  }

  // Handle standard Error - return generic message
  if (error instanceof Error) {
    return 'Something went wrong. Please try again.';
  }

  // Handle string errors - return generic message
  if (typeof error === 'string') {
    return 'Something went wrong. Please try again.';
  }

  // Fallback
  return 'An unexpected error occurred. Please try again.';
}

/**
 * Get error title for toast display
 */
export function getErrorTitle(error: unknown): string {
  if (error instanceof AppError) {
    return error.title;
  }
  return 'Error';
}

/**
 * Default consumer-friendly error messages for common scenarios.
 * Use these instead of technical messages.
 */
export const ErrorMessages = {
  // Network errors
  NETWORK_ERROR: 'Unable to connect to the server. Please check your internet connection and try again.',
  TIMEOUT: 'The request took too long. Please try again.',

  // Auth errors
  AUTH_FAILED: 'Authentication failed. Please log in again.',
  SESSION_EXPIRED: 'Your session has expired. Please log in again.',

  // Task errors
  TASK_CREATE_FAILED: 'Unable to create task. Please try again.',
  TASK_UPDATE_FAILED: 'Unable to update task. Please try again.',
  TASK_DELETE_FAILED: 'Unable to delete task. Please try again.',

  // Family member errors
  MEMBER_CREATE_FAILED: 'Unable to add family member. Please try again.',
  MEMBER_UPDATE_FAILED: 'Unable to update family member. Please try again.',
  MEMBER_DEACTIVATE_FAILED: 'Unable to deactivate family member. Please try again.',
  MEMBER_REACTIVATE_FAILED: 'Unable to reactivate family member. Please try again.',

  // Generic errors
  GENERIC_ERROR: 'Something went wrong. Please try again.',
  VALIDATION_ERROR: 'Please check your input and try again.',
} as const;

/**
 * Create an AppError from an API response.
 * The backend sends { code, message } where message is already consumer-friendly.
 */
export function createApiError(
  title: string,
  apiMessage: string,
  technicalDetails?: string
): AppError {
  return new AppError({
    title,
    userMessage: apiMessage, // Backend already sends consumer-friendly message
    technicalMessage: technicalDetails || apiMessage,
  });
}
