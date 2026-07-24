from types import SimpleNamespace

from app.services.labels import effective_label_map, effective_labels_for_track


class FakeScalars:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


class FakeSession:
    def __init__(self):
        self.calls = 0
        self.inferred = [
            SimpleNamespace(dimension="mood", value="romantic", confidence=0.8, evidence={"rule": "test"}),
            SimpleNamespace(dimension="language", value="Telugu", confidence=0.8, evidence={"rule": "test"}),
        ]
        self.overrides = [
            SimpleNamespace(id=1, dimension="mood", value="calm", reason="owner correction"),
        ]

    def scalars(self, _statement):
        self.calls += 1
        return FakeScalars(self.inferred if self.calls == 1 else self.overrides)


def test_effective_labels_keep_inferred_evidence_and_overlay_override() -> None:
    labels = effective_labels_for_track(FakeSession(), 1)

    assert {"dimension": "language", "value": "Telugu", "confidence": 0.8, "evidence": {"rule": "test"}, "source": "inferred"} in labels
    assert {"dimension": "mood", "value": "calm", "confidence": 1.0, "evidence": {"override_id": 1, "reason": "owner correction"}, "source": "override"} in labels
    assert all(label["value"] != "romantic" for label in labels)


def test_effective_label_map_uses_override_value() -> None:
    labels = effective_label_map(FakeSession(), 1)

    assert labels["mood"] == {"calm"}
    assert labels["language"] == {"Telugu"}
