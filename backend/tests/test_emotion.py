"""Unit tests for emotion services and fusion.

Run from backend/:
  set PYTHONPATH=.
  pytest tests -v
"""
import numpy as np
import pytest

from app.services.text_emotion.detector import text_service
from app.services.emotion_fusion.fusion import fusion_service
from app.schemas.emotion import MultimodalRequest
from app.services.music_recommendation.engine import music_engine


def test_text_happy():
    resp = text_service.detect("I am so happy and excited today!")
    assert resp.success
    assert resp.prediction.emotion == "happy"
    assert resp.prediction.confidence > 0.3


def test_text_sad():
    resp = text_service.detect("I feel so sad and lonely, I want to cry")
    assert resp.success
    assert resp.prediction.emotion == "sad"


def test_text_empty():
    resp = text_service.detect("")
    assert not resp.success


def test_text_angry():
    resp = text_service.detect("I am so angry and furious about this!")
    assert resp.success
    assert resp.prediction.emotion == "angry"


def test_fusion_single_modality():
    req = MultimodalRequest(face_emotion="happy", face_confidence=0.9)
    res = fusion_service.fuse(req)
    assert res.success
    assert res.fused_emotion == "happy"
    assert "face" in res.modalities_used


def test_fusion_all_modalities():
    req = MultimodalRequest(
        face_emotion="happy",
        face_confidence=0.85,
        audio_emotion="neutral",
        audio_confidence=0.7,
        text_emotion="happy",
        text_confidence=0.9,
    )
    res = fusion_service.fuse(req)
    assert res.success
    assert res.fused_emotion == "happy"
    assert len(res.modalities_used) == 3


def test_fusion_conflict_high_confidence_wins():
    req = MultimodalRequest(
        face_emotion="sad",
        face_confidence=0.9,
        text_emotion="happy",
        text_confidence=0.4,
    )
    res = fusion_service.fuse(req)
    assert res.success
    assert res.fused_emotion == "sad"


def test_fusion_empty():
    req = MultimodalRequest()
    res = fusion_service.fuse(req)
    assert not res.success


def test_music_recommend_happy():
    songs = music_engine.recommend("happy", language="English", limit=5)
    assert len(songs) > 0
    assert all("title" in s for s in songs)


def test_music_recommend_sad_hindi():
    songs = music_engine.recommend("sad", language="Hindi", limit=3)
    assert len(songs) >= 1
    assert all(s.get("language") == "Hindi" for s in songs)


def test_music_search():
    results = music_engine.search(query="happy")
    assert isinstance(results, list)


def test_music_filters():
    langs = music_engine.all_languages()
    assert len(langs) > 0


def test_face_service_no_crash_on_blank():
    cv2 = pytest.importorskip("cv2")
    from app.services.face_emotion.detector import face_service

    img = np.zeros((64, 64, 3), dtype=np.uint8)
    _, buf = cv2.imencode(".jpg", img)
    res = face_service.detect_from_image_bytes(buf.tobytes())
    # success True with 0 faces, or False if cascade unavailable — both OK
    assert res.faces_detected == 0 or res.success is False


def test_audio_too_short():
    pytest.importorskip("librosa")
    from app.services.audio_emotion.detector import audio_service

    y = np.zeros(1000, dtype=np.float32)
    with pytest.raises(ValueError):
        audio_service.extract_features(y, 22050)
