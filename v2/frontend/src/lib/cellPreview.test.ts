import { describe, expect, it } from "vitest";
import { firstLine, hostOf } from "./cellPreview";

describe("firstLine", () => {
  it("returns empty for empty source", () => {
    expect(firstLine("", "code")).toBe("");
  });

  it("skips blank leading lines", () => {
    expect(firstLine("\n\n  \nhello\nworld", "code")).toBe("hello");
  });

  it("strips Python comment marker on code cells", () => {
    expect(firstLine("# load the model\nimport torch", "code")).toBe("load the model");
  });

  it("strips markdown heading marks", () => {
    expect(firstLine("### Setup\nblurb", "markdown")).toBe("Setup");
  });

  it("strips markdown bullet markers", () => {
    expect(firstLine("- item one\n- item two", "markdown")).toBe("item one");
    expect(firstLine("* item one", "markdown")).toBe("item one");
  });

  it("truncates at 60 chars with an ellipsis", () => {
    const s = "x".repeat(80);
    const out = firstLine(s, "code");
    expect(out.endsWith("…")).toBe(true);
    expect(out.length).toBe(58); // 57 chars + ellipsis
  });

  it("preserves URLs for non-markdown/non-code kinds (iter 134)", () => {
    // Browser/media sources are URLs — neither the markdown bullet
    // stripper nor the python comment stripper should fire. A URL
    // fragment '#section' must survive verbatim.
    expect(firstLine("https://example.com/page#section", "browser"))
      .toBe("https://example.com/page#section");
    expect(firstLine("*not-a-bullet", "browser")).toBe("*not-a-bullet");
  });
});

describe("hostOf", () => {
  it("returns the host without www.", () => {
    expect(hostOf("https://www.example.com/path")).toBe("example.com");
    expect(hostOf("https://example.com")).toBe("example.com");
  });

  it("handles uppercase hosts (URL normalizes them)", () => {
    expect(hostOf("https://EXAMPLE.COM")).toBe("example.com");
  });

  it("falls back to bare host when URL parsing fails", () => {
    expect(hostOf("example.com/foo")).toBe("example.com");
  });

  it("returns (blank) for empty input", () => {
    expect(hostOf("")).toBe("(blank)");
  });

  it("keeps port numbers in the host", () => {
    expect(hostOf("http://localhost:8080/dashboard")).toBe("localhost:8080");
  });
});
