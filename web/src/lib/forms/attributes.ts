/**
 * Form attribute utilities for handling type conversion and formatting
 * Extracted from page components for testability
 */

import type { Dimension } from "$lib/api/client";

/**
 * Convert and update an attribute value based on dimension type
 * Handles type conversion for integer, float, boolean, list, enum, and string types
 */
export function updateAttribute(
  attributes: Record<string, unknown>,
  key: string,
  value: unknown,
  dimension: Dimension,
): Record<string, unknown> {
  const updated = { ...attributes };

  if (dimension.type === "integer") {
    const numericValue =
      typeof value === "string" ? value : String(value ?? "");
    updated[key] = numericValue === "" ? 0 : parseInt(numericValue, 10);
  } else if (dimension.type === "float") {
    const numericValue =
      typeof value === "string" ? value : String(value ?? "");
    updated[key] = numericValue === "" ? 0 : parseFloat(numericValue);
  } else if (dimension.type === "boolean") {
    updated[key] = value;
  } else if (dimension.type === "list") {
    // Parse comma-separated values
    const listValue = typeof value === "string" ? value : String(value ?? "");
    const items = listValue
      .split(",")
      .map((v: string) => v.trim())
      .filter((v: string) => v);

    // Convert based on item_type
    if (dimension.item_type === "integer") {
      updated[key] = items.map((v: string) => parseInt(v, 10));
    } else if (dimension.item_type === "float") {
      updated[key] = items.map((v: string) => parseFloat(v));
    } else if (dimension.item_type === "boolean") {
      updated[key] = items.map((v: string) => v.toLowerCase() === "true");
    } else {
      updated[key] = items;
    }
  } else {
    updated[key] = value;
  }

  return updated;
}

/**
 * Get a list value as a comma-separated string for form display
 */
export function getListValueAsString(
  attributes: Record<string, unknown>,
  key: string,
): string {
  const value = attributes[key];
  if (Array.isArray(value)) {
    return value.map((v) => String(v)).join(", ");
  }
  return "";
}

/**
 * Initialize default attribute values based on schema dimensions
 */
export function initializeAttributes(
  dimensions: Dimension[],
): Record<string, unknown> {
  const attributes: Record<string, unknown> = {};

  for (const dim of dimensions) {
    if (dim.type === "boolean") {
      attributes[dim.name] = false;
    } else if (dim.type === "list") {
      attributes[dim.name] = [];
    } else if (dim.type === "integer" || dim.type === "float") {
      attributes[dim.name] = dim.min ?? 0;
    } else if (dim.type === "enum" && dim.values && dim.values.length > 0) {
      attributes[dim.name] = dim.values[0];
    } else {
      attributes[dim.name] = "";
    }
  }

  return attributes;
}
