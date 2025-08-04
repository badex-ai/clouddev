import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import {ISOStringFormat, parseISO} from 'date-fns'
import { fromZonedTime, toZonedTime } from 'date-fns-tz'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;

function localToUtc(localDateTime : string | number | Date) {
  if(!localDateTime) return null
  return fromZonedTime(localDateTime, userTimeZone).toISOString();
}

function utcToLocal(utcDateTime, timeZone) {
 
  return toZonedTime(utcDate, timeZone, 'yyyy-MM-dd HH:mm:ss');
}

export {utcToLocal, localToUtc} 