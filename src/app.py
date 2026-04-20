import os
import textwrap
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request
from agents.orchestrator import OrchestratorAgent

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = ImageDraw = ImageFont = None

app = Flask(__name__)

orchestrator = OrchestratorAgent()

SCREENSHOT_DIR = Path(__file__).resolve().parent / "screenshot"
SCREENSHOT_DIR.mkdir(exist_ok=True)

FLOWS = [
    "Login & Account Overview",
    "Fund Transfer",
    "Bill Payment",
    "User Registration",
]

@app.route("/", methods=["GET", "POST"])
def index():
    selected_flow = FLOWS[0]
    description = ""
    outputs = {
        "gherkin": "",
        "playwright": "",
        "coverage": "",
    }

    screenshot_message = ""

    if request.method == "POST":
        selected_flow = request.form.get("flow", selected_flow)
        description = request.form.get("description", "").strip()
        action = request.form.get("action", "generate_all")

        if action == "generate_gherkin":
            outputs["gherkin"] = orchestrator.gherkin_agent.generate(selected_flow, description)
        elif action == "generate_playwright":
            gherkin_text = orchestrator.gherkin_agent.generate(selected_flow, description)
            outputs["gherkin"] = gherkin_text
            outputs["playwright"] = orchestrator.script_agent.generate(gherkin_text)
        elif action == "coverage_gaps":
            gherkin_text = orchestrator.gherkin_agent.generate(selected_flow, description)
            outputs["gherkin"] = gherkin_text
            outputs["coverage"] = orchestrator.coverage_agent.analyze(description, gherkin_text)
        elif action == "generate_all":
            result = orchestrator.orchestrate(selected_flow, description)
            outputs["gherkin"] = result["gherkin"]
            outputs["playwright"] = result["script"]
            outputs["coverage"] = result["coverage"]

        screenshot_path = capture_screenshot(selected_flow, description, outputs)
        if screenshot_path:
            screenshot_message = f"Screenshot captured successfully: {os.path.basename(screenshot_path)}"

    return render_template(
        "index.html",
        flows=FLOWS,
        selected_flow=selected_flow,
        description=description,
        outputs=outputs,
        screenshot_message=screenshot_message,
    )


def capture_screenshot(selected_flow: str, description: str, outputs: dict) -> str | None:
    if Image is None or ImageDraw is None or ImageFont is None:
        return None

    def safe_text(value: str, prefix: str = "") -> str:
        if not value:
            return "None"
        text = value.strip()
        if len(text) > 600:
            text = text[:600].rstrip() + "..."
        return f"{prefix}{text}"

    filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    path = SCREENSHOT_DIR / filename

    width, height = 1200, 920
    background = (15, 23, 42)
    image = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    margin = 40
    line_height = 22
    current_y = margin

    title = "Parabank AI Test Assistant"
    draw.text((margin, current_y), title, fill=(255, 255, 255), font=font)
    current_y += 40

    draw.text((margin, current_y), f"Flow: {selected_flow}", fill=(165, 180, 252), font=font)
    current_y += line_height + 6
    draw.text((margin, current_y), f"Description:", fill=(148, 163, 184), font=font)
    current_y += line_height
    for line in textwrap.wrap(description or "No description provided.", width=90):
        draw.text((margin + 16, current_y), line, fill=(226, 232, 240), font=font)
        current_y += line_height
    current_y += 12

    for label, text in [("Gherkin", outputs.get("gherkin", "")), ("Playwright", outputs.get("playwright", "")), ("Coverage", outputs.get("coverage", ""))]:
        draw.text((margin, current_y), f"{label}:", fill=(148, 163, 184), font=font)
        current_y += line_height
        for line in textwrap.wrap(text or "No output generated.", width=90):
            draw.text((margin + 16, current_y), line, fill=(226, 232, 240), font=font)
            current_y += line_height
        current_y += 12
        if current_y > height - 120:
            break

    image.save(path)
    return str(path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
