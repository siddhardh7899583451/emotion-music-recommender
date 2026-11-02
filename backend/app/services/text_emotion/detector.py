"""Text emotion recognition using lexicon + keyword scoring (no heavy downloads)."""
from __future__ import annotations

import logging
import re
from collections import defaultdict
from typing import Dict, Tuple

from app.schemas.emotion import EmotionPrediction, TextEmotionResponse

logger = logging.getLogger(__name__)

TEXT_EMOTIONS = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]

# Lightweight curated lexicon (English). Extendable.
LEXICON: Dict[str, Dict[str, float]] = {
    "happy": {
        "happy": 1.0, "joy": 1.0, "joyful": 0.9, "delighted": 0.9, "excited": 0.85,
        "great": 0.7, "awesome": 0.8, "wonderful": 0.85, "love": 0.8, "loved": 0.75,
        "amazing": 0.8, "fantastic": 0.85, "cheerful": 0.8, "glad": 0.75, "pleased": 0.7,
        "smile": 0.6, "laugh": 0.7, "fun": 0.65, "blessed": 0.7, "grateful": 0.65,
        "yay": 0.8, "haha": 0.6, "lol": 0.55, "❤️": 0.9, "😊": 0.9, "😄": 0.9, "🎉": 0.85,
    },
    "sad": {
        "sad": 1.0, "unhappy": 0.9, "depressed": 0.95, "miserable": 0.9, "lonely": 0.85,
        "cry": 0.8, "crying": 0.85, "tears": 0.75, "heartbroken": 0.95, "grief": 0.9,
        "sorrow": 0.85, "disappointed": 0.75, "hopeless": 0.85, "down": 0.6, "blue": 0.55,
        "miss": 0.5, "missing": 0.55, "pain": 0.7, "hurt": 0.7, "😢": 0.9, "😭": 0.95, "💔": 0.9,
    },
    "angry": {
        "angry": 1.0, "mad": 0.9, "furious": 0.95, "rage": 0.95, "hate": 0.9,
        "annoyed": 0.75, "irritated": 0.8, "frustrated": 0.8, "pissed": 0.9,
        "outrage": 0.85, "disgusted": 0.7, "kill": 0.6, "stupid": 0.55, "idiot": 0.6,
        "🤬": 0.95, "😡": 0.95, "😠": 0.9,
    },
    "fear": {
        "fear": 1.0, "afraid": 0.9, "scared": 0.9, "terrified": 0.95, "anxious": 0.8,
        "worry": 0.7, "worried": 0.75, "panic": 0.9, "nervous": 0.7, "dread": 0.85,
        "horror": 0.85, "threat": 0.7, "danger": 0.7, "frightened": 0.9, "😨": 0.9, "😱": 0.95,
    },
    "surprise": {
        "surprise": 1.0, "surprised": 0.95, "shocked": 0.9, "amazed": 0.85, "wow": 0.8,
        "unexpected": 0.75, "astonished": 0.85, "unbelievable": 0.8, "omg": 0.75,
        "whoa": 0.7, "incredible": 0.7, "😲": 0.9, "😮": 0.85, "‼️": 0.7,
    },
    "disgust": {
        "disgust": 1.0, "disgusting": 0.95, "gross": 0.85, "nasty": 0.8, "revolting": 0.9,
        "sick": 0.6, "yuck": 0.85, "ew": 0.8, "repulsive": 0.9, "🤢": 0.95, "🤮": 0.95,
    },
    "neutral": {
        "okay": 0.5, "ok": 0.5, "fine": 0.45, "alright": 0.5, "normal": 0.6,
        "average": 0.5, "meh": 0.6, "whatever": 0.5, "nothing": 0.4,
    },
}


class TextEmotionService:
    def __init__(self) -> None:
        # Invert lexicon for faster lookup
        self.word_to_emotion: Dict[str, list] = defaultdict(list)
        for emotion, words in LEXICON.items():
            for word, weight in words.items():
                self.word_to_emotion[word.lower()].append((emotion, weight))

    def _clean(self, text: str) -> str:
        text = text.lower().strip()
        # Keep emojis, remove URLs and mentions
        text = re.sub(r"http\S+|www\.\S+", " ", text)
        text = re.sub(r"@\w+", " ", text)
        text = re.sub(r"#(\w+)", r"\1", text)
        return text

    def predict(self, text: str) -> EmotionPrediction:
        cleaned = self._clean(text)
        if not cleaned or len(cleaned) < 2:
            return EmotionPrediction(
                emotion="neutral",
                confidence=0.5,
                scores={e: 1.0 / len(TEXT_EMOTIONS) for e in TEXT_EMOTIONS},
                modality="text",
                message="Empty or too short input.",
            )

        scores = {e: 0.0 for e in TEXT_EMOTIONS}
        tokens = re.findall(r"[\w']+|[\U0001F300-\U0001F9FF]", cleaned)

        matched = 0
        for tok in tokens:
            if tok in self.word_to_emotion:
                matched += 1
                for emotion, weight in self.word_to_emotion[tok]:
                    scores[emotion] += weight

        # Mild boost from polarity keywords
        if any(w in cleaned for w in ("not happy", "not good", "unhappy")):
            scores["sad"] += 0.6
            scores["happy"] *= 0.3
        if any(w in cleaned for w in ("so happy", "very happy", "extremely happy")):
            scores["happy"] += 0.5

        if matched == 0:
            # Fallback neutral
            scores["neutral"] = 1.0
        else:
            # Add small prior
            for e in TEXT_EMOTIONS:
                scores[e] += 0.05

        total = sum(scores.values()) or 1.0
        scores = {k: v / total for k, v in scores.items()}
        emotion = max(scores, key=scores.get)
        confidence = scores[emotion]

        # Cap confidence when few matches
        if matched < 2:
            confidence = min(confidence, 0.55)

        return EmotionPrediction(
            emotion=emotion,
            confidence=round(float(confidence), 4),
            scores={k: round(v, 4) for k, v in scores.items()},
            modality="text",
        )

    def detect(self, text: str) -> TextEmotionResponse:
        if not text or not text.strip():
            return TextEmotionResponse(success=False, message="Text cannot be empty.")
        try:
            pred = self.predict(text)
            return TextEmotionResponse(success=True, prediction=pred, message="Text analysed.")
        except Exception as exc:
            logger.exception("Text emotion error")
            return TextEmotionResponse(success=False, message=str(exc))


text_service = TextEmotionService()
