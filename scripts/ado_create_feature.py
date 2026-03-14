#!/usr/bin/env python3
"""
ado_create_feature.py — Create an Azure DevOps Feature with optional child User Stories and Tasks.

Usage:
    python3 scripts/ado_create_feature.py --title "My Feature" --description "..." \\
        [--assigned-to email] [--area-path path] [--iteration path] [--bundle value] \\
        [--stories "Story 1, Story 2"] [--acceptance-criteria "..."] \\
        [--tasks "Task 1, Task 2"] [--project name]

Auth (env vars):
    AZURE_DEVOPS_ORG_URL          e.g. https://dev.azure.com/myorg
    AZURE_PERSONAL_ACCESS_TOKEN   PAT with Work Items read/write scope
    AZURE_DEVOPS_PROJECT          Default project name
"""

import argparse
import os
import sys

try:
    from azure.devops.connection import Connection
    from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation, Wiql
    from msrest.authentication import BasicAuthentication
except ImportError:
    print("ERROR: azure-devops package not installed.")
    print("Run: pip install azure-devops")
    sys.exit(1)


def make_patch(fields):
    return [
        JsonPatchOperation(op="add", path=f"/fields/{k}", value=v)
        for k, v in fields.items()
        if v is not None
    ]


def add_parent_relation(patch, org_url, parent_id):
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


def prompt_if_missing(args_dict, field, label):
    if not args_dict.get(field):
        while True:
            value = input(f"  {label}: ").strip()
            if value:
                args_dict[field] = value
                break
            print("  Value cannot be empty.")


def main():
    parser = argparse.ArgumentParser(description="Create an Azure DevOps Feature")
    parser.add_argument("--title", required=True, help="Feature title")
    parser.add_argument("--description", required=True, help="Feature description")
    parser.add_argument("--assigned-to", dest="assigned_to", help="Assignee email")
    parser.add_argument("--area-path", dest="area_path", help="Area path")
    parser.add_argument("--iteration", dest="iteration", help="Iteration path")
    parser.add_argument("--bundle", help="Corestack Bundle field value")
    parser.add_argument("--stories", help="Comma-separated list of User Story titles")
    parser.add_argument("--acceptance-criteria", dest="acceptance_criteria",
                        help="Acceptance criteria applied to all child User Stories")
    parser.add_argument("--tasks", help="Comma-separated list of Task titles (created under each story)")
    parser.add_argument("--estimate", type=int, default=8,
                        help="Default task estimate in hours (default: 8)")
    parser.add_argument("--project", help="ADO project name (overrides AZURE_DEVOPS_PROJECT env var)")
    args = parser.parse_args()

    # Auth
    org_url = os.environ.get("AZURE_DEVOPS_ORG_URL")
    pat = os.environ.get("AZURE_PERSONAL_ACCESS_TOKEN")
    project = args.project or os.environ.get("AZURE_DEVOPS_PROJECT")

    if not org_url:
        print("ERROR: AZURE_DEVOPS_ORG_URL environment variable not set")
        sys.exit(1)
    if not pat:
        print("ERROR: AZURE_PERSONAL_ACCESS_TOKEN environment variable not set")
        sys.exit(1)
    if not project:
        print("ERROR: --project not provided and AZURE_DEVOPS_PROJECT env var not set")
        sys.exit(1)

    # Prompt for missing Corestack mandatory fields
    fields = {
        "assigned_to": args.assigned_to,
        "area_path": args.area_path,
        "iteration": args.iteration,
        "bundle": args.bundle,
    }
    prompts = {
        "assigned_to":   "Assigned To (e.g. user@company.com)",
        "area_path":     "Area Path (e.g. Product_Mgmt\\Core)",
        "iteration":     "Iteration Path (e.g. Product_Mgmt\\Product_Backlog)",
        "bundle":        "Bundle (e.g. CORE)",
    }
    missing = [f for f in prompts if not fields[f]]
    if missing:
        print("Some required fields are not set. Please provide them now:\n")
        for f in missing:
            prompt_if_missing(fields, f, prompts[f])
        print()

    # Connect
    credentials = BasicAuthentication("", pat)
    connection = Connection(base_url=org_url, creds=credentials)
    wit_client = connection.clients.get_work_item_tracking_client()

    # Create Feature
    f_fields = {
        "System.Title":        args.title,
        "System.Description":  args.description,
        "System.AssignedTo":   fields["assigned_to"],
        "System.AreaPath":     fields["area_path"],
        "System.IterationPath": fields["iteration"],
        "Custom.Bundle":       fields["bundle"],
    }
    try:
        wi = wit_client.create_work_item(make_patch(f_fields), project, "Feature")
        feature_id = wi.id
        print(f"Feature #{feature_id}: {args.title}")
    except Exception as e:
        print(f"ERROR: Failed to create Feature — {e}")
        sys.exit(1)

    if not args.stories:
        feature_url = f"{org_url.rstrip('/')}/_workitems/edit/{feature_id}"
        print(f"\nFeature URL: {feature_url}")
        sys.exit(0)

    # Create child User Stories
    story_titles = [s.strip() for s in args.stories.split(",") if s.strip()]
    task_titles = [t.strip() for t in args.tasks.split(",") if t.strip()] if args.tasks else []
    ac = args.acceptance_criteria or f"Acceptance criteria for {args.title}"

    created_stories = []
    for story_title in story_titles:
        s_fields = {
            "System.Title":       story_title,
            "System.Description": story_title,
            "System.AssignedTo":  fields["assigned_to"],
            "System.AreaPath":    fields["area_path"],
            "System.IterationPath": fields["iteration"],
            "Custom.Bundle":      fields["bundle"],
            "Microsoft.VSTS.Common.AcceptanceCriteria": ac,
        }
        patch = make_patch(s_fields)
        patch = add_parent_relation(patch, org_url, feature_id)
        try:
            wi = wit_client.create_work_item(patch, project, "User Story")
            story_id = wi.id
            created_stories.append((story_id, story_title))
            print(f"  User Story #{story_id}: {story_title}")
        except Exception as e:
            print(f"  FAILED Story: {story_title} — {e}")
            continue

        # Create Tasks under this story
        for task_title in task_titles:
            t_fields = {
                "System.Title":        task_title,
                "System.Description":  task_title,
                "System.AssignedTo":   fields["assigned_to"],
                "System.AreaPath":     fields["area_path"],
                "System.IterationPath": fields["iteration"],
                "Microsoft.VSTS.Scheduling.OriginalEstimate": args.estimate,
                "Microsoft.VSTS.Scheduling.RemainingWork":    args.estimate,
            }
            t_patch = make_patch(t_fields)
            t_patch = add_parent_relation(t_patch, org_url, story_id)
            try:
                wi = wit_client.create_work_item(t_patch, project, "Task")
                print(f"    Task #{wi.id}: {task_title} [{args.estimate}h]")
            except Exception as e:
                print(f"    FAILED Task: {task_title} — {e}")

    # Summary
    n_stories = len(story_titles)
    n_tasks = len(task_titles) * len(story_titles)
    feature_url = f"{org_url.rstrip('/')}/_workitems/edit/{feature_id}"
    print(f"\nTotal: 1 Feature | {n_stories} User Stories | {n_tasks} Tasks")
    print(f"Feature URL: {feature_url}")


if __name__ == "__main__":
    main()
