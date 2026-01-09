import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(value: number): string {
  if (value === 0) return '₹0'
  
  const absValue = Math.abs(value)
  
  if (absValue >= 10000000) {
    return `₹${(value / 10000000).toFixed(1)}Cr`
  } else if (absValue >= 100000) {
    return `₹${(value / 100000).toFixed(1)}L`
  } else if (absValue >= 1000) {
    return `₹${(value / 1000).toFixed(1)}K`
  } else {
    return `₹${value.toFixed(0)}`
  }
}

export function formatCurrencyDetailed(value: number): string {
  return `₹${value.toLocaleString('en-IN', { maximumFractionDigits: 2, minimumFractionDigits: 2 })}`
}

