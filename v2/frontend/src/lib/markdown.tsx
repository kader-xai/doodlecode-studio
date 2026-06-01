import { JSX } from "react";

/**
 * Minimal markdown renderer — zero dependencies, deliberately small.
 *
 * Supports:
 *   `# H1`, `## H2`, `### H3`
 *   `- item` or `* item`            (bullet list)
 *   `- [ ] todo` / `- [x] done`     (task list — read-only checkbox)
 *   `1. item` or `1) item`          (ordered list)
 *   `> blockquote`
 *   `---`                           (horizontal rule)
 *   `**bold**`, `*italic*`, `~~strikethrough~~`
 *   `` `inline code` ``
 *   ```` ```fenced code``` ````     (literal block, optional language)
 *   `[text](url)`                   (link — http/https/mailto/relative)
 *   `| a | b |` + `| --- | :-: |`   (table, with column alignment)
 *   blank lines separate paragraphs
 *
 * We do NOT support full CommonMark (no images, nested lists). That's
 * intentional — v1 grew a giant markdown surface and most of it went
 * unused. Add only what users ask for.
 */
/** A `| --- | :--: |` row: pipes plus dashes, only dash/colon/pipe/space. */
function isTableSeparator(line: string): boolean {
  return (
    line.includes("|") &&
    line.includes("-") &&
    /^\s*\|?[\s:|-]+\|?\s*$/.test(line) &&
    /\|/.test(line)
  );
}

/** Split `| a | b |` into trimmed cells, tolerating optional edge pipes. */
function splitTableRow(line: string): string[] {
  let s = line.trim();
  if (s.startsWith("|")) s = s.slice(1);
  if (s.endsWith("|")) s = s.slice(0, -1);
  return s.split("|").map((c) => c.trim());
}

/** Column alignment from a separator cell: `:--` left, `:-:` center, `--:` right. */
function alignOf(seg: string): "left" | "center" | "right" {
  const t = seg.trim();
  const l = t.startsWith(":");
  const r = t.endsWith(":");
  if (l && r) return "center";
  if (r) return "right";
  return "left";
}

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

    // Iter 197: fenced code block — ```lang … ```. Content is literal
    // (no inline parsing), so example syntax shows verbatim. An
    // unterminated fence runs to the end of the source.
    if (/^```/.test(line)) {
      const lang = line.replace(/^```+/, "").trim();
      const codeLines: string[] = [];
      i++; // skip opening fence
      while (i < lines.length && !/^```/.test(lines[i])) {
        codeLines.push(lines[i]);
        i++;
      }
      if (i < lines.length) i++; // skip closing fence
      out.push(
        <pre
          key={key++}
          className="my-2 rounded-lg border-2 border-ink/25 dark:border-white/25 bg-ink/5 dark:bg-white/10 p-3 overflow-x-auto scrollbar-none"
        >
          <code
            className="font-mono text-base whitespace-pre"
            data-lang={lang || undefined}
          >
            {codeLines.join("\n")}
          </code>
        </pre>,
      );
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

    // Iter 196: GitHub-style table — a header row of `| a | b |`
    // immediately followed by a separator row `| --- | :--: |`. The
    // separator's colons set per-column alignment. Body rows continue
    // until a blank or non-pipe line.
    if (
      line.includes("|") &&
      i + 1 < lines.length &&
      isTableSeparator(lines[i + 1])
    ) {
      const headers = splitTableRow(line);
      const aligns = splitTableRow(lines[i + 1]).map(alignOf);
      i += 2;
      const rows: string[][] = [];
      while (
        i < lines.length &&
        lines[i].includes("|") &&
        lines[i].trim() !== ""
      ) {
        rows.push(splitTableRow(lines[i]));
        i++;
      }
      const cellBase =
        "border-2 border-ink/30 dark:border-white/30 px-3 py-1 align-top";
      out.push(
        <div key={key++} className={`my-2 overflow-x-auto scrollbar-none ${wrap}`}>
          <table className="border-collapse font-hand text-xl">
            <thead>
              <tr>
                {headers.map((h, j) => (
                  <th
                    key={j}
                    scope="col"
                    style={{ textAlign: aligns[j] ?? "left" }}
                    className={`${cellBase} font-bold bg-ink/5 dark:bg-white/10`}
                  >
                    {renderInline(h)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, ri) => (
                <tr key={ri}>
                  {headers.map((_, ci) => (
                    <td
                      key={ci}
                      style={{ textAlign: aligns[ci] ?? "left" }}
                      className={cellBase}
                    >
                      {renderInline(r[ci] ?? "")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>,
      );
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
          {items.map((it, j) => {
            // Iter 201: GitHub-style task list — `- [ ]` / `- [x]` renders
            // a read-only checkbox instead of a disc. Mixed lists are fine.
            const task = /^\[([ xX])\]\s+(.*)$/.exec(it);
            if (task) {
              const checked = task[1].toLowerCase() === "x";
              return (
                <li key={j} className="list-none -ml-6 flex items-start gap-2">
                  <input
                    type="checkbox"
                    checked={checked}
                    readOnly
                    aria-checked={checked}
                    className="mt-1.5 accent-marker-pink"
                  />
                  <span className={checked ? "line-through opacity-70" : ""}>
                    {renderInline(task[2])}
                  </span>
                </li>
              );
            }
            return <li key={j}>{renderInline(it)}</li>;
          })}
        </ul>,
      );
      continue;
    }

    // Iter 186: ordered list — `1. item`, `2) item`. The list starts at
    // the first number found, so `3. … 4. …` renders 3, 4 (via `start`).
    if (/^\d+[.)]\s+/.test(line)) {
      const items: string[] = [];
      const startNum = parseInt(line.match(/^(\d+)/)![1], 10);
      while (i < lines.length && /^\d+[.)]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\d+[.)]\s+/, ""));
        i++;
      }
      out.push(
        <ol
          key={key++}
          start={startNum}
          className={`list-decimal pl-6 font-hand text-xl leading-snug space-y-0.5 ${wrap}`}
        >
          {items.map((it, j) => (
            <li key={j}>{renderInline(it)}</li>
          ))}
        </ol>,
      );
      continue;
    }

    // Paragraph (group consecutive non-empty non-block lines)
    const para: string[] = [];
    while (
      i < lines.length &&
      lines[i].trim() !== "" &&
      !/^(#{1,3}\s|[-*]\s|\d+[.)]\s|>\s|---+\s*$)/.test(lines[i])
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

/** Inline pass: `[text](url)` links, **bold**, *italic*, `~~strike~~`,
 *  `code`. */
function renderInline(s: string): (string | JSX.Element)[] {
  const out: (string | JSX.Element)[] = [];
  // One regex with several alternatives. Links come first so their text
  // isn't parsed as emphasis; `bold` precedes `italic` so `**x**` isn't
  // first parsed as `*` + `*x*` + `*`; `~~strike~~` is unambiguous.
  const re = /(\[[^\]]+\]\([^)\s]+\)|\*\*[^*]+\*\*|~~[^~]+~~|\*[^*\n]+\*|`[^`]+`)/g;
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
    } else if (tok.startsWith("~~")) {
      out.push(
        <del key={key++} className="opacity-70">
          {tok.slice(2, -2)}
        </del>,
      );
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
