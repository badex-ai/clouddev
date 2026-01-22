import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { fromZonedTime, format, toZonedTime } from 'date-fns-tz';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;

function localToUtc(localDateTime: string | number | Date) {
  if (!localDateTime) return null;
  return fromZonedTime(localDateTime, userTimeZone).toISOString();
}

function utcToLocal(utcDateTime: string | number | Date) {
  const zonedDate = toZonedTime(utcDateTime, userTimeZone);
  return format(zonedDate, 'yyyy-MM-dd HH:mm:ss');
}

export { utcToLocal, localToUtc };

// Re-export from errors.ts for backwards compatibility
export { AppError as ApiException, ErrorMessages, getErrorMessage, getErrorTitle } from './errors';

export const NetworkError =
  'Unable to connect to the server. Please check your internet connection and try again.';
