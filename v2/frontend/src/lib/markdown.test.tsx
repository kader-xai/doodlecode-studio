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
});
