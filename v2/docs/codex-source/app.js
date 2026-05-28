import { renderDoodleDiagramBlocks } from "./diagramBlocks.js";

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

const markdownSample = `# Doodle pitch

## What this slide proves
- Markdown turns into presentation-ready notes
- Code blocks keep the engineer brain happy
- Sketchy styling keeps it human

> A good walkthrough should feel like a whiteboard that can run.

\`\`\`js
const idea = "draw, explain, execute";
console.log(idea);
\`\`\``;

const diagramSample = `flowchart
Idea --> Markdown
Idea --> Whiteboard
Markdown --> Presentation
Whiteboard --> Presentation
Presentation --> Python

chart: Demo energy
Markdown: 8
Whiteboard: 9
Browser: 6
Python: 10`;

const pythonSample = `from statistics import mean

scores = {"markdown": 8, "whiteboard": 9, "browser": 6, "python": 10}
print("Doodle code score:", round(mean(scores.values()), 2))
for name, score in scores.items():
    print(f"{name:10} " + "#" * score)`;

const slides = [
  {
    title: "Opening sketch",
    markdown: markdownSample,
    diagram: diagramSample,
    python: pythonSample
  },
  {
    title: "Architecture map",
    markdown: "## One page, many surfaces\n\nUse the tabs to move between notes, drawing, live pages, diagrams, charts, and Python output.",
    diagram: "flowchart\nPresenter --> Markdown\nPresenter --> Canvas\nPresenter --> Browser\nPresenter --> Python\nPython --> Output\n\nchart: Feature fit\nNotes: 8\nDrawing: 10\nCharts: 7\nCode: 9",
    python: "print('Hello from slide 2')"
  },
  {
    title: "Live demo",
    markdown: "## Run the room\n\n1. Sketch the system\n2. Show the website\n3. Render the flow\n4. Run the tiny proof",
    diagram: diagramSample,
    python: "for n in range(1, 6):\n    print(n, 'squared is', n*n)"
  }
];

let activeSlide = 0;
let activeMode = "markdown";

const markdownInput = $("#markdownInput");
const markdownPreview = $("#markdownPreview");
const diagramInput = $("#diagramInput");
const diagramPreview = $("#diagramPreview");
const pythonInput = $("#pythonInput");
const pythonOutput = $("#pythonOutput");
const slideList = $("#slideList");
const slideCounter = $("#slideCounter");

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  })[char]);
}

function inlineMarkdown(value) {
  return escapeHtml(value)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>")
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
}

function renderMarkdown(source) {
  const lines = source.split("\n");
  let html = "";
  let inList = false;
  let inOrderedList = false;
  let inCode = false;
  let code = [];

  const closeList = () => {
    if (inList) {
      html += "</ul>";
      inList = false;
    }
    if (inOrderedList) {
      html += "</ol>";
      inOrderedList = false;
    }
  };

  for (const line of lines) {
    if (line.startsWith("```")) {
      if (inCode) {
        html += `<pre><code>${escapeHtml(code.join("\n"))}</code></pre>`;
        code = [];
        inCode = false;
      } else {
        closeList();
        inCode = true;
      }
      continue;
    }

    if (inCode) {
      code.push(line);
      continue;
    }

    if (/^###\s+/.test(line)) {
      closeList();
      html += `<h3>${inlineMarkdown(line.replace(/^###\s+/, ""))}</h3>`;
    } else if (/^##\s+/.test(line)) {
      closeList();
      html += `<h2>${inlineMarkdown(line.replace(/^##\s+/, ""))}</h2>`;
    } else if (/^#\s+/.test(line)) {
      closeList();
      html += `<h1>${inlineMarkdown(line.replace(/^#\s+/, ""))}</h1>`;
    } else if (/^[-*]\s+/.test(line)) {
      if (inOrderedList) {
        html += "</ol>";
        inOrderedList = false;
      }
      if (!inList) {
        html += "<ul>";
        inList = true;
      }
      html += `<li>${inlineMarkdown(line.replace(/^[-*]\s+/, ""))}</li>`;
    } else if (/^\d+\.\s+/.test(line)) {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      if (!inOrderedList) {
        html += "<ol>";
        inOrderedList = true;
      }
      html += `<li>${inlineMarkdown(line.replace(/^\d+\.\s+/, ""))}</li>`;
    } else if (/^>\s?/.test(line)) {
      closeList();
      html += `<blockquote>${inlineMarkdown(line.replace(/^>\s?/, ""))}</blockquote>`;
    } else if (line.trim()) {
      closeList();
      html += `<p>${inlineMarkdown(line)}</p>`;
    } else {
      closeList();
    }
  }

  closeList();
  return html;
}

