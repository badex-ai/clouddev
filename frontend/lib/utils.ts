import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import { fromZonedTime,format,  toZonedTime } from 'date-fns-tz'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;

function localToUtc(localDateTime : string | number | Date) {
  if(!localDateTime) return null
  return fromZonedTime(localDateTime, userTimeZone).toISOString();
}

function utcToLocal(utcDateTime  : string | number | Date)  {
 
  const zonedDate =  toZonedTime(utcDateTime, userTimeZone, 'yyyy-MM-dd HH:mm:ss');
  return format(zonedDate, "EEE MMM dd yyyy h:mmaaa", { timeZone: userTimeZone });
}

export {utcToLocal, localToUtc} 