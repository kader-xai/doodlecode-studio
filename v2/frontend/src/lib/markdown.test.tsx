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

  it("renders task-list checkboxes, checked + unchecked (iter 201)", () => {
    const html = toHtml("- [ ] todo\n- [x] done");
    expect((html.match(/<input[^>]*type="checkbox"/g) ?? []).length).toBe(2);
    expect(html).toContain("checked"); // the [x] item
    expect(html).toContain("todo");
    expect(html).toContain("done");
  });

  it("accepts capital [X] and strikes through done items (iter 201)", () => {
    const html = toHtml("- [X] finished");
    expect(html).toContain("checkbox");
    expect(html).toContain("line-through");
  });

  it("mixes task and plain bullets in one list (iter 201)", () => {
    const html = toHtml("- plain\n- [ ] task");
    expect(html).toContain("<ul");
    expect((html.match(/<li/g) ?? []).length).toBe(2);
    expect((html.match(/type="checkbox"/g) ?? []).length).toBe(1);
  });

  it("renders ordered lists with a start offset (iter 186)", () => {
    const html = toHtml("1. first\n2. second\n3. third");
    expect(html).toContain("<ol");
    expect((html.match(/<li/g) ?? []).length).toBe(3);
    const off = toHtml("3. c\n4. d");
    expect(off).toContain('start="3"');
  });

  it("accepts `1)` ordered-list style and keeps it off paragraphs (iter 186)", () => {
    const html = toHtml("intro line\n\n1) a\n2) b");
    expect(html).toContain("<ol");
    expect(html).toContain("<p");
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

  it("renders a table with a header and body rows (iter 196)", () => {
    const html = toHtml("| A | B |\n| --- | --- |\n| 1 | 2 |\n| 3 | 4 |");
    expect(html).toContain("<table");
    expect((html.match(/<th[\s>]/g) ?? []).length).toBe(2); // not <thead
    expect((html.match(/<tr[\s>]/g) ?? []).length).toBe(3); // 1 header + 2 body
    expect((html.match(/<td/g) ?? []).length).toBe(4);
    expect(html).toContain(">A</th>");
    expect(html).toContain(">4</td>");
  });

  it("honors per-column alignment from the separator (iter 196)", () => {
    const html = toHtml("| L | C | R |\n| :-- | :-: | --: |\n| a | b | c |");
    expect(html).toContain("text-align:left");
    expect(html).toContain("text-align:center");
    expect(html).toContain("text-align:right");
  });

  it("renders inline formatting inside table cells (iter 196)", () => {
    const html = toHtml("| Col |\n| --- |\n| **bold** |");
    expect(html).toContain("<strong>bold</strong>");
  });

  it("does not treat a lone pipe line as a table (iter 196)", () => {
    const html = toHtml("a | b without a separator row");
    expect(html).not.toContain("<table");
    expect(html).toContain("<p");
  });

  it("pads short body rows to the header column count (iter 196)", () => {
    const html = toHtml("| A | B |\n| --- | --- |\n| only-one |");
    expect(html).toContain("<table");
    // header defines 2 columns, so the short row still emits 2 <td>.
    expect((html.match(/<td/g) ?? []).length).toBe(2);
  });

  it("renders a fenced code block verbatim (iter 197)", () => {
    const html = toHtml("```\nx = 1\ny = 2\n```");
    expect(html).toContain("<pre");
    expect(html).toContain("<code");
    expect(html).toContain("x = 1\ny = 2");
  });

  it("does not parse markdown inside a fenced block (iter 197)", () => {
    const html = toHtml("```\n**not bold** and `not code`\n```");
    expect(html).not.toContain("<strong>");
    expect(html).toContain("**not bold**");
  });

  it("keeps a language tag from the opening fence (iter 197)", () => {
    const html = toHtml("```python\nprint(1)\n```");
    expect(html).toContain('data-lang="python"');
  });

  it("closes an unterminated fence at end of source (iter 197)", () => {
    const html = toHtml("```\nstuck open");
    expect(html).toContain("<pre");
    expect(html).toContain("stuck open");
  });

  it("does not treat fence content as a heading (iter 197)", () => {
    const html = toHtml("```\n# not a heading\n```");
    expect(html).not.toContain("<h1");
    expect(html).toContain("# not a heading");
  });
});
