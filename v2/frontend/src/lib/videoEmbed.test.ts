import { describe, expect, it } from "vitest";
import {
  parseTimestamp,
  videoEmbed,
  vimeoEmbed,
  youTubeEmbed,
} from "./videoEmbed";

describe("parseTimestamp (iter 183)", () => {
  it("parses bare seconds and Ns", () => {
    expect(parseTimestamp("90")).toBe(90);
    expect(parseTimestamp("90s")).toBe(90);
  });
  it("parses compound h/m/s", () => {
    expect(parseTimestamp("1m30s")).toBe(90);
    expect(parseTimestamp("1h2m3s")).toBe(3723);
    expect(parseTimestamp("45s")).toBe(45);
  });
  it("parses colon clock", () => {
    expect(parseTimestamp("1:30")).toBe(90);
    expect(parseTimestamp("1:02:03")).toBe(3723);
  });
  it("rejects junk / zero / empty", () => {
    expect(parseTimestamp(null)).toBeNull();
    expect(parseTimestamp("")).toBeNull();
    expect(parseTimestamp("0")).toBeNull();
    expect(parseTimestamp("abc")).toBeNull();
  });
});

describe("youTubeEmbed (iter 183)", () => {
  it("maps a watch URL", () => {
    expect(youTubeEmbed("https://www.youtube.com/watch?v=abc123")).toBe(
      "https://www.youtube.com/embed/abc123",
    );
  });
  it("maps youtu.be short links", () => {
    expect(youTubeEmbed("https://youtu.be/abc123")).toBe(
      "https://www.youtube.com/embed/abc123",
    );
  });
  it("preserves a ?t= start time as ?start=", () => {
    expect(youTubeEmbed("https://www.youtube.com/watch?v=abc123&t=90s")).toBe(
      "https://www.youtube.com/embed/abc123?start=90",
    );
    expect(youTubeEmbed("https://youtu.be/abc123?t=1m30s")).toBe(
      "https://www.youtube.com/embed/abc123?start=90",
    );
  });
  it("honors an explicit ?start=", () => {
    expect(youTubeEmbed("https://www.youtube.com/watch?v=x&start=12")).toBe(
      "https://www.youtube.com/embed/x?start=12",
    );
  });
  it("maps shorts with a timestamp", () => {
    expect(youTubeEmbed("https://www.youtube.com/shorts/zzz?t=5")).toBe(
      "https://www.youtube.com/embed/zzz?start=5",
    );
  });
  it("returns null for non-YouTube", () => {
    expect(youTubeEmbed("https://example.com")).toBeNull();
  });

  it("propagates autoplay + mute flags (iter 184)", () => {
    expect(youTubeEmbed("https://www.youtube.com/watch?v=x&autoplay=1&mute=1")).toBe(
      "https://www.youtube.com/embed/x?autoplay=1&mute=1",
    );
  });

  it("loop names the single-video playlist (iter 184)", () => {
    expect(youTubeEmbed("https://www.youtube.com/watch?v=x&loop=1")).toBe(
      "https://www.youtube.com/embed/x?loop=1&playlist=x",
    );
  });

  it("combines start + flags deterministically (iter 184)", () => {
    expect(
      youTubeEmbed("https://www.youtube.com/watch?v=x&t=30&autoplay=1"),
    ).toBe("https://www.youtube.com/embed/x?start=30&autoplay=1");
  });
});

describe("vimeoEmbed (iter 183)", () => {
  it("maps a vimeo URL", () => {
    expect(vimeoEmbed("https://vimeo.com/123456789")).toBe(
      "https://player.vimeo.com/video/123456789",
    );
  });
  it("preserves a #t= start time", () => {
    expect(vimeoEmbed("https://vimeo.com/123456789#t=90s")).toBe(
      "https://player.vimeo.com/video/123456789#t=90s",
    );
  });
  it("returns null for non-vimeo", () => {
    expect(vimeoEmbed("https://youtube.com/watch?v=x")).toBeNull();
  });
});

describe("videoEmbed (iter 183)", () => {
  it("dispatches to either provider", () => {
    expect(videoEmbed("https://youtu.be/x")).toContain("youtube.com/embed/x");
    expect(videoEmbed("https://vimeo.com/9")).toContain("player.vimeo.com/video/9");
    expect(videoEmbed("https://example.com/clip.mp4")).toBeNull();
  });
});
