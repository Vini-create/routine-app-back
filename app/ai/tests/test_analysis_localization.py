import pytest

from app.ai.graph.nodes.analysis import (
    diagnose_execution_node,
    identify_patterns_node,
)


@pytest.mark.anyio
async def test_feedbacker_structured_metric_cards_are_localized_in_portuguese() -> None:
    state = {
        "response_language": "pt-BR",
        "habit_metrics": {
            "summary": {
                "expected_count": 10,
                "completed_count": 7,
                "completion_rate": 0.7,
            },
            "window": {"start_date": "2026-07-01", "end_date": "2026-07-07"},
        },
        "detected_trends": [
            {"type": "completion_rate", "direction": "down", "delta": -0.2},
        ],
        "detected_anomalies": [
            {"type": "missed_schedule", "severity": "medium", "evidence": {}},
        ],
    }

    diagnosis = await diagnose_execution_node(state)
    patterns = await identify_patterns_node(state)

    assert diagnosis["execution_diagnosis"]["summary"].startswith("7 de 10")
    assert diagnosis["execution_diagnosis"]["observed_facts"] == [
        "ocorrências_planejadas=10",
        "ocorrências_concluídas=7",
        "taxa_de_conclusão=0.7",
        "tendências_detectadas=1",
        "anomalias_detectadas=1",
    ]
    # Pattern identifiers stay machine-readable because the frontend maps them
    # to translated visual cards; only the expanded technical payload is raw.
    assert patterns["identified_patterns"][0]["name"] == "trend:completion_rate"
    assert patterns["identified_patterns"][1]["name"] == "anomaly:missed_schedule"
