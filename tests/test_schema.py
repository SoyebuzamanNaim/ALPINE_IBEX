"""Unit tests for schema validation and unit conversions."""
import pytest
from src.schema.models import ExperimentRecord, convert_units


def test_unit_conversions():
    # Pressure conversions
    assert pytest.approx(convert_units(14.696, "psia", "pressure"), rel=1e-3) == 101.325
    assert pytest.approx(convert_units(1.0, "atm", "pressure"), rel=1e-4) == 101.325
    assert pytest.approx(convert_units(1.0, "bar", "pressure"), rel=1e-4) == 100.0

    # Flow velocity conversions
    assert pytest.approx(convert_units(0.05, "m/s", "flow_velocity"), rel=1e-4) == 5.0
    assert pytest.approx(convert_units(50.0, "mm/s", "flow_velocity"), rel=1e-4) == 5.0

    # Length conversions
    assert pytest.approx(convert_units(1.0, "inch", "length"), rel=1e-4) == 25.4
    assert pytest.approx(convert_units(0.5, "cm", "length"), rel=1e-4) == 5.0


def test_experiment_record_valid():
    rec = ExperimentRecord(
        experiment_id="TEST_01",
        investigation="BASS-II",
        material="PMMA",
        material_raw="100-um PMMA sheet",
        sample_geometry="sheet",
        sample_thickness_mm=0.1,
        oxygen_pct=21.0,
        pressure_kpa=101.3,
        flow_cm_s=5.0,
        flow_direction="opposed",
        outcome="spread",
        outcome_raw="Steady flame spread",
        gravity_env="ISS",
        report_id="20210011385",
        source_url="https://ntrs.nasa.gov/citations/20210011385",
        source_page=103,
        source_table="Table A.1",
        extraction_method="table_parsed"
    )
    assert rec.material == "PMMA"
    assert rec.oxygen_pct == 21.0
    assert rec.outcome == "spread"


def test_experiment_record_invalid_url():
    with pytest.raises(ValueError):
        ExperimentRecord(
            experiment_id="TEST_02",
            investigation="BASS-II",
            material="PMMA",
            material_raw="PMMA",
            sample_geometry="rod",
            oxygen_pct=21.0,
            pressure_kpa=101.3,
            flow_cm_s=5.0,
            flow_direction="opposed",
            outcome="spread",
            outcome_raw="Spread",
            gravity_env="ISS",
            report_id="20210011385",
            source_url="invalid_url_without_scheme",
            extraction_method="table_parsed"
        )
