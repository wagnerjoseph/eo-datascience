from pathlib import Path

import yaml
from packaging.version import parse


def main():
    root = Path("notebooks").resolve()
    print(root, root.exists())
    files = list(root.glob("**/*.yml"))
    files.append(root.parent / "environment.yml")

    dependencies = set()
    fixed_dependencies = dict()

    for file in files:
        with file.open("r") as f:
            environment = yaml.safe_load(f)

        for d in environment.get("dependencies", []):
            parts = d.split("=")
            name = parts[0]

            if len(parts) > 1:
                version = parts[-1]
                if name in fixed_dependencies:
                    fixed_dependencies[name].append(version)
                else:
                    fixed_dependencies[name] = [version]

            dependencies.add(name)

    # Update dependencies set with latest versions
    final_dependencies = set()
    for name in dependencies:
        if name in fixed_dependencies:
            latest_version = max(fixed_dependencies[name], key=parse)
            final_dependencies.add(f"{name}={latest_version}")
        else:
            final_dependencies.add(name)

    # Create master YAML file
    master_env = {
        "name": "eo-datascience",
        "channels": ["conda-forge"],
        "dependencies": sorted(final_dependencies),
    }
    yaml_file = "environment.yml"
    with open(yaml_file, "w") as f:
        yaml.dump(
            master_env,
            f,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
            width=80,
        )

    # Dirty fix: Read the file and add two spaces before
    with open(yaml_file, "r") as f:
        lines = f.readlines()

    with open(yaml_file, "w") as f:
        for line in lines:
            if line.strip().startswith("-"):
                f.write("  " + line)  # Add two spaces before the line
            else:
                f.write(line)

    print("Master environment file created successfully.")


if __name__ == "__main__":
    main()
