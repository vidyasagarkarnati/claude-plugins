#!/usr/bin/env python3
"""
ado_create_task.py — Create an Azure DevOps Task linked to a parent User Story.

Usage:
    python3 scripts/ado_create_task.py --title "Task" --description "..." \\
        --parent <story-id> \\
        [--assigned-to email] [--area-path path] [--iteration path] \\
        [--estimate hours] [--project name]

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


def prompt_if_missing(d, field, label):
    if not d.get(field):
        while True:
            value = input(f"  {label}: ").strip()
            if value:
                d[field] = value
                break
            print("  Value cannot be empty.")


def resolve_parent_story(wit_client, project):
    """Query open User Stories and ask user to pick one."""
    print("\nNo --parent provided. Fetching open User Stories...\n")
    wiql = Wiql(query=(
        f"SELECT [System.Id],[System.Title] FROM WorkItems "
        f"WHERE [System.TeamProject]='{project}' "
        f"AND [System.WorkItemType]='User Story' "
        f"AND [System.State]<>'Closed' "
        f"ORDER BY [System.Id] DESC"
    ))
    try:
        result = wit_client.query_by_wiql(wiql, project=project)
        ids = [r.id for r in (result.work_items or [])]
        if not ids:
            print("No open User Stories found. Create a User Story first.")
            sys.exit(1)
        items = wit_client.get_work_items(ids[:20], fields=["System.Id", "System.Title"])
        print(f"{'ID':<8} Title")
        print("-" * 60)
        for item in items:
            print(f"#{item.id:<7} {item.fields.get('System.Title', '')}")
        print()
        while True:
            val = input("Enter parent User Story ID: ").strip().lstrip("#")
            if val.isdigit():
                return int(val)
            print("  Please enter a numeric ID.")
    except Exception as e:
        print(f"ERROR: Could not query User Stories — {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Create an Azure DevOps Task")
    parser.add_argument("--title", required=True, help="Task title")
    parser.add_argument("--description", required=True, help="Task description")
    parser.add_argument("--parent", type=int, help="Parent User Story work item ID")
    parser.add_argument("--assigned-to", dest="assigned_to", help="Assignee email")
    parser.add_argument("--area-path", dest="area_path", help="Area path")
    parser.add_argument("--iteration", dest="iteration", help="Iteration path")
    parser.add_argument("--estimate", type=int, default=8,
                        help="Original estimate in hours (default: 8)")
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

    # Connect
    credentials = BasicAuthentication("", pat)
    connection = Connection(base_url=org_url, creds=credentials)
    wit_client = connection.clients.get_work_item_tracking_client()

    # Resolve parent User Story
    parent_id = args.parent or resolve_parent_story(wit_client, project)

    # Prompt for missing mandatory fields
    fields = {
        "assigned_to": args.assigned_to,
        "area_path":   args.area_path,
        "iteration":   args.iteration,
    }
    prompts = {
        "assigned_to": "Assigned To (e.g. user@company.com)",
        "area_path":   "Area Path (e.g. Product_Mgmt\\Core)",
        "iteration":   "Iteration Path (e.g. Product_Mgmt\\Product_Backlog)",
    }
    missing = [f for f in prompts if not fields[f]]
    if missing:
        print("\nSome required fields are not set. Please provide them now:\n")
        for f in missing:
            prompt_if_missing(fields, f, prompts[f])
        print()

    estimate = args.estimate

    # Create Task
    t_fields = {
        "System.Title":        args.title,
        "System.Description":  args.description,
        "System.AssignedTo":   fields["assigned_to"],
        "System.AreaPath":     fields["area_path"],
        "System.IterationPath": fields["iteration"],
        "Microsoft.VSTS.Scheduling.OriginalEstimate": estimate,
        "Microsoft.VSTS.Scheduling.RemainingWork":    estimate,
    }
    patch = make_patch(t_fields)
    patch = add_parent_relation(patch, org_url, parent_id)

    try:
        wi = wit_client.create_work_item(patch, project, "Task")
        task_id = wi.id
    except Exception as e:
        print(f"ERROR: Failed to create Task — {e}")
        sys.exit(1)

    task_url = f"{org_url.rstrip('/')}/_workitems/edit/{task_id}"
    print(f"""
Task Created

  ID:                #{task_id}
  Title:             {args.title}
  Assigned:          {fields['assigned_to']}
  Area Path:         {fields['area_path']}
  Iteration:         {fields['iteration']}
  Original Estimate: {estimate}h
  Remaining Work:    {estimate}h
  Parent Story:      #{parent_id}
  URL:               {task_url}""")


if __name__ == "__main__":
    main()
