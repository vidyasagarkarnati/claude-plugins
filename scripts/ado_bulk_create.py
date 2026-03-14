#!/usr/bin/env python3
"""
ado_bulk_create.py — Bulk-create Azure DevOps work items (Features, User Stories, Tasks)
from a structured JSON manifest.

Usage:
    python3 scripts/ado_bulk_create.py --input /tmp/ado_import.json

Auth (env vars):
    AZURE_DEVOPS_ORG_URL          e.g. https://dev.azure.com/myorg
    AZURE_PERSONAL_ACCESS_TOKEN   Personal Access Token with Work Items read/write scope
    AZURE_DEVOPS_PROJECT          Default project name (can be overridden in JSON)

JSON input schema:
    {
      "project": "MyProject",          // optional, overrides AZURE_DEVOPS_PROJECT env var
      "defaults": {
        "assigned_to": "dev@company.com",
        "area_path": "MyProject\\\\TeamA",
        "iteration_path": "MyProject\\\\Sprint 5",
        "bundle": "Q1-Release"
      },
      "features": [
        {
          "title": "Feature Title",
          "description": "Feature description",
          "assigned_to": "...",         // optional, overrides defaults
          "area_path": "...",           // optional, overrides defaults
          "iteration_path": "...",      // optional, overrides defaults
          "bundle": "...",              // optional, overrides defaults
          "stories": [
            {
              "title": "Story Title",
              "description": "As a user, I want ...",
              "acceptance_criteria": "Given ... When ... Then ...",
              "assigned_to": "...",     // optional override
              "tasks": [
                {
                  "title": "Task Title",
                  "description": "Implementation detail",
                  "estimate": 6,        // hours; defaults to 8
                  "assigned_to": "..."  // optional override
                }
              ]
            }
          ]
        }
      ]
    }

Dependencies:
    pip install azure-devops
"""

import argparse
import json
import os
import sys

try:
    from azure.devops.connection import Connection
    from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation
    from msrest.authentication import BasicAuthentication
except ImportError:
    print("ERROR: azure-devops package not installed.")
    print("Run: pip install azure-devops")
    sys.exit(1)


def resolve(item, defaults, field):
    """Resolve a field value from item overrides or defaults."""
    return item.get(field) or defaults.get(field)


def validate_manifest(manifest):
    """Validate the manifest before any API calls. Returns list of error strings."""
    errors = []
    defaults = manifest.get("defaults", {})

    required_defaults = ["assigned_to", "area_path", "iteration_path", "bundle"]
    for field in required_defaults:
        if not defaults.get(field):
            errors.append(f"defaults.{field} is required (or must be set on every item)")

    features = manifest.get("features", [])
    if not features:
        errors.append("manifest must contain at least one feature")
        return errors

    for fi, feature in enumerate(features):
        f_label = f'feature[{fi}] "{feature.get("title", "(no title)")}"'
        if not feature.get("title"):
            errors.append(f"{f_label}: title is required")
        if not feature.get("description"):
            errors.append(f"{f_label}: description is required")
        for field in ["assigned_to", "area_path", "iteration_path", "bundle"]:
            if not resolve(feature, defaults, field):
                errors.append(f"{f_label}: {field} is required (not set on item or in defaults)")

        for si, story in enumerate(feature.get("stories", [])):
            s_label = f'story[{fi}.{si}] "{story.get("title", "(no title)")}"'
            if not story.get("title"):
                errors.append(f"{s_label}: title is required")
            if not story.get("description"):
                errors.append(f"{s_label}: description is required")
            if not story.get("acceptance_criteria"):
                errors.append(f"{s_label}: acceptance_criteria is required (no default permitted)")
            for field in ["assigned_to", "area_path", "iteration_path", "bundle"]:
                if not resolve(story, defaults, field):
                    errors.append(f"{s_label}: {field} is required")

            for ti, task in enumerate(story.get("tasks", [])):
                t_label = f'task[{fi}.{si}.{ti}] "{task.get("title", "(no title)")}"'
                if not task.get("title"):
                    errors.append(f"{t_label}: title is required")
                if not task.get("description"):
                    errors.append(f"{t_label}: description is required")
                for field in ["assigned_to", "area_path", "iteration_path"]:
                    if not resolve(task, defaults, field):
                        errors.append(f"{t_label}: {field} is required")

    return errors


