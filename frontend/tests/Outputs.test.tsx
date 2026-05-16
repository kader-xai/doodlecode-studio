import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Outputs } from "../src/components/Outputs";

describe("Outputs", () => {
  it("renders nothing when no result is passed", () => {
    const { container } = render(<Outputs />);
    expect(container.firstChild).toBeNull();
  });

  it("shows stdout text", () => {
    render(
      <Outputs
        result={{
          status: "ok",
          outputs: [{ type: "stream", name: "stdout", text: "hello world" }],
        }}
      />
    );
    expect(screen.getByText(/hello world/)).toBeInTheDocument();
  });

  it("shows result text/plain", () => {
    render(
      <Outputs
        result={{
          status: "ok",
          outputs: [{ type: "result", data: { "text/plain": "42" } }],
        }}
      />
    );
    expect(screen.getByText("42")).toBeInTheDocument();
  });

  it("shows error pill when status is error", () => {
    render(
      <Outputs
        result={{
          status: "error",
          outputs: [{ type: "error", ename: "TypeError", evalue: "bad", traceback: [] }],
        }}
      />
    );
    expect(screen.getByText("error")).toBeInTheDocument();
    expect(screen.getByText(/TypeError: bad/)).toBeInTheDocument();
  });

  it("shows install chip for ModuleNotFoundError", () => {
    render(
      <Outputs
        result={{
          status: "error",
          outputs: [
            {
              type: "error",
              ename: "ModuleNotFoundError",
              evalue: "No module named 'torch'",
              traceback: [],
            },
          ],
        }}
      />
    );
    expect(screen.getByText(/Install/)).toBeInTheDocument();
    expect(screen.getByText("torch")).toBeInTheDocument();
  });

  it("shows '(no output)' for an empty successful run", () => {
    render(<Outputs result={{ status: "ok", outputs: [] }} />);
    expect(screen.getByText(/no output/)).toBeInTheDocument();
  });
});
