#!/usr/bin/env python3
import argparse
import os
import re
import shutil
import sys
import uuid
import json
from typing import Dict, List, Tuple, Optional


VERSION_OPT_RE = re.compile(r"^--?v(?:ersion)?(\d+)$")


def parse_args(argv: List[str]) -> Tuple[str, Dict[int, List[str]], Optional[str], str]:
    """
    Parse command line arguments supporting dynamic -vN/--versionN options.

    Returns:
        (batch_dir, versions_map, nbn) where:
          - versions_map maps version number (int) -> list of input directories (str)
          - nbn is an optional identifier provided with --nbn/-n
    """
    # First pass: parse known args (positional batch), leave the rest for custom processing.
    parser = argparse.ArgumentParser(
        prog="create-object-import-dir.py",
        description=(
            "Create a new object import directory with a URN:NBN and copy version inputs into vN subdirectories."
        ),
        epilog=(
            "Usage examples:\n"
            "  create-object-import-dir.py data/ingest/inbox/batch-1 -v1 path/to/v1\n"
            "  create-object-import-dir.py data/ingest/inbox/batch-1 -v2 dirA dirB --version5 dirC\n"
            "  create-object-import-dir.py data/ingest/inbox/batch-1 -n urn:nbn:nl:ui:13-<id> -v1 dir\n"
            "  create-object-import-dir.py data/ingest/inbox/batch-1 --nbn 123e4567-e89b-12d3-a456-426614174000 -v3 dir\n\n"
            "Notes:\n"
            "  - Specify each version as -vN or --versionN where N is an integer (e.g., -v1, --version2).\n"
            "  - You may provide one or more input directories after each version option; they will be merged into vN.\n"
            "  - Version numbers do not have to start at 1 and do not have to be contiguous.\n"
            "  - With --nbn/-n you can provide either a URN:NBN (e.g., urn:nbn:nl:ui:13-...) or a bare UUID; UUIDs are converted to URN:NBN."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "batch",
        help="Import batch directory under which to create the object import directory."
    )
    parser.add_argument(
        "-n", "--nbn",
        help="Use the given identifier as the object directory name. Accepts a URN:NBN or a bare UUID (converted to urn:nbn:nl:ui:13-<uuid>).",
        metavar="NBN_OR_UUID",
    )
    parser.add_argument(
        "--version-info-template",
        default=os.path.join(os.path.dirname(__file__), "default-version-info.json"),
        help="Path to version-info JSON template file (default: default-version-info.json in script directory)",
        metavar="TEMPLATE_JSON",
    )

    # Let argparse parse only the known args; we'll process dynamic -vN/--versionN ourselves.
    known, unknown = parser.parse_known_args(argv)

    # Custom pass to parse version options with dynamic suffix N and their inputs
    versions: Dict[int, List[str]] = {}
    i = 0
    while i < len(unknown):
        token = unknown[i]
        if token == "--":
            # All remaining are positional; but we don't support global positionals.
            i += 1
            continue

        m = VERSION_OPT_RE.match(token)
        if m:
            ver = int(m.group(1))
            i += 1
            inputs: List[str] = []
            # Collect subsequent arguments until the next -vN/--versionN option.
            while i < len(unknown):
                nxt = unknown[i]
                if nxt == "--":
                    i += 1
                    break
                if nxt.startswith("-"):
                    # If it's another version option, stop collecting for this version.
                    if VERSION_OPT_RE.match(nxt):
                        break
                    # Unknown option encountered
                    parser.error(f"Unknown option: {nxt}")
                inputs.append(nxt)
                i += 1

            if not inputs:
                parser.error(f"No input directories provided for version {ver} after option {token}")
            versions.setdefault(ver, []).extend(inputs)
            continue

        # If we get here, we encountered an unexpected token.
        parser.error(f"Unexpected argument: {token}")

    if not versions:
        parser.error("At least one -vN/--versionN option with input directory/directories is required.")

    return known.batch, versions, known.nbn, known.version_info_template


def ensure_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def copy_into(src_dir: str, dst_dir: str) -> None:
    """
    Merge-copy contents of src_dir into dst_dir. Creates dst_dir if needed.
    """
    if not os.path.isdir(src_dir):
        raise ValueError(f"Input path is not a directory: {src_dir}")
    ensure_directory(dst_dir)

    for entry in os.listdir(src_dir):
        src_path = os.path.join(src_dir, entry)
        dst_path = os.path.join(dst_dir, entry)
        if os.path.isdir(src_path):
            # shutil.copytree with dirs_exist_ok=True merges directories
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        else:
            # Ensure parent exists, then copy (overwriting if necessary)
            ensure_directory(os.path.dirname(dst_path))
            shutil.copy2(src_path, dst_path)


def validate_or_format_nbn(value: str) -> str:
    """
    Validate provided --nbn/-n value and normalize if needed.
    - If it's a UUID (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx), convert to 'urn:nbn:nl:ui:13-<uuid>'.
    - If it is a URN:NBN (starts with 'urn:nbn:'), accept as-is.
    Otherwise raise ValueError.
    """
    v = value.strip()
    lower = v.lower()

    # Bare UUID -> urn:nbn:nl:ui:13-<uuid>
    try:
        u = uuid.UUID(v)
        return f"urn:nbn:nl:ui:13-{str(u)}"
    except (ValueError, AttributeError):
        pass

    # Accept urn:nbn:* as-is
    if lower.startswith("urn:nbn:"):
        return v

    raise ValueError(f"Invalid --nbn value: {value}. Provide a URN:NBN or a bare UUID.")


def main(argv: List[str]) -> int:
    try:
        batch_dir, versions, provided_nbn, version_info_template = parse_args(argv)
        # Determine the object directory name (URN)
        if provided_nbn:
            urn = validate_or_format_nbn(provided_nbn)
        else:
            urn = f"urn:nbn:nl:ui:13-{uuid.uuid4()}"
        base_dir = os.path.join(batch_dir, urn)
        ensure_directory(base_dir)

        # Load version-info template
        if not os.path.isfile(version_info_template):
            raise FileNotFoundError(f"Version info template not found: {version_info_template}")
        with open(version_info_template, "r", encoding="utf-8") as f:
            version_info_content = f.read()

        # For each version, copy provided inputs into vN and create vN.json
        for ver in sorted(versions.keys()):
            v_dir = os.path.join(base_dir, f"v{ver}")
            ensure_directory(v_dir)
            for src in versions[ver]:
                if not os.path.exists(src):
                    raise FileNotFoundError(f"Input path does not exist: {src}")
                if not os.path.isdir(src):
                    raise NotADirectoryError(f"Input path is not a directory: {src}")
                copy_into(src, v_dir)
            # Write version info JSON
            v_json_path = os.path.join(base_dir, f"v{ver}.json")
            with open(v_json_path, "w", encoding="utf-8") as f:
                f.write(version_info_content)

        # Print the created object directory path so callers can capture it.
        print(base_dir)
        return 0
    except SystemExit:
        # argparse already printed an error/help
        raise
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))