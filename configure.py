#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import random
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

# --------------------------------------------------------------------------------------
# Constants & Paths
# --------------------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
TELEGRAF_CONF = BASE_DIR / "telegraf.conf"
TELEGRAF_BACKUP = TELEGRAF_CONF.with_suffix(".conf.backup")

AVAILABLE_DATASETS: List[str] = [
    "scores_1m",
    "responsiveness_1s",
    "speed_results",
    "web_responsiveness_results",
]

# dataset name -> template file stem, interval extractor/constant
TEMPLATE_MAPPING: Dict[str, str] = {
    r"^scores_(.+)$": "input_scores",
    r"^responsiveness_(.+)$": "input_responsiveness",
    r"^speed_results$": "input_speed",
    r"^web_responsiveness_results$": "input_web_responsiveness",
}

DEFAULT_INTERVAL_BY_TEMPLATE = {
    "input_speed": "30s",
    "input_web_responsiveness": "30s",
}

HTTP_LISTENER_TEMPLATE = "input_http_listener"
AGENT_TEMPLATE = "agent"
OUTPUT_TEMPLATE = "output"

# --------------------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Orb:
    host: str
    port: str

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

# --------------------------------------------------------------------------------------
# IO Helpers
# --------------------------------------------------------------------------------------

def prompt(msg: str, default: str | None = None, validator=None) -> str:
    """
    Prompt the user once; apply default and optional validator.
    """
    suffix = f" [{default}]" if default else ""
    while True:
        val = input(f"{msg}{suffix}: ").strip()
        if not val and default is not None:
            val = default
        if validator and not validator(val):
            print("Invalid value, please try again.")
            continue
        return val

def select_from_list(name: str, options: Sequence[str]) -> List[str]:
    """
    Allow comma-separated selection by index or by name, de-duplicated.
    """
    print(f"\n=== {name.upper()} SELECTION ===")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    print("\nEnter numbers (comma-separated) or names (also comma-separated)")
    print("Examples: 1,3  or  scores_1m,speed_results")

    while True:
        raw = input(f"{name.capitalize()} to enable: ").strip()
        if not raw:
            print("Please select at least one.")
            continue

        selected: List[str] = []
        for item in (x.strip() for x in raw.split(",")):
            if not item:
                continue
            if item.isdigit():
                idx = int(item) - 1
                if 0 <= idx < len(options):
                    selected.append(options[idx])
                else:
                    print(f"Out of range: {item}")
                    selected = []
                    break
            elif item in options:
                selected.append(item)
            else:
                print(f"Unknown option: {item}")
                selected = []
                break

        if selected:
            # remove duplicates preserving order
            seen = set()
            deduped = [x for x in selected if not (x in seen or seen.add(x))]
            return deduped

