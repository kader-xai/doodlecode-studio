"""IPython kernel pool. One persistent kernel per session_id keeps state across runs."""
from __future__ import annotations

import queue
import threading
from typing import Optional

from jupyter_client.manager import KernelManager

from .models import ExecuteOutput, ExecuteResponse


class KernelSession:
    def __init__(self) -> None:
        self.km = KernelManager(kernel_name="python3")
        self.km.start_kernel()
        self.kc = self.km.client()
        self.kc.start_channels()
        self.kc.wait_for_ready(timeout=30)
        self._lock = threading.Lock()

    def execute(self, code: str, timeout: float = 60.0) -> ExecuteResponse:
        with self._lock:
            msg_id = self.kc.execute(code, store_history=True)
            outputs: list[ExecuteOutput] = []
            status: str = "ok"
            execution_count: Optional[int] = None
            done = False
            while not done:
                try:
                    msg = self.kc.get_iopub_msg(timeout=timeout)
                except queue.Empty:
                    status = "aborted"
                    break
                parent = msg.get("parent_header", {})
                if parent.get("msg_id") != msg_id:
                    continue
                msg_type = msg["msg_type"]
                content = msg["content"]
                if msg_type == "status" and content.get("execution_state") == "idle":
                    done = True
                elif msg_type == "stream":
                    outputs.append(ExecuteOutput(
                        type="stream", name=content.get("name"), text=content.get("text"),
                    ))
                elif msg_type == "execute_result":
                    execution_count = content.get("execution_count")
                    outputs.append(ExecuteOutput(type="result", data=content.get("data")))
                elif msg_type == "display_data":
                    outputs.append(ExecuteOutput(type="display", data=content.get("data")))
                elif msg_type == "error":
                    status = "error"
                    outputs.append(ExecuteOutput(
                        type="error",
                        ename=content.get("ename"),
                        evalue=content.get("evalue"),
                        traceback=content.get("traceback"),
                    ))
            # consume the shell reply for execution_count if not seen
            try:
                shell = self.kc.get_shell_msg(timeout=2)
                if shell.get("parent_header", {}).get("msg_id") == msg_id:
                    execution_count = shell["content"].get("execution_count", execution_count)
            except queue.Empty:
                pass
            return ExecuteResponse(
                outputs=outputs, status=status, execution_count=execution_count
            )

    def shutdown(self) -> None:
        try:
            self.kc.stop_channels()
        finally:
            self.km.shutdown_kernel(now=True)


class KernelPool:
    def __init__(self) -> None:
        self._sessions: dict[str, KernelSession] = {}
        self._lock = threading.Lock()

    def get(self, session_id: str) -> KernelSession:
        with self._lock:
            s = self._sessions.get(session_id)
            if s is None:
                s = KernelSession()
                self._sessions[session_id] = s
            return s

    def reset(self, session_id: str) -> None:
        with self._lock:
            s = self._sessions.pop(session_id, None)
        if s:
            s.shutdown()

    def shutdown_all(self) -> None:
        with self._lock:
            sessions = list(self._sessions.values())
            self._sessions.clear()
        for s in sessions:
            try:
                s.shutdown()
            except Exception as e:
                import logging

                logging.getLogger(__name__).warning("kernel shutdown failed: %s", e)


pool = KernelPool()
