#!/usr/bin/env python3
"""dashboard.py — Dual-Process Model Job Dashboard

Interactive terminal UI for launching, monitoring, and managing
training and test jobs for the dual-process language model.

Usage:
    python dashboard.py              # Interactive menu
    python dashboard.py --job smoke  # Launch smoke test directly
    python dashboard.py --job test   # Launch pytest directly
    python dashboard.py --job tiny   # Launch full tiny training
"""

import argparse
import curses
import math
import os
import re
import subprocess
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────

PROJECT_DIR = Path.home() / "KahnemanHybridExperiment"
LOG_DIR = PROJECT_DIR / "logs"

# ── Data Classes ───────────────────────────────────────────────────


class Phase(Enum):
    MENU = auto()
    RUNNING = auto()
    DONE = auto()


@dataclass
class TrainMetrics:
    step: int = 0
    max_steps: int = 0
    ar_loss: float = 0.0
    diff_loss: float = 0.0
    conf_acc: float = 0.0
    lr: float = 0.0
    elapsed_secs: float = 0.0
    # eval
    eval_step: int = 0
    ar_ppl: float = 0.0
    eval_diff_loss: float = 0.0
    s1_tok_acc: float = 0.0
    conf_ece: float = 0.0
    conf_auroc: float = 0.0
    eval_conf_acc: float = 0.0
    # meta
    device: str = ""
    dtype: str = ""
    param_count: str = ""
    checkpoint_path: str = ""


@dataclass
class TestMetrics:
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    collected: int = 0
    duration: float = 0.0
    current_test: str = ""


@dataclass
class GPUInfo:
    name: str = "N/A"
    mem_total_mb: int = 0
    mem_used_mb: int = 0
    utilization: int = 0
    temp: int = 0


# ── Job Definitions ────────────────────────────────────────────────