def print_section(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def load_template(stem: str) -> str:
    path = TEMPLATES_DIR / f"{stem}.conf"
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path.read_text()

def render_template(stem: str, **kwargs) -> str:
    """
    Lightweight templating using Python's format(). Templates should contain
    placeholders in the form {name}.
    """
    return load_template(stem).format(**kwargs)

# --------------------------------------------------------------------------------------
# Parsing & Config assembly
# --------------------------------------------------------------------------------------

def parse_dataset(dataset: str) -> Tuple[str, str]:
    """
    Map dataset -> (template_stem, interval)
    """
    for pattern, template_stem in TEMPLATE_MAPPING.items():
        m = re.match(pattern, dataset)
        if not m:
            continue
        if template_stem in DEFAULT_INTERVAL_BY_TEMPLATE:
            return template_stem, DEFAULT_INTERVAL_BY_TEMPLATE[template_stem]
        return template_stem, m.group(1)
    raise ValueError(f"Unknown dataset: {dataset!r}")

def gather_tag_keys_from_templates() -> List[str]:
    """
    Find all tag_keys across input_* templates for the HTTP listener tag union.
    """
    tags: set[str] = set()
    tag_array_pat = re.compile(r"tag_keys\s*=\s*\[\s*((?:.|\n)*?)\s*\]", re.MULTILINE)
    for fn in os.listdir(TEMPLATES_DIR):
        if not fn.startswith("input_") or fn == f"{HTTP_LISTENER_TEMPLATE}.conf":
            continue
        stem = fn.split(".")[0]
        m = tag_array_pat.search(load_template(stem))
        if not m:
            continue
        vals = m.group(1)
        tags.update(re.findall(r'("[^"]+")', vals))
    return sorted(tags)

def build_api_inputs(orbs: Sequence[Orb], datasets: Sequence[str], collector_id: str) -> List[str]:
    inputs: List[str] = []
    for orb in orbs:
        for ds in datasets:
            stem, interval = parse_dataset(ds)
            inputs.append(
                render_template(
                    stem,
                    url=orb.base_url,
                    collector_id=collector_id,
                    interval=interval,
                )
            )
            inputs.append("")  # spacer
    return inputs

def generate_telegraf_for_api(orbs: Sequence[Orb], datasets: Sequence[str]) -> str:
    collector_id = str(random.randint(10000, 99999))
    print(f"Generated collector ID: {collector_id}")

    parts: List[str] = [load_template(AGENT_TEMPLATE), ""]
    parts.extend(build_api_inputs(orbs, datasets, collector_id))
    parts.append(load_template(OUTPUT_TEMPLATE))
    return "\n".join(parts)

def generate_telegraf_for_push(port: str) -> str:
    tags = gather_tag_keys_from_templates()
    listener = render_template(
        HTTP_LISTENER_TEMPLATE,
        PORT=port,
        TAGS=",\n\t".join(tags),
    )
    return listener + "\n" + load_template(OUTPUT_TEMPLATE)

def backup_existing_config() -> None:
    if TELEGRAF_CONF.exists():
        TELEGRAF_BACKUP.write_text(TELEGRAF_CONF.read_text())
        print(f"Existing configuration backed up to: {TELEGRAF_BACKUP}")

def orb_config_json(datasets: Sequence[str], port: str) -> Dict:
    return {
        "datasets.api": [f"port={port}", *datasets]
    }

def show_orb_cloud_instructions_for_api(orbs: Sequence[Orb], datasets: Sequence[str]) -> None:
    print_section("ORB CLOUD CONFIGURATION REQUIRED")
    print("For each Orb hostname below, you need to:")
    print("1. Go to https://cloud.orb.net/status")
    print("2. Find the Orb with the matching hostname")
    print("3. Click 'Edit Config' for that Orb")
    print("4. Configure the Orb with the JSON below")
    print("\n" + "-" * 60)

    for orb in orbs:
        print(f"\n🔧 Configuration for Orb: {orb.host}:{orb.port}")
        print("-" * 40)
        print(json.dumps(orb_config_json(datasets, orb.port), indent=2))
        print()

def show_orb_cloud_instructions_for_push(url: str, datasets: Sequence[str]) -> None:
    print_section("ORB CLOUD CONFIGURATION REQUIRED")
    cfg = {
        "datasets.push": [
            *datasets,
            "identifiable=true",
            "format=json",
            f"url={url}",
        ],
    }
    print(json.dumps(cfg, indent=2))
    print()

# --------------------------------------------------------------------------------------
# Prompts
# --------------------------------------------------------------------------------------

def prompt_delivery_method() -> str:
    print("\n== DATA DELIVERY METHOD ==")
    print("API  - Telegraf polls individual Orbs (pull).")
    print("Push - Orbs post directly to the Telegraf HTTP listener (requires Orb Cloud features).")
    while True:
        m = prompt("Select api or push delivery method", default="api").lower()
        if m in {"api", "push"}:
            print(f"Using {m} delivery method.")
            return m

def prompt_orbs() -> List[Orb]:
    print("\n=== ORB INPUT CONFIGURATION ===")
    print("Enter Orb instances to use as inputs (hostnames must be routable from this machine).")
    print("Press Enter with empty hostname to finish.\n")

    orbs: List[Orb] = []
    while True:
        host = input(f"Orb #{len(orbs) + 1} hostname (or press Enter to finish): ").strip()
        if not host:
            break
        port = prompt(f"Port for {host}", default="7080")
        orbs.append(Orb(host=host, port=port))
        print(f"Added: {host}:{port}\n")

    if not orbs:
        print("No Orbs configured. Exiting.")
        sys.exit(1)
    return orbs

def prompt_datasets() -> List[str]:
    return select_from_list("datasets", AVAILABLE_DATASETS)

# --------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------

def main() -> None:
    print("Orb Local Analytics Configuration")
    print("=" * 40)

    try:
        method = prompt_delivery_method()
        datasets = prompt_datasets()

        print(f"\nDatasets ({len(datasets)}):")
        for ds in datasets:
            print(f"  - {ds}")

        if method == "api":
            print("\n=== DATA API CONFIGURATION ===")
            orbs = prompt_orbs()
            print("\n=== CONFIGURATION SUMMARY ===")
            print("Delivery: API")
            print(f"Orb instances ({len(orbs)}):")
            for o in orbs:
                print(f"  - {o.host}:{o.port}")
        else:
            print("\n=== DATA PUSH CONFIGURATION ===")
            print("Note: Telegraf host must be reachable from all Orbs.")
            telegraf_host = prompt("Telegraf hostname/ip address")
            port = prompt("Telegraf listener port", default="7081")
            print("\n=== CONFIGURATION SUMMARY ===")
            print("Delivery: Push")
            print(f"Telegraf URL: http://{telegraf_host}:{port}/ingest")

        # Confirm
        confirm = prompt("\nGenerate telegraf.conf with this configuration? [Y/n]: ", default="n").strip().lower()
        if confirm and confirm not in ['y', 'yes']:
            print("Configuration cancelled.")
            return

        # Build telegraf.conf
        backup_existing_config()
        if method == "api":
            cfg = generate_telegraf_for_api(orbs, datasets)
        else:
            cfg = generate_telegraf_for_push(port)

        TELEGRAF_CONF.write_text(cfg)
        print("\n✅ New telegraf.conf generated successfully!")

        # Instructions for Orb Cloud configuration
        if method == "api":
            print(f"Total HTTP inputs configured: {len(orbs) * len(datasets)}")
            show_orb_cloud_instructions_for_api(orbs, datasets)
        else:
            url = f"http://{telegraf_host}:{port}/ingest"
            show_orb_cloud_instructions_for_push(url, datasets)

        print("🚀 Next steps:")
        print("1. Configure your Orbs as shown above")
        print("2. Start your analytics stack: docker compose up -d")
        print("   (or if it's already running, restart telegraf: docker restart telegraf)")
        print("3. Check that data is flowing in Grafana at http://localhost:3000")

    except KeyboardInterrupt:
        print("\n\nConfiguration cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