function renderDiagram() {
  diagramPreview.innerHTML = renderDoodleDiagramBlocks(diagramInput.value, {
    idSeed: `slide-${activeSlide}`
  });
}

function saveActiveSlide() {
  const slide = slides[activeSlide];
  slide.markdown = markdownInput.value;
  slide.diagram = diagramInput.value;
  slide.python = pythonInput.value;
}

function loadSlide(index, options = { save: true }) {
  if (options.save) saveActiveSlide();
  activeSlide = Math.max(0, Math.min(index, slides.length - 1));
  const slide = slides[activeSlide];
  markdownInput.value = slide.markdown;
  diagramInput.value = slide.diagram;
  pythonInput.value = slide.python;
  $("#deckTitle").textContent = slide.title;
  pythonOutput.textContent = "Press Run to execute Python locally.";
  renderAll();
}

function renderSlides() {
  slideList.innerHTML = slides.map((slide, index) => `
    <button class="slide-thumb ${index === activeSlide ? "is-active" : ""}" data-slide="${index}">
      <span class="slide-num">${index + 1}</span>
      <span><strong>${escapeHtml(slide.title)}</strong><small>${escapeHtml(slide.markdown.replace(/[#*`>\n]/g, " ").trim().slice(0, 80))}</small></span>
    </button>
  `).join("");
  slideCounter.textContent = `${activeSlide + 1} / ${slides.length}`;
}

function renderAll() {
  markdownPreview.innerHTML = renderMarkdown(markdownInput.value);
  renderDiagram();
  renderSlides();
}

function setMode(mode) {
  activeMode = mode;
  $$(".tab").forEach((tab) => tab.classList.toggle("is-active", tab.dataset.mode === mode));
  $$(".panel").forEach((panel) => panel.classList.toggle("is-active", panel.dataset.panel === mode));
}

function createPresentationMarkup() {
  if (activeMode === "markdown") return `<article class="doodle-content">${renderMarkdown(markdownInput.value)}</article>`;
  if (activeMode === "diagrams") return `<div class="diagram-preview">${diagramPreview.innerHTML}</div>`;
  if (activeMode === "python") return `<pre class="terminal">${escapeHtml(pythonOutput.textContent)}</pre>`;
  if (activeMode === "browser") return `<h1>Browser view</h1><p>${escapeHtml($("#browserUrl").value)}</p>`;
  return `<h1>Whiteboard</h1><p>Your sketch is ready on the canvas in the main workspace.</p>`;
}

function setupWhiteboard() {
  const canvas = $("#whiteboard");
  const ctx = canvas.getContext("2d");
  let drawing = false;
  let ink = "#202124";

  ctx.lineCap = "round";
  ctx.lineJoin = "round";

  const point = (event) => {
    const rect = canvas.getBoundingClientRect();
    const touch = event.touches?.[0];
    const clientX = touch ? touch.clientX : event.clientX;
    const clientY = touch ? touch.clientY : event.clientY;
    return {
      x: (clientX - rect.left) * canvas.width / rect.width,
      y: (clientY - rect.top) * canvas.height / rect.height
    };
  };

  const start = (event) => {
    drawing = true;
    const p = point(event);
    ctx.beginPath();
    ctx.moveTo(p.x, p.y);
    event.preventDefault();
  };

  const move = (event) => {
    if (!drawing) return;
    const p = point(event);
    ctx.strokeStyle = ink;
    ctx.lineWidth = Number($("#brushSize").value);
    ctx.lineTo(p.x, p.y);
    ctx.stroke();
    event.preventDefault();
  };

  const stop = () => {
    drawing = false;
  };

  canvas.addEventListener("mousedown", start);
  canvas.addEventListener("mousemove", move);
  window.addEventListener("mouseup", stop);
  canvas.addEventListener("touchstart", start, { passive: false });
  canvas.addEventListener("touchmove", move, { passive: false });
  window.addEventListener("touchend", stop);

  $$("input[name='ink']").forEach((input) => {
    input.addEventListener("change", () => {
      ink = input.value;
      $$(".swatch").forEach((label) => label.classList.toggle("active", label.contains(input)));
    });
  });

  $("#clearCanvas").addEventListener("click", () => ctx.clearRect(0, 0, canvas.width, canvas.height));
}

async function runPython() {
  pythonOutput.textContent = "Running...";
  try {
    const response = await fetch("/api/python", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: pythonInput.value })
    });
    const result = await response.json();
    const output = [
      result.stdout && `stdout:\n${result.stdout}`,
      result.stderr && `stderr:\n${result.stderr}`,
      `exit: ${result.signal || result.code} in ${result.durationMs}ms`
    ].filter(Boolean).join("\n\n");
    pythonOutput.textContent = output;
  } catch (error) {
    pythonOutput.textContent = `Could not run Python: ${error.message}`;
  }
}

$$(".tab").forEach((tab) => tab.addEventListener("click", () => setMode(tab.dataset.mode)));
markdownInput.addEventListener("input", () => {
  slides[activeSlide].markdown = markdownInput.value;
  renderAll();
});
diagramInput.addEventListener("input", () => {
  slides[activeSlide].diagram = diagramInput.value;
  renderAll();
});
pythonInput.addEventListener("input", () => {
  slides[activeSlide].python = pythonInput.value;
});
$("#deckTitle").addEventListener("input", (event) => {
  slides[activeSlide].title = event.target.textContent.trim() || `Slide ${activeSlide + 1}`;
  renderSlides();
});
slideList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-slide]");
  if (button) loadSlide(Number(button.dataset.slide));
});
$("#prevSlide").addEventListener("click", () => loadSlide(activeSlide - 1));
$("#nextSlide").addEventListener("click", () => loadSlide(activeSlide + 1));
$("#addSlide").addEventListener("click", () => {
  saveActiveSlide();
  slides.push({
    title: `Slide ${slides.length + 1}`,
    markdown: "# New doodle\n\nStart shaping the thought here.",
    diagram: "flowchart\nStart --> Shape\nShape --> Share",
    python: "print('New slide')"
  });
  loadSlide(slides.length - 1);
});
$("#sampleMarkdown").addEventListener("click", () => {
  markdownInput.value = markdownSample;
  slides[activeSlide].markdown = markdownSample;
  renderAll();
});
$("#sampleDiagram").addEventListener("click", () => {
  diagramInput.value = diagramSample;
  slides[activeSlide].diagram = diagramSample;
  renderAll();
});
$("#runPython").addEventListener("click", runPython);
$("#loadBrowser").addEventListener("click", () => {
  let url = $("#browserUrl").value.trim();
  if (url && !/^https?:\/\//i.test(url)) url = `https://${url}`;
  $("#browserUrl").value = url;
  $("#browserFrame").src = url;
});
$("#presentBtn").addEventListener("click", () => {
  saveActiveSlide();
  $("#presentCard").innerHTML = createPresentationMarkup();
  $("#presentOverlay").hidden = false;
});
$("#closePresent").addEventListener("click", () => {
  $("#presentOverlay").hidden = true;
});

setupWhiteboard();
loadSlide(0, { save: false });
