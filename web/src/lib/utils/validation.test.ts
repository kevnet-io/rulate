import { describe, expect, it } from "vitest";

import {
  compose,
  email,
  max,
  maxLength,
  min,
  minLength,
  oneOf,
  pattern,
  required,
  url,
  type ValidationRule,
  validateForm,
} from "./validation";

describe("utils/validation", () => {
  it("required validates empty values", () => {
    const rule = required("Required");
    expect(rule(undefined)).toBe("Required");
    expect(rule(null)).toBe("Required");
    expect(rule("")).toBe("Required");
    expect(rule("ok")).toBeUndefined();
  });

  it("minLength validates length", () => {
    const rule = minLength(3);
    expect(rule("")).toBeUndefined();
    expect(rule("ab")).toBe("Must be at least 3 characters");
    expect(rule("abc")).toBeUndefined();
  });

  it("maxLength validates length", () => {
    const rule = maxLength(3);
    expect(rule("")).toBeUndefined();
    expect(rule("abcd")).toBe("Must be no more than 3 characters");
    expect(rule("abc")).toBeUndefined();
  });

  it("pattern validates matching", () => {
    const rule = pattern(/^\d+$/, "Digits only");
    expect(rule("")).toBeUndefined();
    expect(rule("abc")).toBe("Digits only");
    expect(rule("123")).toBeUndefined();
  });

  it("email validates format", () => {
    const rule = email();
    expect(rule("")).toBeUndefined();
    expect(rule("not-an-email")).toBe("Invalid email address");
    expect(rule("a@b.com")).toBeUndefined();
  });

  it("min/max validate numeric range", () => {
    expect(min(5)(4)).toBe("Must be at least 5");
    expect(min(5)(5)).toBeUndefined();
    expect(max(5)(6)).toBe("Must be no more than 5");
    expect(max(5)(5)).toBeUndefined();
  });

  it("url validates URL", () => {
    const rule = url("Bad URL");
    expect(rule("")).toBeUndefined();
    expect(rule("notaurl")).toBe("Bad URL");
    expect(rule("https://example.com")).toBeUndefined();
  });

  it("oneOf validates allowed values", () => {
    const rule = oneOf<string>(["a", "b", "c"]);
    expect(rule("a")).toBeUndefined();
    expect(rule("z")).toContain("Must be one of:");
  });

  it("compose returns first error", () => {
    const rule = compose(required("Required"), minLength(3, "Too short"));
    expect(rule("")).toBe("Required");
    expect(rule("ab")).toBe("Too short");
    expect(rule("abc")).toBeUndefined();
  });

  it("validateForm returns per-field errors", () => {
    const values = { name: "", email: "not-an-email" };
    const errors = validateForm(values, {
      name: required("Name required"),
      email: [required("Email required"), email("Email invalid")],
    });
    expect(errors).toEqual({ name: "Name required", email: "Email invalid" });
  });

  it("validateForm skips fields with undefined rules", () => {
    const values = { name: "ok" };
    const rules: Partial<Record<keyof typeof values, ValidationRule<string>>> =
      {
        name: undefined,
      };
    const errors = validateForm(values, rules);
    expect(errors).toEqual({});
  });

  it("validateForm handles single-rule success and failure", () => {
    const valuesOk = { name: "ok" };
    const valuesBad = { name: "" };

    expect(validateForm(valuesOk, { name: required("Name required") })).toEqual(
      {},
    );
    expect(
      validateForm(valuesBad, { name: required("Name required") }),
    ).toEqual({ name: "Name required" });
  });

  it("validateForm handles array-rule success without errors", () => {
    const values = { name: "abc" };
    const errors = validateForm(values, {
      name: [required("Name required"), minLength(3, "Too short")],
    });
    expect(errors).toEqual({});
  });
});
