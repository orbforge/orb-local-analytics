#!/usr/bin/env python3
"""
Orb Local Analytics Configuration Script

This script prompts the user for Orb inputs and datasets, then generates
a telegraf.conf file with the appropriate HTTP input configurations.
"""

import os
import sys
import random
import re
import json
from pathlib import Path
from typing import List, Tuple, Dict


def get_orb_inputs() -> List[Tuple[str, str]]:
    """
    Prompt user for Orb inputs (hostname, port).
    Returns list of tuples: (hostname, port)
    """
    print("\n=== ORB INPUT CONFIGURATION ===")
    print("Enter Orb instances you'd like to use as inputs.")
    print("Note: They must be routable/accessible from this machine.")
    print("Press Enter with empty hostname to finish.\n")
    
    orbs = []
    while True:
        hostname = input(f"Orb #{len(orbs) + 1} hostname (or press Enter to finish): ").strip()
        if not hostname:
            break
            
        port = input(f"Port for {hostname} [8000]: ").strip() or "8000"
        
        orbs.append((hostname, port))
        print(f"Added: {hostname}:{port}\n")
    
    if not orbs:
        print("No Orbs configured. Exiting.")
        sys.exit(1)
        
    return orbs


def parse_dataset_info(dataset_name: str) -> Tuple[str, str]:
    """
    Parse dataset name to extract template type and interval.
    
    Args:
        dataset_name: e.g., "responsiveness_15s", "scores_1m", "speed_results"
        
    Returns:
        Tuple of (template_name, interval)
    """
    # Map dataset patterns to template names
    template_mapping = {
        r"^scores_(.+)$": "input_scores",
        r"^responsiveness_(.+)$": "input_responsiveness", 
        r"^speed_results$": "input_speed",
        r"^web_responsiveness_results$": "input_web_responsiveness"
    }
    
    for pattern, template_name in template_mapping.items():
        match = re.match(pattern, dataset_name)
        if match:
            if template_name in ["input_speed", "input_web_responsiveness"]:
                # These don't have intervals in their names
                return template_name, "30s"  # Default interval
            else:
                # Extract interval from match group
                interval = match.group(1)
                return template_name, interval
    
    raise ValueError(f"Unknown dataset format: {dataset_name}")


def get_datasets() -> List[str]:
    """
    Prompt user for datasets to enable.
    Returns list of dataset names.
    """
    print("\n=== DATASET CONFIGURATION ===")
    print("Available datasets:")
    available_datasets = [
        "scores_1m",
        "responsiveness_1m",
        "responsiveness_15s", 
        "responsiveness_1s", 
        "speed_results",
        "web_responsiveness_results"
    ]
    
    for i, dataset in enumerate(available_datasets, 1):
        print(f"  {i}. {dataset}")
    
    print("\nEnter dataset numbers (comma-separated) or dataset names:")
    print("Example: 1,3 or responsiveness_15s,speed_results")
    
    while True:
        selection = input("Datasets to enable: ").strip()
        if not selection:
            print("Please select at least one dataset.")
            continue
            
        selected_datasets = []
        
        # Parse input (could be numbers or names)
        for item in selection.split(','):
            item = item.strip()
            
            # Check if it's a number
            if item.isdigit():
                idx = int(item) - 1
                if 0 <= idx < len(available_datasets):
                    selected_datasets.append(available_datasets[idx])
                else:
                    print(f"Invalid dataset number: {item}")
                    selected_datasets = []
                    break
            # Check if it's a dataset name
            elif item in available_datasets:
                selected_datasets.append(item)
            else:
                print(f"Unknown dataset: {item}")
                selected_datasets = []
                break
        
        if selected_datasets:
            return list(set(selected_datasets))  # Remove duplicates
        print("Please try again.")


def load_template(template_name: str) -> str:
    """Load a template file from the templates directory."""
    template_path = Path(__file__).parent / "templates" / f"{template_name}.conf"
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
        
    return template_path.read_text()