JOBS = [
    {
        "key": "1",
        "name": "Run Tests",
        "desc": "pytest tests/ -v --tb=short",
        "cmd": [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        "type": "test",
        "max_steps": 0,
    },
    {
        "key": "2",
        "name": "Smoke Test",
        "desc": "Tiny config, 100 steps, fast validation",
        "cmd": [
            sys.executable, "-m", "src.training.joint_trainer",
            "--config", "configs/tiny.yaml", "--smoke_test",
        ],
        "type": "train",
        "max_steps": 100,
    },
    {
        "key": "3",
        "name": "Training — Tiny",
        "desc": "GPT-2 Small 124M, 50k steps, full run",
        "cmd": [
            sys.executable, "-m", "src.training.joint_trainer",
            "--config", "configs/tiny.yaml",
        ],
        "type": "train",
        "max_steps": 50000,
    },
]

# ── Color Pairs ────────────────────────────────────────────────────

C_NORMAL = 0
C_TITLE = 1
C_RUN = 2
C_OK = 3
C_FAIL = 4
C_BAR_FILL = 5
C_BAR_EMPTY = 6
C_LABEL = 7
C_VALUE = 8
C_LOG = 9
C_BORDER = 10
C_MENU_SEL = 11
C_HEADER = 12
C_DIM = 13
C_WARN = 14


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(C_TITLE,    curses.COLOR_CYAN,    -1)
    curses.init_pair(C_RUN,      curses.COLOR_YELLOW,  -1)
    curses.init_pair(C_OK,       curses.COLOR_GREEN,   -1)
    curses.init_pair(C_FAIL,     curses.COLOR_RED,     -1)
    curses.init_pair(C_BAR_FILL, curses.COLOR_BLACK,   curses.COLOR_GREEN)
    curses.init_pair(C_BAR_EMPTY,curses.COLOR_WHITE,   -1)
    curses.init_pair(C_LABEL,    curses.COLOR_WHITE,   -1)
    curses.init_pair(C_VALUE,    curses.COLOR_GREEN,   -1)
    curses.init_pair(C_LOG,      curses.COLOR_WHITE,   -1)
    curses.init_pair(C_BORDER,   curses.COLOR_BLUE,    -1)
    curses.init_pair(C_MENU_SEL, curses.COLOR_BLACK,   curses.COLOR_CYAN)
    curses.init_pair(C_HEADER,   curses.COLOR_WHITE,   curses.COLOR_BLUE)
    curses.init_pair(C_DIM,      curses.COLOR_WHITE,   -1)
    curses.init_pair(C_WARN,     curses.COLOR_RED,     -1)


# ── Helpers ────────────────────────────────────────────────────────


def fmt_time(secs: float) -> str:
    if secs < 0:
        return "--:--:--"
    h, rem = divmod(int(secs), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def fmt_mem(mb: int) -> str:
    return f"{mb / 1024:.1f}"


def safe_addstr(win, y: int, x: int, text: str, attr: int = 0):
    """Write string clipped to window bounds."""
    try:
        h, w = win.getmaxyx()
        if y < 0 or y >= h or x >= w:
            return
        avail = w - x - 1
        if avail <= 0:
            return
        win.addnstr(y, x, text, avail, attr)
    except curses.error:
        pass


def hbar(filled: int, total: int) -> str:
    """Build a bar string from block characters."""
    return "\u2588" * filled + "\u2591" * (total - filled)


# ── Line Parsers ──────────────────────────────────────────────────

RE_TRAIN = re.compile(
    r"step:\s*(\d+)\s*\|\s*ar_loss:\s*([\d.]+)\s*\|\s*"
    r"diff_loss:\s*([\d.]+)\s*\|\s*conf_acc:\s*([\d.]+)\s*\|\s*"
    r"lr:\s*([\d.eE+-]+)\s*\|\s*time:\s*([\d.]+)s"
)
RE_EVAL = re.compile(
    r"\[eval\]\s*step:\s*(\d+)\s*\|\s*ar_ppl:\s*([\d.]+)\s*\|\s*"
    r"diff_loss:\s*([\d.]+)\s*\|\s*"
    r"s1_tok_acc:\s*([\d.]+)\s*\|\s*conf_acc:\s*([\d.]+)\s*\|\s*"
    r"conf_ece:\s*([\d.]+)\s*\|\s*conf_auroc:\s*([\d.]+)"
)
RE_DEVICE = re.compile(r"Device:\s*(\S+),\s*dtype:\s*(\S+)")
RE_PARAMS = re.compile(r"Model parameters:\s*([\d,]+)")
RE_MAXSTEPS = re.compile(r"Max steps:\s*(\d+)")
RE_CHECKPOINT = re.compile(r"Saved checkpoint:\s*(.+)")
RE_COMPLETE = re.compile(r"Training complete")

RE_TEST_RESULT = re.compile(r"(\S+::\S+)\s+(PASSED|FAILED|ERROR)")
RE_TEST_COLLECTED = re.compile(r"collected\s+(\d+)\s+items?")
RE_TEST_SUMMARY = re.compile(
    r"=+\s*(?:(\d+)\s+passed)?(?:,?\s*(\d+)\s+failed)?"
    r"(?:,?\s*(\d+)\s+error)?.*?(?:in\s+([\d.]+)s)?\s*=+"
)


def parse_train_line(line: str, m: TrainMetrics) -> bool:
    """Parse one training output line into metrics. Returns True if updated."""
    match = RE_TRAIN.search(line)
    if match:
        m.step = int(match.group(1))
        m.ar_loss = float(match.group(2))
        m.diff_loss = float(match.group(3))
        m.conf_acc = float(match.group(4))
        m.lr = float(match.group(5))
        m.elapsed_secs = float(match.group(6))
        return True

    match = RE_EVAL.search(line)
    if match:
        m.eval_step = int(match.group(1))
        m.ar_ppl = float(match.group(2))
        m.eval_diff_loss = float(match.group(3))
        m.s1_tok_acc = float(match.group(4))
        m.eval_conf_acc = float(match.group(5))
        m.conf_ece = float(match.group(6))
        m.conf_auroc = float(match.group(7))
        return True

    match = RE_DEVICE.search(line)
    if match:
        m.device = match.group(1)
        m.dtype = match.group(2)
        return True

    match = RE_PARAMS.search(line)
    if match:
        m.param_count = match.group(1)
        return True

    match = RE_MAXSTEPS.search(line)
    if match:
        m.max_steps = int(match.group(1))
        return True

    match = RE_CHECKPOINT.search(line)
    if match:
        m.checkpoint_path = match.group(1).strip()
        return True

    return False


def parse_test_line(line: str, m: TestMetrics) -> bool:
    """Parse one pytest output line into metrics. Returns True if updated."""
    match = RE_TEST_RESULT.search(line)
    if match:
        m.current_test = match.group(1)
        result = match.group(2)
        if result == "PASSED":
            m.passed += 1
        elif result == "FAILED":
            m.failed += 1
        elif result == "ERROR":
            m.errors += 1
        m.total = m.passed + m.failed + m.errors
        return True

    match = RE_TEST_COLLECTED.search(line)
    if match:
        m.collected = int(match.group(1))
        return True

    match = RE_TEST_SUMMARY.search(line)
    if match:
        if match.group(1):
            m.passed = int(match.group(1))
        if match.group(2):
            m.failed = int(match.group(2))
        if match.group(3):
            m.errors = int(match.group(3))
        if match.group(4):
            m.duration = float(match.group(4))
        m.total = m.passed + m.failed + m.errors
        return True

    return False


# ── GPU Monitor ────────────────────────────────────────────────────


class GPUMonitor:
    """Polls nvidia-smi in a background thread."""

    def __init__(self):
        self.info = GPUInfo()
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        while not self._stop.is_set():
            self._poll()
            self._stop.wait(2.0)

    def _poll(self):
        try:
            raw = subprocess.check_output(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total,memory.used,utilization.gpu,temperature.gpu",
                    "--format=csv,noheader,nounits",
                ],
                timeout=5,
                stderr=subprocess.DEVNULL,
            ).decode().strip()
            parts = [p.strip() for p in raw.split(",")]
            if len(parts) >= 5:
                with self._lock:
                    self.info = GPUInfo(
                        name=parts[0],
                        mem_total_mb=int(parts[1]),
                        mem_used_mb=int(parts[2]),
                        utilization=int(parts[3]),
                        temp=int(parts[4]),
                    )
        except Exception:
            pass

    def get(self) -> GPUInfo:
        with self._lock:
            return GPUInfo(
                name=self.info.name,
                mem_total_mb=self.info.mem_total_mb,
                mem_used_mb=self.info.mem_used_mb,
                utilization=self.info.utilization,
                temp=self.info.temp,
            )

    def stop(self):
        self._stop.set()


# ── Dashboard ──────────────────────────────────────────────────────


class Dashboard:
    def __init__(self, stdscr, initial_job: int | None = None):
        self.scr = stdscr
        self.phase = Phase.MENU
        self.menu_sel = 0
        self.tm = TrainMetrics()
        self.xm = TestMetrics()
        self.gpu = GPUMonitor()
        self.log: deque[str] = deque(maxlen=2000)
        self.log_scroll = 0
        self.proc: subprocess.Popen | None = None
        self.job: dict | None = None
        self.job_start = 0.0
        self.exit_code: int | None = None
        self._reader: threading.Thread | None = None
        self._lock = threading.Lock()
        self._logfile = None
        self._initial_job = initial_job

        curses.curs_set(0)
        self.scr.nodelay(True)
        self.scr.timeout(250)
        init_colors()

    # ── Drawing ────────────────────────────────────────────────

    def _box(self, y: int, x: int, h: int, w: int, title: str = ""):
        s = self.scr
        a = curses.color_pair(C_BORDER)
        safe_addstr(s, y, x, "\u250c" + "\u2500" * (w - 2) + "\u2510", a)
        for r in range(y + 1, y + h - 1):
            safe_addstr(s, r, x, "\u2502", a)
            safe_addstr(s, r, x + w - 1, "\u2502", a)
        safe_addstr(s, y + h - 1, x, "\u2514" + "\u2500" * (w - 2) + "\u2518", a)
        if title:
            safe_addstr(s, y, x + 2, f" {title} ",
                        curses.color_pair(C_TITLE) | curses.A_BOLD)

    def _bar(self, y: int, x: int, w: int, frac: float, label: str = ""):
        s = self.scr
        inner = w - 2
        filled = max(0, min(inner, int(inner * min(frac, 1.0))))
        empty = inner - filled
        safe_addstr(s, y, x, "\u2590", curses.color_pair(C_BORDER))
        if filled > 0:
            safe_addstr(s, y, x + 1, "\u2588" * filled,
                        curses.color_pair(C_BAR_FILL))
        if empty > 0:
            safe_addstr(s, y, x + 1 + filled, "\u2591" * empty,
                        curses.color_pair(C_BAR_EMPTY) | curses.A_DIM)
        safe_addstr(s, y, x + 1 + inner, "\u258c", curses.color_pair(C_BORDER))
        if label:
            safe_addstr(s, y, x + w + 1, label,
                        curses.color_pair(C_VALUE) | curses.A_BOLD)

    def _metric(self, y: int, x: int, lbl: str, val: str, vattr=None):
        if vattr is None:
            vattr = curses.color_pair(C_VALUE) | curses.A_BOLD
        safe_addstr(self.scr, y, x, lbl,
                    curses.color_pair(C_LABEL) | curses.A_DIM)
        safe_addstr(self.scr, y, x + len(lbl), val, vattr)

    # ── Menu View ──────────────────────────────────────────────

    def _draw_menu(self):
        s = self.scr
        h, w = s.getmaxyx()
        s.erase()

        # Header
        safe_addstr(s, 0, 0, " " * w, curses.color_pair(C_HEADER))
        title = " DUAL-PROCESS MODEL \u2014 JOB DASHBOARD "
        safe_addstr(s, 0, max(0, (w - len(title)) // 2), title,
                    curses.color_pair(C_HEADER) | curses.A_BOLD)

        gpu = self.gpu.get()
        if gpu.name != "N/A":
            gi = f"{gpu.name}  {fmt_mem(gpu.mem_used_mb)}/{fmt_mem(gpu.mem_total_mb)} GB"
            safe_addstr(s, 0, max(0, w - len(gi) - 2), gi,
                        curses.color_pair(C_HEADER))

        # Job list
        bw = min(62, w - 4)
        bx = max(0, (w - bw) // 2)
        by = 3
        bh = len(JOBS) * 3 + 3
        self._box(by, bx, bh, bw, "Select Job")

        for i, job in enumerate(JOBS):
            ry = by + 1 + i * 3
            if i == self.menu_sel:
                safe_addstr(s, ry, bx + 2, " " * (bw - 4),
                            curses.color_pair(C_MENU_SEL))
                safe_addstr(s, ry, bx + 3, f"\u25b8 [{job['key']}] {job['name']}",
                            curses.color_pair(C_MENU_SEL) | curses.A_BOLD)
                safe_addstr(s, ry + 1, bx + 8, job["desc"],
                            curses.color_pair(C_MENU_SEL))
            else:
                safe_addstr(s, ry, bx + 3, f"  [{job['key']}] {job['name']}",
                            curses.color_pair(C_LABEL))
                safe_addstr(s, ry + 1, bx + 8, job["desc"],
                            curses.color_pair(C_DIM) | curses.A_DIM)

        # Keybinds
        fy = by + bh + 1
        safe_addstr(s, fy, bx + 2, "[", curses.color_pair(C_DIM))
        safe_addstr(s, fy, bx + 3, "\u2191\u2193", curses.color_pair(C_TITLE))
        safe_addstr(s, fy, bx + 5, "] Navigate   [", curses.color_pair(C_DIM))
        safe_addstr(s, fy, bx + 19, "Enter", curses.color_pair(C_TITLE))
        safe_addstr(s, fy, bx + 24, "] Launch   [", curses.color_pair(C_DIM))
        safe_addstr(s, fy, bx + 36, "q", curses.color_pair(C_TITLE))
        safe_addstr(s, fy, bx + 37, "] Quit", curses.color_pair(C_DIM))

        s.refresh()

    # ── Running / Done View ────────────────────────────────────

    def _draw_dashboard(self):
        s = self.scr
        h, w = s.getmaxyx()
        s.erase()

        job = self.job
        is_train = job["type"] == "train"
        elapsed = time.time() - self.job_start
        gpu = self.gpu.get()
        pw = max(20, w - 4)  # panel inner width

        # ── Row 0: Header bar ──
        safe_addstr(s, 0, 0, " " * w, curses.color_pair(C_HEADER))
        safe_addstr(s, 0, 1, f" {job['name']} \u2014 {job['desc']}",
                    curses.color_pair(C_HEADER) | curses.A_BOLD)

        if self.phase == Phase.RUNNING:
            st, sa = "\u25cf RUNNING", curses.color_pair(C_RUN) | curses.A_BOLD
        elif self.exit_code == 0:
            st, sa = "\u2713 COMPLETED", curses.color_pair(C_OK) | curses.A_BOLD
        else:
            st, sa = "\u2717 FAILED (rc=%d)" % (self.exit_code or -1), \
                     curses.color_pair(C_FAIL) | curses.A_BOLD
        safe_addstr(s, 0, max(0, w - len(st) - 2), st, sa)

        row = 2

        # ── Row 2: Timing ──
        self._metric(row, 2, "Elapsed: ", fmt_time(elapsed))
        if is_train and self.tm.step > 0:
            mx = self.tm.max_steps or job["max_steps"]
            if mx > 0:
                frac = self.tm.step / mx
                if frac > 0.001:
                    eta = elapsed / frac * (1.0 - frac)
                    self._metric(row, 24, "ETA: ", fmt_time(eta))
        if is_train and self.tm.device:
            info = f"{self.tm.device}  {self.tm.dtype}"
            if self.tm.param_count:
                info += f"  {self.tm.param_count} params"
            safe_addstr(s, row, max(0, w - len(info) - 2), info,
                        curses.color_pair(C_DIM) | curses.A_DIM)

        row += 2

        # ── Row 4: Progress bar ──
        bar_w = min(pw - 18, 50)
        if is_train:
            mx = self.tm.max_steps or job["max_steps"]
            frac = self.tm.step / mx if mx > 0 else 0.0
            pct = f" {self.tm.step}/{mx} ({frac * 100:.0f}%)"
            self._bar(row, 2, bar_w, frac, pct)
        else:
            if self.xm.collected > 0:
                frac = self.xm.total / self.xm.collected
                pct = f" {self.xm.total}/{self.xm.collected} tests ({frac * 100:.0f}%)"
                self._bar(row, 2, bar_w, frac, pct)
            else:
                safe_addstr(s, row, 2, "Collecting tests...",
                            curses.color_pair(C_DIM) | curses.A_DIM)

        row += 2

        # ── Metrics panels ──
        col_w = pw // 3

        if is_train:
            # Training metrics
            self._box(row, 1, 4, pw, "Training Metrics")
            y = row + 1
            self._metric(y, 3,          "Step: ",      f"{self.tm.step}")
            self._metric(y, 3 + col_w,  "AR Loss: ",   f"{self.tm.ar_loss:.4f}")
            self._metric(y, 3 + col_w * 2, "Diff Loss: ", f"{self.tm.diff_loss:.4f}")
            y += 1
            self._metric(y, 3,          "LR: ",        f"{self.tm.lr:.2e}")
            self._metric(y, 3 + col_w,  "Conf Acc: ",  f"{self.tm.conf_acc:.4f}")
            if self.tm.checkpoint_path:
                ckpt = self.tm.checkpoint_path.rsplit("/", 1)[-1]
                self._metric(y, 3 + col_w * 2, "Ckpt: ", ckpt)
            row += 5

            # Eval metrics
            if self.tm.eval_step > 0:
                self._box(row, 1, 4, pw,
                          f"Eval Metrics (step {self.tm.eval_step})")
                y = row + 1
                self._metric(y, 3,          "AR PPL: ",     f"{self.tm.ar_ppl:.2f}")
                self._metric(y, 3 + col_w,  "S1 Tok Acc: ", f"{self.tm.s1_tok_acc:.4f}")
                self._metric(y, 3 + col_w * 2, "Conf Acc: ",  f"{self.tm.eval_conf_acc:.4f}")
                y += 1
                self._metric(y, 3,          "Conf ECE: ",   f"{self.tm.conf_ece:.4f}")
                self._metric(y, 3 + col_w,  "AUROC: ",      f"{self.tm.conf_auroc:.4f}")
                self._metric(y, 3 + col_w * 2, "Diff Loss: ", f"{self.tm.eval_diff_loss:.4f}")
                row += 5
            else:
                self._box(row, 1, 3, pw, "Eval Metrics")
                safe_addstr(s, row + 1, 3, "Waiting for first eval...",
                            curses.color_pair(C_DIM) | curses.A_DIM)
                row += 4
        else:
            # Test metrics
            th = 5 if self.xm.current_test else 4
            self._box(row, 1, th, pw, "Test Results")
            y = row + 1
            self._metric(y, 3, "Passed: ", f"{self.xm.passed}",
                         curses.color_pair(C_OK) | curses.A_BOLD)
            self._metric(y, 3 + col_w, "Failed: ", f"{self.xm.failed}",
                         curses.color_pair(C_FAIL) | curses.A_BOLD
                         if self.xm.failed else
                         curses.color_pair(C_VALUE) | curses.A_BOLD)
            self._metric(y, 3 + col_w * 2, "Errors: ", f"{self.xm.errors}",
                         curses.color_pair(C_FAIL) | curses.A_BOLD
                         if self.xm.errors else
                         curses.color_pair(C_VALUE) | curses.A_BOLD)
            y += 1
            if self.xm.duration > 0:
                self._metric(y, 3, "Duration: ", f"{self.xm.duration:.1f}s")
            if self.xm.current_test:
                y += 1
                safe_addstr(s, y, 3, "Last: ", curses.color_pair(C_DIM))
                trunc = pw - 12
                tn = self.xm.current_test
                if len(tn) > trunc:
                    tn = "..." + tn[-(trunc - 3):]
                safe_addstr(s, y, 9, tn, curses.color_pair(C_VALUE))
            row += th + 1

        # ── GPU panel ──
        self._box(row, 1, 4, pw, f"GPU \u2014 {gpu.name}")
        y = row + 1
        mem_frac = gpu.mem_used_mb / gpu.mem_total_mb if gpu.mem_total_mb else 0
        gbw = min(22, pw // 3)

        safe_addstr(s, y, 3, "VRAM: ", curses.color_pair(C_LABEL) | curses.A_DIM)
        self._bar(y, 9, gbw, mem_frac,
                  f" {fmt_mem(gpu.mem_used_mb)}/{fmt_mem(gpu.mem_total_mb)} GB")

        y += 1
        uf = gpu.utilization / 100.0
        safe_addstr(s, y, 3, "Util: ", curses.color_pair(C_LABEL) | curses.A_DIM)
        self._bar(y, 9, gbw, uf, f" {gpu.utilization}%")

        temp_str = f"Temp: {gpu.temp}\u00b0C"
        temp_attr = curses.color_pair(C_WARN) if gpu.temp > 80 else \
                    curses.color_pair(C_VALUE)
        safe_addstr(s, y, 9 + gbw + 10, temp_str, temp_attr | curses.A_BOLD)

        row += 5

        # ── Log panel ──
        log_h = max(4, h - row - 2)
        self._box(row, 1, log_h, pw, "Log Output")

        with self._lock:
            lines = list(self.log)

        visible = log_h - 2
        total = len(lines)
        if self.log_scroll == 0:
            start = max(0, total - visible)
        else:
            start = max(0, total - visible - self.log_scroll)

        for i in range(visible):
            idx = start + i
            if 0 <= idx < total:
                ln = lines[idx]
                if ln.startswith("[eval]"):
                    a = curses.color_pair(C_TITLE)
                elif "PASSED" in ln:
                    a = curses.color_pair(C_OK)
                elif "FAILED" in ln or "ERROR" in ln or "error" in ln.lower():
                    a = curses.color_pair(C_FAIL)
                elif "checkpoint" in ln.lower() or "Saved" in ln:
                    a = curses.color_pair(C_RUN) | curses.A_BOLD
                elif "Training complete" in ln:
                    a = curses.color_pair(C_OK) | curses.A_BOLD
                else:
                    a = curses.color_pair(C_LOG) | curses.A_DIM
                safe_addstr(s, row + 1 + i, 3, ln[:pw - 6], a)

        # Scroll indicator
        if total > visible:
            pos_frac = start / max(1, total - visible)
            ind_y = row + 1 + int(pos_frac * max(0, visible - 1))
            safe_addstr(s, ind_y, pw, "\u2588",
                        curses.color_pair(C_TITLE) | curses.A_DIM)

        # ── Footer ──
        fy = h - 1
        footer_w = min(pw, w)
        safe_addstr(s, fy, 0, " " * footer_w, curses.color_pair(C_HEADER))
        if self.phase == Phase.RUNNING:
            quit_str = " [q] Quit "
            safe_addstr(s, fy, 1, " [k]",
                        curses.color_pair(C_TITLE) | curses.A_BOLD)
            safe_addstr(s, fy, 5, " Kill", curses.color_pair(C_HEADER))
            safe_addstr(s, fy, 11, " [\u2191\u2193]",
                        curses.color_pair(C_TITLE) | curses.A_BOLD)
            safe_addstr(s, fy, 16, " Scroll", curses.color_pair(C_HEADER))
            qx = max(24, footer_w - len(quit_str) - 1)
            safe_addstr(s, fy, qx, " [q]",
                        curses.color_pair(C_TITLE) | curses.A_BOLD)
            safe_addstr(s, fy, qx + 4, " Quit ", curses.color_pair(C_HEADER))
        else:
            quit_str = " [q] Quit "
            safe_addstr(s, fy, 1, " [Enter]",
                        curses.color_pair(C_TITLE) | curses.A_BOLD)
            safe_addstr(s, fy, 9, " Menu", curses.color_pair(C_HEADER))
            safe_addstr(s, fy, 15, " [r]",
                        curses.color_pair(C_TITLE) | curses.A_BOLD)
            safe_addstr(s, fy, 19, " Rerun", curses.color_pair(C_HEADER))
            qx = max(26, footer_w - len(quit_str) - 1)
            safe_addstr(s, fy, qx, " [q]",
                        curses.color_pair(C_TITLE) | curses.A_BOLD)
            safe_addstr(s, fy, qx + 4, " Quit ", curses.color_pair(C_HEADER))

        s.refresh()

    # ── Job Execution ──────────────────────────────────────────

    def _read_output(self):
        """Background thread: stream subprocess output."""
        for raw in self.proc.stdout:
            line = raw.rstrip("\n\r")
            with self._lock:
                self.log.append(line)
                if self.job["type"] == "train":
                    parse_train_line(line, self.tm)
                else:
                    parse_test_line(line, self.xm)
            if self._logfile:
                try:
                    self._logfile.write(line + "\n")
                    self._logfile.flush()
                except Exception:
                    pass

    def _launch(self, job: dict):
        self.job = job
        self.phase = Phase.RUNNING
        self.tm = TrainMetrics(max_steps=job.get("max_steps", 0))
        self.xm = TestMetrics()
        self.log.clear()
        self.log_scroll = 0
        self.exit_code = None
        self.job_start = time.time()

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_slug = job["name"].lower().replace(" ", "_").replace("\u2014", "-")
        lp = LOG_DIR / f"{name_slug}_{ts}.log"
        self._logfile = open(lp, "w")

        env = {**os.environ, "PYTHONUNBUFFERED": "1"}
        self.proc = subprocess.Popen(
            job["cmd"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=str(PROJECT_DIR),
            env=env,
        )
        self._reader = threading.Thread(target=self._read_output, daemon=True)
        self._reader.start()

    def _kill(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()

    def _check_done(self):
        if self.proc and self.proc.poll() is not None:
            self.exit_code = self.proc.returncode
            self.phase = Phase.DONE
            if self._logfile:
                self._logfile.close()
                self._logfile = None
            # Terminal bell notification
            sys.stdout.write("\a")
            sys.stdout.flush()

    # ── Main Loop ──────────────────────────────────────────────

    def run(self):
        # Auto-launch if specified via CLI
        if self._initial_job is not None and 0 <= self._initial_job < len(JOBS):
            self._launch(JOBS[self._initial_job])

        try:
            while True:
                try:
                    key = self.scr.getch()
                except curses.error:
                    key = -1

                if self.phase == Phase.MENU:
                    if key == ord("q"):
                        break
                    elif key == curses.KEY_UP:
                        self.menu_sel = (self.menu_sel - 1) % len(JOBS)
                    elif key == curses.KEY_DOWN:
                        self.menu_sel = (self.menu_sel + 1) % len(JOBS)
                    elif key in (curses.KEY_ENTER, 10, 13):
                        self._launch(JOBS[self.menu_sel])
                        continue
                    elif key in (ord("1"), ord("2"), ord("3")):
                        idx = key - ord("1")
                        if 0 <= idx < len(JOBS):
                            self.menu_sel = idx
                            self._launch(JOBS[idx])
                            continue
                    self._draw_menu()

                elif self.phase == Phase.RUNNING:
                    self._check_done()
                    if key == ord("q"):
                        self._kill()
                        break
                    elif key == ord("k"):
                        self._kill()
                    elif key == curses.KEY_UP:
                        self.log_scroll = min(
                            self.log_scroll + 3,
                            max(0, len(self.log) - 5))
                    elif key == curses.KEY_DOWN:
                        self.log_scroll = max(0, self.log_scroll - 3)
                    self._draw_dashboard()

                elif self.phase == Phase.DONE:
                    if key == ord("q"):
                        break
                    elif key in (curses.KEY_ENTER, 10, 13):
                        self.phase = Phase.MENU
                        continue
                    elif key == ord("r"):
                        self._launch(self.job)
                        continue
                    elif key == curses.KEY_UP:
                        self.log_scroll = min(
                            self.log_scroll + 3,
                            max(0, len(self.log) - 5))
                    elif key == curses.KEY_DOWN:
                        self.log_scroll = max(0, self.log_scroll - 3)
                    self._draw_dashboard()

        finally:
            self.gpu.stop()
            if self.proc and self.proc.poll() is None:
                self.proc.terminate()
            if self._logfile:
                self._logfile.close()


# ── Entry Point ────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Dual-Process Model Job Dashboard")
    parser.add_argument(
        "--job", choices=["test", "smoke", "tiny"],
        help="Launch a job directly (skip menu)")
    args = parser.parse_args()

    job_idx = {"test": 0, "smoke": 1, "tiny": 2}.get(args.job)

    def run(stdscr):
        Dashboard(stdscr, initial_job=job_idx).run()

    curses.wrapper(run)


if __name__ == "__main__":
    main()
