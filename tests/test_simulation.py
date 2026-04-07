"""Tests for the simulation config generator (Phase 5)."""

from __future__ import annotations

from pathlib import Path


from creator.simulation.config_gen import (
    generate_experiment_configs,
    generate_sim_config,
    list_conditions,
    save_sim_configs,
)


class TestSimConfigGeneration:
    def test_default_config(self):
        config = generate_sim_config()
        assert config["agents"]["count"] == 12
        assert config["simulation"]["max_ticks"] == 100
        assert "world" in config
        assert "resources" in config["world"]

    def test_custom_agents_and_ticks(self):
        config = generate_sim_config(agents=24, ticks=200)
        assert config["agents"]["count"] == 24
        assert config["simulation"]["max_ticks"] == 200

    def test_condition_template(self):
        config = generate_sim_config(condition_name="resource_scarcity")
        assert config["world"]["resources"]["food"]["density"] == 0.1

    def test_direct_overrides(self):
        config = generate_sim_config(
            conditions={"agents.communication_range": 3}
        )
        assert config["agents"]["communication_range"] == 3

    def test_overrides_take_precedence(self):
        config = generate_sim_config(
            condition_name="resource_scarcity",
            conditions={"world.resources.food.density": 0.99},
        )
        assert config["world"]["resources"]["food"]["density"] == 0.99


class TestExperimentConfigs:
    def test_treatment_and_control(self):
        configs = generate_experiment_configs(
            hypothesis="Resource scarcity drives cooperation",
            conditions={"world.resources.food.density": 0.05},
        )
        assert len(configs) == 2
        roles = [c["role"] for c in configs]
        assert "control" in roles
        assert "treatment" in roles

    def test_no_control(self):
        configs = generate_experiment_configs(
            hypothesis="Test",
            control=False,
        )
        assert len(configs) == 1
        assert configs[0]["role"] == "treatment"

    def test_variations(self):
        configs = generate_experiment_configs(
            hypothesis="Test",
            conditions={"agents.count": 20},
            variations=3,
        )
        # 1 control + 1 treatment + 2 extra variations
        assert len(configs) == 4
        roles = [c["role"] for c in configs]
        assert "treatment_v2" in roles
        assert "treatment_v3" in roles

    def test_hypothesis_attached(self):
        configs = generate_experiment_configs(
            hypothesis="Social drive causes cooperation",
        )
        assert all(c["hypothesis"] == "Social drive causes cooperation" for c in configs)


class TestSaveConfigs:
    def test_save_to_disk(self, tmp_path: Path):
        configs = generate_experiment_configs(
            hypothesis="Test",
            conditions={"agents.count": 8},
        )
        paths = save_sim_configs(configs, tmp_path / "sim_configs")
        assert len(paths) == 2
        for p in paths:
            assert Path(p).exists()


class TestListConditions:
    def test_conditions_available(self):
        conditions = list_conditions()
        assert len(conditions) >= 8
        names = [c["name"] for c in conditions]
        assert "resource_scarcity" in names
        assert "communication_limited" in names
