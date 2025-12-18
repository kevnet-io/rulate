/**
 * Form validation utilities
 */

export type ValidationRule<T = unknown> = (value: T) => string | undefined;

export function required(message = "This field is required"): ValidationRule {
  return (value: unknown) => {
    if (value === undefined || value === null || value === "") {
      return message;
    }
    return undefined;
  };
}

export function minLength(
  min: number,
  message?: string,
): ValidationRule<string> {
  return (value: string) => {
    if (value && value.length < min) {
      return message || `Must be at least ${min} characters`;
    }
    return undefined;
  };
}

export function maxLength(
  max: number,
  message?: string,
): ValidationRule<string> {
  return (value: string) => {
    if (value && value.length > max) {
      return message || `Must be no more than ${max} characters`;
    }
    return undefined;
  };
}

export function pattern(
  regex: RegExp,
  message = "Invalid format",
): ValidationRule<string> {
  return (value: string) => {
    if (value && !regex.test(value)) {
      return message;
    }
    return undefined;
  };
}

export function email(
  message = "Invalid email address",
): ValidationRule<string> {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern(emailRegex, message);
}

export function min(
  minValue: number,
  message?: string,
): ValidationRule<number> {
  return (value: number) => {
    if (value !== undefined && value !== null && value < minValue) {
      return message || `Must be at least ${minValue}`;
    }
    return undefined;
  };
}

export function max(
  maxValue: number,
  message?: string,
): ValidationRule<number> {
  return (value: number) => {
    if (value !== undefined && value !== null && value > maxValue) {
      return message || `Must be no more than ${maxValue}`;
    }
    return undefined;
  };
}

export function url(message = "Invalid URL"): ValidationRule<string> {
  return (value: string) => {
    if (!value) return undefined;
    try {
      new URL(value);
      return undefined;
    } catch {
      return message;
    }
  };
}

export function oneOf<T>(options: T[], message?: string): ValidationRule<T> {
  return (value: T) => {
    if (value && !options.includes(value)) {
      return message || `Must be one of: ${options.join(", ")}`;
    }
    return undefined;
  };
}

export function compose<T>(...rules: ValidationRule<T>[]): ValidationRule<T> {
  return (value: T) => {
    for (const rule of rules) {
      const error = rule(value);
      if (error) return error;
    }
    return undefined;
  };
}

export function validateForm<T extends Record<string, unknown>>(
  values: T,
  rules: Partial<Record<keyof T, ValidationRule | ValidationRule[]>>,
): Partial<Record<keyof T, string>> {
  const errors: Partial<Record<keyof T, string>> = {};

  for (const field in rules) {
    const fieldRules = rules[field];
    const value = values[field];

    if (Array.isArray(fieldRules)) {
      const error = compose(...fieldRules)(value);
      if (error) errors[field] = error;
    } else if (fieldRules) {
      const error = fieldRules(value);
      if (error) errors[field] = error;
    }
  }

  return errors;
}
