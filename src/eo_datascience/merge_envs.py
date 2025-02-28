from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

import yaml
from packaging.version import parse


def collect_yaml_files(root: Path) -> List[Path]:
    files = list(root.glob("**/*.yml"))
    files.append(root.parent / "environment.yml")
    return files


def get_environment_from_yml(file: Path) -> Dict:
    with file.open("r") as f:
        environment = yaml.safe_load(f)
    return environment


def aggregate_env_dependencies(files: List[Path]) -> List[str]:
    unrefined_dependencies: List = []
    for file in files:
        environment = get_environment_from_yml(file)
        unrefined_dependencies.extend(environment.get("dependencies", []))
    return unrefined_dependencies


def extract_unique_dependencies(dep: List[str]) -> Tuple[Set, Dict]:
    dependencies = set()
    multi_versions = dict()
    for d in dep:
        parts = d.split("=")
        name = parts[0]
        dependencies.add(name)
        # Check if version is specified
        if len(parts) > 1:
            version = parts[-1]
            if name in multi_versions:
                multi_versions[name].append(version)
            else:
                multi_versions[name] = [version]
    return dependencies, multi_versions


def resolve_dependency_versions(
    unique_dependencies: Iterable, multi_versions: Dict
) -> Set:
    final_dependencies = set()
    for name in unique_dependencies:
        if name in multi_versions:
            latest_version = max(multi_versions[name], key=parse)
            final_dependencies.add(f"{name}={latest_version}")
        else:
            final_dependencies.add(name)
    return final_dependencies


def create_master_environment(final_dependencies: List | Set) -> Dict:
    master_env = {
        "name": "eo-datascience",
        "channels": ["conda-forge"],
        "dependencies": sorted(final_dependencies),
    }
    return master_env


def dump_environment(output_file: str | Path, master_env: Dict) -> None:
    with open(output_file, "w") as f:
        yaml.dump(
            master_env,
            f,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
            width=80,
        )


def fix_yml_indentation(output_file):
    with open(output_file, "r") as f:
        lines = f.readlines()

    with open(output_file, "w") as f:
        for line in lines:
            if line.strip().startswith("-"):
                f.write("  " + line)  # Add two spaces before the line
            else:
                f.write(line)


def main(output_file: str | Path = "environment.yml") -> None:
    root = Path("notebooks").resolve()
    files = collect_yaml_files(root)

    # Collect all dependencies from all YAML files
    unrefined_dependencies = aggregate_env_dependencies(files)

    unique_dependencies, multi_versions = extract_unique_dependencies(
        unrefined_dependencies
    )
    # Update dependencies set with latest versions
    final_dependencies = resolve_dependency_versions(
        unique_dependencies, multi_versions
    )

    # Create master YAML file
    master_env = create_master_environment(final_dependencies)
    dump_environment(output_file, master_env)

    # Dirty fix: Read the file and add two spaces before
    fix_yml_indentation(output_file)
    print("Master environment file created successfully.")


if __name__ == "__main__":
    main(output_file="environment.yml")
