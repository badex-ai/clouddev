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

export class ApiException extends Error {
  constructor(
    public title: string,
    public message: string
  ) {
    super(message);
    this.name = 'ApiException';
  }
}

export const NetworkError = 'We’re having trouble connecting to the server. Please check your internet connection or try again later.';


