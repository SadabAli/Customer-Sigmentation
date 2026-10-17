from pathlib import Path
import os
import json

import joblib
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google import genai
from filters import markdown_to_html

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

MODEL_PATH = BASE_DIR / "customer_segment_classifier.joblib"
if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model file not found: {MODEL_PATH}. Copy your saved .joblib file into this project folder."
    )

model = joblib.load(MODEL_PATH)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip()
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

app = FastAPI(title="Segmenza AI | Customer Intelligence")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
templates.env.filters["markdown_to_html"] = markdown_to_html

FEATURE_COLUMNS = [
    "Age", "PurchaseAmountUSD", "PreviousPurchases", "Category",
    "SubscriptionStatus", "DiscountApplied", "PromoCodeUsed", "FrequencyOfPurchases"
]

# Dataset categories: edit these lists if your training dataset uses different values.
CATEGORIES = ["Accessories", "Clothing", "Footwear", "Outerwear"]
FREQUENCIES = ["Weekly", "Fortnightly", "Monthly", "Quarterly", "Every 3 Months", "Annually"]


def segment_fallback(cluster: int, customer: dict) -> str:
    """A cautious local fallback if Gemini is not configured or unavailable."""
    spend = customer["PurchaseAmountUSD"]
    previous = customer["PreviousPurchases"]
    if spend < 180:
        profile = "lower-spend customer in this input"
        action = "Test relevant product bundles and value-focused offers; validate response before scaling."
    elif previous >= 8:
        profile = "repeat customer in this input"
        action = "Consider a loyalty or replenishment message, and measure incremental response."
    else:
        profile = "higher-spend or developing customer in this input"
        action = "Consider relevant cross-sell recommendations and test engagement before broad rollout."
    return (
        f"### Predicted segment\nThe model assigned this customer to **Cluster {cluster}**. "
        f"Cluster IDs are labels, not rankings.\n\n### Input-based observation\nBased only on the entered values, this customer looks like a {profile}. "
        "This observation is not the definition of the cluster; compare it with the actual cluster profile.\n\n"
        f"### Possible next action\n{action}\n\n### Caution\nThis is a model prediction, not a guarantee of customer behaviour or campaign performance."
    )


def generate_ai_insight(cluster: int, customer: dict) -> tuple[str, bool]:
    if not gemini_client:
        return (
            "### Gemini is not configured\nAdd `GEMINI_API_KEY` to your local `.env` file and restart the server. "
            "A local fallback insight is shown below for now.\n\n" + segment_fallback(cluster, customer),
            False,
        )

    prompt = f"""You are a careful customer analytics assistant explaining a machine-learning result.
The Random Forest classifier predicted Cluster {cluster} for the customer below.
Customer inputs (JSON): {json.dumps(customer, ensure_ascii=False)}

Write concise Markdown with these headings:
### Predicted segment
Explain that Cluster {cluster} is the model output and cluster numbers are arbitrary labels, not rankings.
### What the inputs suggest
Describe only cautious observations supported by the supplied inputs. Do not claim these inputs define the cluster unless stated.
### Possible marketing experiments
Give 2 practical, low-risk ideas and say to measure results. Avoid guarantees and manipulative tactics.
### Limitations
State that this is not proof of future behaviour, profitability, causation, or campaign success. Do not invent cluster averages, dataset statistics, or model explanations not provided.
Use plain language and stay under 180 words."""
    try:
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response")
        return text, True
    except Exception as exc:
        # Don't expose API keys or raw provider error details in the UI.
        return (
            "### Gemini could not generate an insight\nCheck your API key, model name, network connection, and API quota. "
            "The local fallback insight is shown instead.\n\n" + segment_fallback(cluster, customer),
            False,
        )


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "categories": CATEGORIES,
            "frequencies": FREQUENCIES,
            "gemini_ready": bool(gemini_client),
        },
    )


@app.post("/predict", response_class=HTMLResponse)
def predict(
    request: Request,
    Age: int = Form(...),
    PurchaseAmountUSD: float = Form(...),
    PreviousPurchases: int = Form(...),
    Category: str = Form(...),
    SubscriptionStatus: str = Form(...),
    DiscountApplied: str = Form(...),
    PromoCodeUsed: str = Form(...),
    FrequencyOfPurchases: str = Form(...),
):
    if not 18 <= Age <= 100:
        return HTMLResponse("Age must be between 18 and 100. Go back and try again.", status_code=422)
    if PurchaseAmountUSD < 0 or PreviousPurchases < 0:
        return HTMLResponse("Purchase amount and previous purchases cannot be negative.", status_code=422)
    if Category not in CATEGORIES or FrequencyOfPurchases not in FREQUENCIES:
        return HTMLResponse("Please select a valid category and purchase frequency.", status_code=422)

    customer = {
        "Age": Age,
        "PurchaseAmountUSD": PurchaseAmountUSD,
        "PreviousPurchases": PreviousPurchases,
        "Category": Category,
        "SubscriptionStatus": SubscriptionStatus,
        "DiscountApplied": DiscountApplied,
        "PromoCodeUsed": PromoCodeUsed,
        "FrequencyOfPurchases": FrequencyOfPurchases,
    }
    row = pd.DataFrame([customer], columns=FEATURE_COLUMNS)
    cluster = int(model.predict(row)[0])
    insight, used_gemini = generate_ai_insight(cluster, customer)

    probabilities = []
    if hasattr(model, "predict_proba"):
        try:
            probs = model.predict_proba(row)[0]
            classes = getattr(model, "classes_", range(len(probs)))
            probabilities = [
                {"label": str(label), "percent": round(float(prob) * 100, 1)}
                for label, prob in zip(classes, probs)
            ]
            probabilities.sort(key=lambda x: x["percent"], reverse=True)
        except Exception:
            probabilities = []

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "customer": customer,
            "cluster": cluster,
            "insight": insight,
            "used_gemini": used_gemini,
            "probabilities": probabilities,
        },
    )


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True, "gemini_configured": bool(gemini_client)}
