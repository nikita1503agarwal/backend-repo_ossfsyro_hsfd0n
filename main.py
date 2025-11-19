import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from database import create_document, get_documents, db

app = FastAPI(title="Krishna GPT API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=2, description="Arjuna's question")
    conversation_id: Optional[str] = Field(None, description="Conversation identifier")


class AskResponse(BaseModel):
    answer: str
    verse: Optional[str] = None
    chapter: Optional[str] = None
    reference: Optional[str] = None
    image_url: Optional[str] = None


# Minimal curated mapping of themes to verses and teachings
# Note: Short verse excerpts used for educational reference, encourage readers to consult full text
GITA_KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "keywords": ["duty", "dharma", "work", "karma", "action", "responsibility"],
        "chapter": "2.47",
        "verse": "karmaṇy-evādhikāras te mā phaleṣhu kadāchana",
        "reference": "Bhagavad-gītā 2.47",
        "teaching": (
            "O Arjuna, your right is to perform your prescribed duty, but never to the fruits. Perform your work as an offering to Me, free from attachment and anxiety. When action is done in devotion, peace follows like a cool moonlight on a clear night."
        ),
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/08/Kurukshetra_Bhagavad_Gita.jpg",
    },
    {
        "keywords": ["surrender", "take shelter", "refuge", "give up", "fear", "deliver", "save"],
        "chapter": "18.66",
        "verse": "sarva-dharmān parityajya mām ekaṁ śharaṇaṁ vraja",
        "reference": "Bhagavad-gītā 18.66",
        "teaching": (
            "Abandon all varieties of duty and simply take shelter of Me. I shall deliver you from all reactions; do not fear. Offer your heart to Me with trust—when the child holds the father's hand, the road becomes safe."
        ),
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/4d/Krishna_and_Arjuna.jpg",
    },
    {
        "keywords": ["mind", "control", "meditation", "yoga", "practice", "abhyasa", "vairagya"],
        "chapter": "6.35",
        "verse": "asaṁśayaṁ mahā-bāho mano durnigrahaṁ chalam",
        "reference": "Bhagavad-gītā 6.35",
        "teaching": (
            "The mind is restless and difficult to curb, but by constant practice and detachment it can be controlled. Begin with remembrance of Me—chant My names, hear My glories—and the mind, like a wild river, will gently find the ocean of peace."
        ),
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/77/Krishna_Arjuna.jpg",
    },
    {
        "keywords": ["soul", "atma", "death", "birth", "change", "body", "eternal"],
        "chapter": "2.20",
        "verse": "na jāyate mriyate vā kadācin",
        "reference": "Bhagavad-gītā 2.20",
        "teaching": (
            "The soul is unborn, eternal, ever-existing, and primeval; it is not slain when the body is slain. Grief fades when one knows the self beyond the body—see with wisdom, O Arjuna, and stand steady in your duty."
        ),
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/9a/Bhagavad_Gita_Krishna_Arjuna.jpg",
    },
    {
        "keywords": ["food", "offer", "prayer", "eat", "prasadam", "yajna", "devotion"],
        "chapter": "9.26",
        "verse": "patraṁ puṣhpaṁ phalaṁ toyaṁ yo me bhaktyā prayachchhati",
        "reference": "Bhagavad-gītā 9.26",
        "teaching": (
            "If one offers Me with love a leaf, a flower, fruit, or water, I accept it. Cook and eat as an offering to Me; then even simple fare becomes sanctified, and your heart becomes light and joyful."
        ),
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/17/Krishna_with_flute.jpg",
    },
    {
        "keywords": ["devotion", "bhakti", "love", "serve", "chant", "remember"],
        "chapter": "9.34",
        "verse": "man-manā bhava mad-bhakto",
        "reference": "Bhagavad-gītā 9.34",
        "teaching": (
            "Fix your mind on Me, become My devotee, worship Me, and offer your homage to Me; surely you will come to Me. Keep Me at the center—then your days will become a garland of auspicious moments."
        ),
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0c/Krishna_and_Radha%2C_19_century%2C_India.jpg",
    },
]


@app.get("/")
def read_root():
    return {"message": "Krishna GPT Backend is running"}


@app.get("/api/hello")
def hello():
    return {"message": "Jai Shri Krishna! Ask your question at POST /api/ask"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, "name") else "❌ Unknown"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


def select_teaching(question: str) -> Dict[str, Any]:
    q = question.lower()
    best = None
    best_score = -1
    for item in GITA_KNOWLEDGE_BASE:
        score = sum(1 for k in item["keywords"] if k in q)
        if score > best_score:
            best = item
            best_score = score
    # default to devotion teaching if no keyword matches
    return best or GITA_KNOWLEDGE_BASE[-1]


@app.post("/api/ask", response_model=AskResponse)
async def ask_krishna(req: AskRequest):
    question = req.question.strip()
    if len(question) < 2:
        raise HTTPException(status_code=400, detail="Question is too short")

    teaching = select_teaching(question)

    # Compose Krishna's voice response
    answer = (
        "Dear Arjuna, hear My words with a tranquil heart. "
        + teaching["teaching"]
        + " Engage your duty with devotion, remain steady, and take shelter of Me."
    )

    # Persist messages
    try:
        conversation_id = req.conversation_id or None
        user_msg_id = create_document(
            "message",
            {
                "role": "user",
                "content": question,
                "conversation_id": conversation_id,
            },
        )
        krishna_msg_id = create_document(
            "message",
            {
                "role": "krishna",
                "content": answer,
                "image_url": teaching.get("image_url"),
                "conversation_id": conversation_id,
            },
        )
    except Exception:
        # Database may be unavailable; proceed without failing the request
        user_msg_id = None
        krishna_msg_id = None

    return AskResponse(
        answer=answer,
        verse=teaching.get("verse"),
        chapter=teaching.get("chapter"),
        reference=teaching.get("reference"),
        image_url=teaching.get("image_url"),
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