def make_patch(fields):
    """Build a JSON patch document from a field dict."""
    return [
        JsonPatchOperation(op="add", path=f"/fields/{k}", value=v)
        for k, v in fields.items()
        if v is not None
    ]


def add_parent_relation(patch, org_url, parent_id):
    """Append a parent relation operation to the patch document."""
    patch.append(JsonPatchOperation(
        op="add",
        path="/relations/-",
        value={
            "rel": "System.LinkTypes.Hierarchy-Reverse",
            "url": f"{org_url.rstrip('/')}/_apis/wit/workItems/{parent_id}",
            "attributes": {"comment": ""}
        }
    ))
    return patch


def print_results(results, stats):
    """Print the final summary table."""
    print("\nBulk Import Complete")
    print("=" * 50)
    print(f"  Features created : {stats['feature_created']}")
    print(f"  Stories created  : {stats['story_created']}")
    print(f"  Tasks created    : {stats['task_created']}")
    skipped = stats['story_skipped'] + stats['task_skipped']
    failed = stats['feature_failed'] + stats['story_failed'] + stats['task_failed']
    print(f"  Skipped          : {skipped}")
    print(f"  Failed           : {failed}")
    print()

    # Print hierarchy
    for r in results:
        if r["type"] == "Feature":
            icon = "+" if r["status"] == "created" else "!"
            id_str = f"#{r['id']}" if r.get("id") else "[FAILED]"
            print(f"{icon} Feature {id_str}: {r['title']}  [{r['status'].upper()}]")
        elif r["type"] == "User Story":
            icon = "  +" if r["status"] == "created" else "  !"
            id_str = f"#{r['id']}" if r.get("id") else f"[{r['status'].upper()}]"
            print(f"{icon} Story {id_str}: {r['title']}")
        elif r["type"] == "Task":
            icon = "    -" if r["status"] == "created" else "    !"
            id_str = f"#{r['id']}" if r.get("id") else f"[{r['status'].upper()}]"
            est = f"  [{r.get('estimate', 8)}h]" if r["status"] == "created" else ""
            print(f"{icon} Task {id_str}: {r['title']}{est}")

    failures = [r for r in results if r["status"] in ("failed", "skipped") and r.get("error")]
    if failures:
        print("\nFailures & Skips")
        print("-" * 40)
        for r in failures:
            print(f"  [{r['type']}] {r['title']}: {r['error']}")

    return failed


