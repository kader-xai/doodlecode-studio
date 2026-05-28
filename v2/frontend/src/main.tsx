import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App";
import { ToolsPage } from "./ToolsPage";
import "./index.css";

/** Tiny path-based router. We have exactly two pages — the canvas
 *  app and the /tools utilities — so a 200-byte switch is enough.
 *  No react-router dependency to add for this. */
const Root = window.location.pathname.startsWith("/tools") ? <ToolsPage /> : <App />;

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>{Root}</React.StrictMode>,
);
