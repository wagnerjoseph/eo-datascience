from pathlib import Path
from unittest.mock import patch

import pytest  # noqa
from eo_datascience import merge_envs


def test_create_master_environment_returns_correct():
    dependencies = ["numpy", "pandas", "matplotlib==3.2.2"]
    expected_result = {
        "name": "eo-datascience",
        "channels": ["conda-forge"],
        "dependencies": ["matplotlib==3.2.2", "numpy", "pandas"],
    }

    actual_result = merge_envs.create_master_environment(
        dependencies, name="eo-datascience"
    )
    assert actual_result == expected_result


def test_resolve_dependency_versions_returns_correct():
    dependencies = ["numpy", "pandas", "matplotlib"]
    multiple_versions = {"matplotlib": ["3.2.2", "3.3.0", "3.3.1"]}
    expected_result = {"matplotlib=3.3.1", "numpy", "pandas"}
    actual_result = merge_envs.resolve_dependency_versions(
        dependencies, multiple_versions
    )
    assert actual_result == expected_result


def test_extract_unique_dependencies_returns_correct():
    dependencies = ["numpy", "pandas", "matplotlib==3.2.2"]
    expected_result = (
        {"numpy", "pandas", "matplotlib"},
        {"matplotlib": ["3.2.2"]},
    )
    actual_result = merge_envs.extract_unique_dependencies(dependencies)
    assert actual_result == expected_result


@patch("eo_datascience.merge_envs.get_environment_from_yml")
def test_aggregate_env_dependencies_returns_correct(mock_get_env):
    env1 = {"dependencies": ["numpy==3.2.1", "pandas", "xarray"]}
    env2 = {"dependencies": ["numpy=3.4.5", "pandas", "seaborn"]}
    # Setting the return values of calling `get_environment_from_yml` two times
    mock_get_env.side_effect = [env1, env2]

    # Create dummy file paths
    files = [Path("env1.yml"), Path("env2.yml")]

    result = merge_envs.aggregate_env_dependencies(files)

    expected = [
        "numpy==3.2.1",
        "pandas",
        "xarray",
        "numpy=3.4.5",
        "pandas",
        "seaborn",
    ]
    assert result == expected
