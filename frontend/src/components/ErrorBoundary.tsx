import { Component, ErrorInfo, ReactNode } from "react";

interface State {
  err: Error | null;
}

/**
 * Catches any thrown error in the React tree and shows a small dismiss-
 * able card instead of letting the whole page go blank. Reload button
 * survives even a totally borked render.
 */
export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { err: null };

  static getDerivedStateFromError(err: Error): State {
    return { err };
  }

  componentDidCatch(err: Error, info: ErrorInfo) {
    // eslint-disable-next-line no-console
    console.error("Render error:", err, info.componentStack);
  }

  render() {
    if (this.state.err) {
      return (
        <div className="fixed inset-0 z-[1000] flex items-center justify-center bg-black/70 text-ink dark:text-white">
          <div className="w-[480px] max-w-[92vw] bg-white dark:bg-[#1f2228] border-2 border-ink dark:border-white rounded-2xl p-5 shadow-sketch font-hand">
            <div className="text-3xl mb-2">😬 Something broke</div>
            <div className="text-lg text-ink/80 dark:text-white/80 mb-3">
              The UI hit an unexpected error. Your work is still saved
              (auto-save runs every edit). You can reload to recover.
            </div>
            <pre className="font-mono text-xs whitespace-pre-wrap bg-stone-50 dark:bg-[#0f1115] border-2 border-ink/40 dark:border-white/40 rounded p-2 max-h-48 overflow-auto">
              {String(this.state.err?.stack ?? this.state.err)}
            </pre>
            <div className="flex justify-between mt-3">
              <button
                className="btn-sketch sky"
                onClick={() => this.setState({ err: null })}
              >
                Dismiss
              </button>
              <button
                className="btn-sketch mint"
                onClick={() => window.location.reload()}
              >
                Reload page
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
