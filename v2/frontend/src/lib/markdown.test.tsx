import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { renderMarkdown } from "./markdown";

/** Render the JSX array to a string so we can assert on the HTML. */
function toHtml(src: string): string {
  return renderToStaticMarkup(<>{renderMarkdown(src)}</>);
}

describe("renderMarkdown", () => {
  it("renders headings 1-3", () => {
    expect(toHtml("# Big")).toContain("<h1");
    expect(toHtml("## Mid")).toContain("<h2");
    expect(toHtml("### Small")).toContain("<h3");
  });

  it("renders bullet lists", () => {
    const html = toHtml("- one\n- two");
    expect(html).toContain("<ul");
    expect((html.match(/<li/g) ?? []).length).toBe(2);
  });

  it("renders **bold** and `inline code`", () => {
    const html = toHtml("**bold** and `code`");
    expect(html).toContain("<strong>bold</strong>");
    expect(html).toContain("<code");
  });

  it("renders blockquote", () => {
    const html = toHtml("> quoted");
    expect(html).toContain("<blockquote");
  });

  it("renders horizontal rule", () => {
    const html = toHtml("---");
    expect(html).toContain("<hr");
  });

  it("renders *italic* without confusing it with **bold** (iter 138)", () => {
    const html = toHtml("an *emphasized* word");
    expect(html).toContain("<em");
    expect(html).toContain("emphasized");
    // Double-star bold must collapse to <strong>, not <em>.
    const boldHtml = toHtml("**strong**");
    expect(boldHtml).toContain("<strong>strong</strong>");
    expect(boldHtml).not.toContain("<em");
  });

  it("renders a [text](url) link, new tab + noopener (iter 185)", () => {
    const html = toHtml("see [the docs](https://example.com/x)");
    expect(html).toContain('href="https://example.com/x"');
    expect(html).toContain('target="_blank"');
    expect(html).toContain("noopener");
    expect(html).toContain(">the docs</a>");
  });

  it("allows mailto and relative links (iter 185)", () => {
    expect(toHtml("[mail](mailto:a@b.com)")).toContain('href="mailto:a@b.com"');
    expect(toHtml("[anchor](#section)")).toContain('href="#section"');
  });

  it("refuses a javascript: href and leaves it literal (iter 185)", () => {
    const html = toHtml("[x](javascript:alert(1))");
    expect(html).not.toContain("<a");
    expect(html).toContain("[x](javascript:alert(1))");
  });
});
