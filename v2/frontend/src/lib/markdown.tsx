import { JSX } from "react";

/**
 * Minimal markdown renderer — zero dependencies, deliberately small.
 *
 * Supports:
 *   `# H1`, `## H2`, `### H3`
 *   `- item` or `* item`            (bullet list)
 *   `> blockquote`
 *   `---`                           (horizontal rule)
 *   `**bold**` and `*italic*`
 *   `` `inline code` ``
 *   `[text](url)`                   (link — http/https/mailto/relative)
 *   blank lines separate paragraphs
 *
 * We do NOT support full CommonMark (no images, tables, ordered lists,
 * fenced code). That's intentional — v1 grew a giant markdown surface
 * and most of it went unused. Add only what users ask for.
 */
export function renderMarkdown(src: string): JSX.Element[] {
  const lines = src.split("\n");
  const out: JSX.Element[] = [];
  let key = 0;
  let i = 0;

  const wrap = "break-words [overflow-wrap:anywhere]";

  while (i < lines.length) {
    const line = lines[i];

    // Blank line → spacer
    if (line.trim() === "") {
      out.push(<div key={key++} className="h-2" />);
      i++;
      continue;
    }

    // Headings
    if (/^###\s+/.test(line)) {
      out.push(
        <h3 key={key++} className={`font-hand text-2xl mt-1 ${wrap}`}>
          {renderInline(line.replace(/^###\s+/, ""))}
        </h3>,
      );
      i++;
      continue;
    }
    if (/^##\s+/.test(line)) {
      out.push(
        <h2 key={key++} className={`font-hand text-3xl mt-1 ${wrap}`}>
          {renderInline(line.replace(/^##\s+/, ""))}
        </h2>,
      );
      i++;
      continue;
    }
    if (/^#\s+/.test(line)) {
      out.push(
        <h1 key={key++} className={`font-hand text-4xl mt-1 ${wrap}`}>
          {renderInline(line.replace(/^#\s+/, ""))}
        </h1>,
      );
      i++;
      continue;
    }

    // Horizontal rule
    if (/^---+\s*$/.test(line)) {
      out.push(
        <hr key={key++} className="my-2 border-t-2 border-ink/40 dark:border-white/40" />,
      );
      i++;
      continue;
    }

    // Blockquote
    if (/^>\s+/.test(line)) {
      const quoteLines: string[] = [];
      while (i < lines.length && /^>\s+/.test(lines[i])) {
        quoteLines.push(lines[i].replace(/^>\s+/, ""));
        i++;
      }
      out.push(
        <blockquote
          key={key++}
          className={`border-l-4 border-marker-pink dark:border-[#fcc2d7] pl-3 my-1 italic font-hand text-xl ${wrap}`}
        >
          {quoteLines.map((q, j) => (
            <div key={j}>{renderInline(q)}</div>
          ))}
        </blockquote>,
      );
      continue;
    }

    // Bullet list
    if (/^[-*]\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^[-*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^[-*]\s+/, ""));
        i++;
      }
      out.push(
        <ul
          key={key++}
          className={`list-disc pl-6 font-hand text-xl leading-snug space-y-0.5 ${wrap}`}
        >
          {items.map((it, j) => (
            <li key={j}>{renderInline(it)}</li>
          ))}
        </ul>,
      );
      continue;
    }

    // Paragraph (group consecutive non-empty non-block lines)
    const para: string[] = [];
    while (
      i < lines.length &&
      lines[i].trim() !== "" &&
      !/^(#{1,3}\s|[-*]\s|>\s|---+\s*$)/.test(lines[i])
    ) {
      para.push(lines[i]);
      i++;
    }
    out.push(
      <p key={key++} className={`font-hand text-xl leading-snug ${wrap}`}>
        {renderInline(para.join(" "))}
      </p>,
    );
  }

  return out;
}

/** Iter 185: only allow safe link schemes — a `javascript:` href in
 *  user markdown would be an XSS vector. Relative links and http(s) /
 *  mailto are fine; anything else renders as plain `[text](url)`. */
function safeHref(url: string): string | null {
  const u = url.trim();
  if (/^(https?:|mailto:)/i.test(u)) return u;
  if (/^[/#.]/.test(u)) return u; // relative / anchor / fragment
  return null;
}

/** Inline pass: `[text](url)` links, **bold**, *italic*, `code`. */
function renderInline(s: string): (string | JSX.Element)[] {
  const out: (string | JSX.Element)[] = [];
  // One regex with four alternatives. Links come first so their text
  // isn't parsed as emphasis; `bold` precedes `italic` so `**x**` isn't
  // first parsed as `*` + `*x*` + `*`.
  const re = /(\[[^\]]+\]\([^)\s]+\)|\*\*[^*]+\*\*|\*[^*\n]+\*|`[^`]+`)/g;
  let last = 0;
  let m: RegExpExecArray | null;
  let key = 0;
  while ((m = re.exec(s))) {
    if (m.index > last) out.push(s.slice(last, m.index));
    const tok = m[0];
    if (tok.startsWith("[")) {
      const link = tok.match(/^\[([^\]]+)\]\(([^)\s]+)\)$/);
      const href = link ? safeHref(link[2]) : null;
      if (link && href) {
        out.push(
          <a
            key={key++}
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#1971c2] dark:text-[#74c0fc] underline decoration-2 underline-offset-2 hover:opacity-80"
          >
            {link[1]}
          </a>,
        );
      } else {
        out.push(tok); // unsafe scheme or malformed → leave as literal text
      }
    } else if (tok.startsWith("**")) {
      out.push(<strong key={key++}>{tok.slice(2, -2)}</strong>);
    } else if (tok.startsWith("`")) {
      out.push(
        <code
          key={key++}
          className="font-mono text-[0.9em] bg-marker-yellow/40 dark:bg-amber-700/40 px-1 rounded"
        >
          {tok.slice(1, -1)}
        </code>,
      );
    } else {
      out.push(<em key={key++}>{tok.slice(1, -1)}</em>);
    }
    last = m.index + tok.length;
  }
  if (last < s.length) out.push(s.slice(last));
  return out;
}
