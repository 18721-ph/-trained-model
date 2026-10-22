"""Check preserved files and script paths without importing training scripts."""

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def destination(original, moves):
    for old, new in moves.items():
        if original == old or original.startswith(old + "/"):
            return new + original[len(old):]
    return original


def main():
    inventory = json.loads((ROOT / "docs/notes/inventory-before.json").read_text())
    moves = json.loads((ROOT / "docs/notes/moves.json").read_text())
    missing = [item["path"] for item in inventory["all_files"]
               if not (ROOT / destination(item["path"], moves)).is_file()]
    assert not missing, f"Missing original files: {missing}"

    changed = []
    for item in inventory["project_files"]:
        path = ROOT / destination(item["path"], moves)
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            changed.append(item["path"])
    protected = ("model/", "data/", "api/", "src/", "test/", "frontend/src/", "frontend/public/")
    assert not any(name.startswith(protected) for name in changed), changed

    checked = []
    for folder in ("experiments", "scripts", "analysis", "api", "src", "tests"):
        for path in (ROOT / folder).rglob("*.py"):
            tree = ast.parse(path.read_text(), filename=str(path))
            namespace = {"Path": Path, "__file__": str(path)}
            # Evaluate only file-location constants, never training or inference.
            for node in tree.body:
                if isinstance(node, ast.Assign) and len(node.targets) == 1:
                    target = node.targets[0]
                    if isinstance(target, ast.Name) and target.id in {
                        "BASE_DIR", "PROJECT_ROOT", "MODEL_DIR", "DATA_PATH",
                        "BASE_MODEL_PATH", "CALIBRATED_MODEL_PATH", "METADATA_PATH",
                    }:
                        value = eval(compile(ast.Expression(node.value), str(path), "eval"), namespace)
                        namespace[target.id] = value
                        assert value.exists(), (path, target.id, value)
                for call in ast.walk(node):
                    if (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                            and call.func.attr == "read_csv"):
                        value = eval(compile(ast.Expression(call.args[0]), str(path), "eval"), namespace)
                        assert Path(value).is_absolute() and Path(value).is_file(), (path, value)
            checked.append(path.relative_to(ROOT).as_posix())

    result = {"original_files_accounted_for": len(inventory["all_files"]),
              "missing_files": missing, "changed_original_files": changed,
              "python_files_checked": checked,
              "protected_files_unchanged": True}
    (ROOT / "docs/notes/verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