def generate_telegraf_config(orbs: List[Tuple[str, str]], datasets: List[str]) -> str:
    """
    Generate the complete telegraf.conf content.
    
    Args:
        orbs: List of (hostname, port) tuples
        datasets: List of dataset names to include
        
    Returns:
        Complete telegraf configuration as string
    """
    config_parts = []
    
    # Generate a random 5-digit collector ID
    collector_id = str(random.randint(10000, 99999))
    print(f"Generated collector ID: {collector_id}")
    
    # Add agent configuration
    config_parts.append(load_template("agent"))
    config_parts.append("")  # Empty line
    
    # Add HTTP inputs for each orb/dataset combination
    for hostname, port in orbs:
        url = f"http://{hostname}:{port}"
        
        for dataset in datasets:
            try:
                template_name, interval = parse_dataset_info(dataset)
                template = load_template(template_name)
                # Replace placeholders
                input_config = template.format(url=url, collector_id=collector_id, interval=interval)
                config_parts.append(input_config)
                config_parts.append("")  # Empty line between inputs
            except FileNotFoundError:
                print(f"Warning: Template not found for dataset '{dataset}', skipping.")
                continue
            except ValueError as e:
                print(f"Warning: {e}, skipping.")
                continue
    
    # Add output configuration
    config_parts.append(load_template("output"))
    
    return "\n".join(config_parts)


def backup_existing_config():
    """Backup existing telegraf.conf if it exists."""
    config_path = Path(__file__).parent / "telegraf.conf"
    if config_path.exists():
        backup_path = config_path.with_suffix(".conf.backup")
        backup_path.write_text(config_path.read_text())
        print(f"Existing configuration backed up to: {backup_path}")


def generate_orb_config_json(datasets: List[str], port: str) -> Dict:
    """
    Generate the JSON configuration that needs to be applied to a specific Orb.
    
    Args:
        datasets: List of dataset names to include
        port: Port number for the API for this specific Orb
        
    Returns:
        Dictionary representing the Orb configuration JSON
    """
    # Build the API configuration list (include port + all datasets)
    api_config = [f"port={port}"] + datasets
    
    # Build the datasets configuration list (just the datasets)
    datasets_config = datasets.copy()
    
    return {
        "datasets.api": api_config,
        "datasets.datasets": datasets_config
    }


def display_orb_configurations(orbs: List[Tuple[str, str]], datasets: List[str]):
    """
    Display the JSON configurations that users need to apply to each Orb.
    
    Args:
        orbs: List of (hostname, port) tuples
        datasets: List of dataset names
    """
    print("\n" + "=" * 60)
    print("📋 ORB CLOUD CONFIGURATION REQUIRED")
    print("=" * 60)
    print("For each Orb hostname below, you need to:")
    print("1. Go to https://cloud.orb.net/orbs")
    print("2. Find the Orb with the matching hostname")
    print("3. Click 'Edit Config' for that Orb")
    print("4. Configure the Orb with the JSON below")
    print("6. Restart the Orb sensor (restart twice for now, long story)")
    print("\n" + "-" * 60)
    
    for hostname, port in orbs:
        print(f"\n🔧 Configuration for Orb: {hostname}:{port}")
        print("-" * 40)
        
        orb_config = generate_orb_config_json(datasets, port)
        json_output = json.dumps(orb_config, indent=2)
        print(json_output)
        print()


def main():
    """Main configuration function."""
    print("Orb Local Analytics Configuration")
    print("=" * 40)
    
    try:
        # Get user inputs
        orbs = get_orb_inputs()
        datasets = get_datasets()
        
        # Summary
        print("\n=== CONFIGURATION SUMMARY ===")
        print(f"Orb instances ({len(orbs)}):")
        for hostname, port in orbs:
            print(f"  - {hostname}:{port}")
        
        print(f"\nDatasets ({len(datasets)}):")
        for dataset in datasets:
            print(f"  - {dataset}")
        
        # Confirm
        confirm = input("\nGenerate telegraf.conf with this configuration? [Y/n]: ").strip().lower()
        if confirm and confirm not in ['y', 'yes']:
            print("Configuration cancelled.")
            return
        
        # Backup existing config
        backup_existing_config()
        
        # Generate new config
        config_content = generate_telegraf_config(orbs, datasets)
        
        # Write new config
        config_path = Path(__file__).parent / "telegraf.conf"
        config_path.write_text(config_content)
        
        print(f"\n✅ New telegraf.conf generated successfully!")
        print(f"Total HTTP inputs configured: {len(orbs) * len(datasets)}")
        
        # Display Orb configuration requirements
        display_orb_configurations(orbs, datasets)
        
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