def main():
    parser = argparse.ArgumentParser(description="Bulk-create Azure DevOps work items from JSON manifest")
    parser.add_argument("--input", required=True, help="Path to JSON manifest file")
    args = parser.parse_args()

    # Load manifest
    try:
        with open(args.input) as f:
            manifest = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Could not load manifest: {e}")
        sys.exit(1)

    # Validate
    errors = validate_manifest(manifest)
    if errors:
        print(f"MANIFEST VALIDATION ERRORS — 0 items created\n")
        for err in errors:
            print(f"  {err}")
        print("\nFix all errors above and rerun.")
        sys.exit(1)

    # Auth
    org_url = os.environ.get("AZURE_DEVOPS_ORG_URL")
    pat = os.environ.get("AZURE_PERSONAL_ACCESS_TOKEN")
    project = manifest.get("project") or os.environ.get("AZURE_DEVOPS_PROJECT")

    if not org_url:
        print("ERROR: AZURE_DEVOPS_ORG_URL environment variable not set")
        sys.exit(1)
    if not pat:
        print("ERROR: AZURE_PERSONAL_ACCESS_TOKEN environment variable not set")
        sys.exit(1)
    if not project:
        print("ERROR: project not set in manifest and AZURE_DEVOPS_PROJECT env var not set")
        sys.exit(1)

    credentials = BasicAuthentication("", pat)
    connection = Connection(base_url=org_url, creds=credentials)
    wit_client = connection.clients.get_work_item_tracking_client()

    defaults = manifest.get("defaults", {})
    results = []
    stats = {k: 0 for k in [
        "feature_created", "feature_failed",
        "story_created", "story_failed", "story_skipped",
        "task_created", "task_failed", "task_skipped"
    ]}

    for feature in manifest.get("features", []):
        f_title = feature["title"]

        # Build feature patch
        f_fields = {
            "System.Title": f_title,
            "System.Description": feature["description"],
            "System.AssignedTo": resolve(feature, defaults, "assigned_to"),
            "System.AreaPath": resolve(feature, defaults, "area_path"),
            "System.IterationPath": resolve(feature, defaults, "iteration_path"),
            "Custom.Bundle": resolve(feature, defaults, "bundle"),
        }
        patch = make_patch(f_fields)

        feature_id = None
        try:
            wi = wit_client.create_work_item(patch, project, "Feature")
            feature_id = wi.id
            results.append({"type": "Feature", "title": f_title, "id": feature_id, "status": "created"})
            stats["feature_created"] += 1
            print(f"  Created Feature #{feature_id}: {f_title}")
        except Exception as e:
            results.append({"type": "Feature", "title": f_title, "id": None, "status": "failed", "error": str(e)})
            stats["feature_failed"] += 1
            print(f"  FAILED Feature: {f_title} — {e}")
            # Skip all stories/tasks under this feature
            for story in feature.get("stories", []):
                results.append({"type": "User Story", "title": story["title"], "id": None,
                                 "status": "skipped", "error": "parent feature failed"})
                stats["story_skipped"] += 1
                for task in story.get("tasks", []):
                    results.append({"type": "Task", "title": task["title"], "id": None,
                                    "status": "skipped", "error": "parent feature failed"})
                    stats["task_skipped"] += 1
            continue

        # Create stories under this feature
        for story in feature.get("stories", []):
            s_title = story["title"]

            s_fields = {
                "System.Title": s_title,
                "System.Description": story["description"],
                "System.AssignedTo": resolve(story, defaults, "assigned_to"),
                "System.AreaPath": resolve(story, defaults, "area_path"),
                "System.IterationPath": resolve(story, defaults, "iteration_path"),
                "Custom.Bundle": resolve(story, defaults, "bundle"),
                "Microsoft.VSTS.Common.AcceptanceCriteria": story["acceptance_criteria"],
            }
            patch = make_patch(s_fields)
            patch = add_parent_relation(patch, org_url, feature_id)

            story_id = None
            try:
                wi = wit_client.create_work_item(patch, project, "User Story")
                story_id = wi.id
                results.append({"type": "User Story", "title": s_title, "id": story_id, "status": "created"})
                stats["story_created"] += 1
                print(f"    Created Story #{story_id}: {s_title}")
            except Exception as e:
                results.append({"type": "User Story", "title": s_title, "id": None,
                                 "status": "failed", "error": str(e)})
                stats["story_failed"] += 1
                print(f"    FAILED Story: {s_title} — {e}")
                for task in story.get("tasks", []):
                    results.append({"type": "Task", "title": task["title"], "id": None,
                                    "status": "skipped", "error": "parent story failed"})
                    stats["task_skipped"] += 1
                continue

            # Create tasks under this story
            for task in story.get("tasks", []):
                t_title = task["title"]
                estimate = task.get("estimate", 8)

                t_fields = {
                    "System.Title": t_title,
                    "System.Description": task["description"],
                    "System.AssignedTo": resolve(task, defaults, "assigned_to"),
                    "System.AreaPath": resolve(task, defaults, "area_path"),
                    "System.IterationPath": resolve(task, defaults, "iteration_path"),
                    "Microsoft.VSTS.Scheduling.OriginalEstimate": estimate,
                    "Microsoft.VSTS.Scheduling.RemainingWork": estimate,
                }
                patch = make_patch(t_fields)
                patch = add_parent_relation(patch, org_url, story_id)

                try:
                    wi = wit_client.create_work_item(patch, project, "Task")
                    task_id = wi.id
                    results.append({"type": "Task", "title": t_title, "id": task_id,
                                    "status": "created", "estimate": estimate})
                    stats["task_created"] += 1
                    print(f"      Created Task #{task_id}: {t_title} [{estimate}h]")
                except Exception as e:
                    results.append({"type": "Task", "title": t_title, "id": None,
                                    "status": "failed", "error": str(e)})
                    stats["task_failed"] += 1
                    print(f"      FAILED Task: {t_title} — {e}")

    failed_count = print_results(results, stats)
    sys.exit(1 if failed_count > 0 else 0)


if __name__ == "__main__":
    main()
