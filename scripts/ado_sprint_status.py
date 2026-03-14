#!/usr/bin/env python3
"""
ado_sprint_status.py — Show Azure DevOps sprint status: burndown, completion %, blockers, health.

Usage:
    python3 scripts/ado_sprint_status.py [--sprint "path"] [--team "name"] [--project name]

Auth (env vars):
    AZURE_DEVOPS_ORG_URL          e.g. https://dev.azure.com/myorg
    AZURE_PERSONAL_ACCESS_TOKEN   PAT with Work Items read scope
    AZURE_DEVOPS_PROJECT          Default project name
"""

import argparse
import os
import sys
from datetime import date, datetime, timedelta

try:
    from azure.devops.connection import Connection
    from azure.devops.v7_1.work_item_tracking.models import Wiql
    from azure.devops.v7_1.work import models as work_models
    from msrest.authentication import BasicAuthentication
except ImportError:
    print("ERROR: azure-devops package not installed.")
    print("Run: pip install azure-devops")
    sys.exit(1)


def working_days_remaining(end_date_str):
    try:
        end = datetime.fromisoformat(end_date_str.rstrip("Z")).date()
    except Exception:
        return "?"
    today = date.today()
    if today > end:
        return 0
    count = 0
    d = today
    while d <= end:
        if d.weekday() < 5:
            count += 1
        d += timedelta(days=1)
    return count


def bar(done, total, width=20):
    if total == 0:
        return "░" * width
    filled = int(done / total * width)
    return "█" * filled + "░" * (width - filled)


def main():
    parser = argparse.ArgumentParser(description="Show Azure DevOps sprint status")
    parser.add_argument("--sprint", help="Iteration path (e.g. 'MyProject\\Sprint 5')")
    parser.add_argument("--team", help="Team name")
    parser.add_argument("--project", help="ADO project name")
    args = parser.parse_args()

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

    credentials = BasicAuthentication("", pat)
    connection = Connection(base_url=org_url, creds=credentials)
    wit_client = connection.clients.get_work_item_tracking_client()
    work_client = connection.clients.get_work_client()

    # Resolve sprint
    sprint_path = args.sprint
    sprint_name = sprint_path
    sprint_start = sprint_end = None

    if not sprint_path:
        try:
            team_context = work_models.TeamContext(project=project, team=args.team)
            iterations = work_client.get_team_iterations(team_context, timeframe="current")
            if not iterations:
                print("ERROR: No current sprint found. Use --sprint to specify one.")
                sys.exit(1)
            current = iterations[0]
            sprint_path = current.path
            sprint_name = current.name
            if current.attributes:
                sprint_start = str(current.attributes.start_date)[:10] if current.attributes.start_date else None
                sprint_end = str(current.attributes.finish_date)[:10] if current.attributes.finish_date else None
        except Exception as e:
            print(f"ERROR: Could not resolve current sprint — {e}")
            sys.exit(1)
    else:
        # Sprint path provided explicitly — look up dates from classification nodes
        sprint_name = sprint_path.split("\\")[-1]
        try:
            # The path relative to project is everything after "Project\"
            parts = sprint_path.split("\\")
            relative_path = "\\".join(parts[1:]) if len(parts) > 1 else parts[0]
            import urllib.parse
            encoded = urllib.parse.quote(relative_path, safe="")
            node = wit_client.get_classification_node(
                project, "iterations", depth=0,
                path=relative_path
            )
            if node and node.attributes:
                sprint_start = str(node.attributes.get("startDate", "") or "")[:10] or None
                sprint_end = str(node.attributes.get("finishDate", "") or "")[:10] or None
        except Exception:
            pass  # dates remain None; not fatal

    days_remaining = working_days_remaining(sprint_end) if sprint_end else "?"

    # Query sprint work items
    wiql_str = (
        f"SELECT [System.Id],[System.Title],[System.State],[System.AssignedTo],"
        f"[System.WorkItemType],[Microsoft.VSTS.Scheduling.StoryPoints],"
        f"[System.ChangedDate],[System.Tags] "
        f"FROM WorkItems "
        f"WHERE [System.IterationPath]='{sprint_path}' "
        f"AND [System.TeamProject]='{project}' "
        f"ORDER BY [System.WorkItemType],[System.State]"
    )
    try:
        result = wit_client.query_by_wiql(Wiql(query=wiql_str))
        ids = [r.id for r in (result.work_items or [])]
    except Exception as e:
        print(f"ERROR: WIQL query failed — {e}")
        sys.exit(1)

    if not ids:
        print(f"No work items found in sprint: {sprint_path}")
        sys.exit(0)

    fields = [
        "System.Id", "System.Title", "System.State", "System.AssignedTo",
        "System.WorkItemType", "Microsoft.VSTS.Scheduling.StoryPoints",
        "System.ChangedDate", "System.Tags"
    ]
    items = []
    batch_size = 200
    for i in range(0, len(ids), batch_size):
        items.extend(wit_client.get_work_items(ids[i:i+batch_size], fields=fields))

    # Analyze
    done_states = {"Resolved", "Closed", "Done"}
    type_state_counts = {}  # type -> state -> count
    total_pts = done_pts = 0
    at_risk = []
    today = date.today()
    three_days_ago = today - timedelta(days=3)

    for item in items:
        f = item.fields
        wit = f.get("System.WorkItemType", "Other")
        state = f.get("System.State", "Unknown")
        pts = f.get("Microsoft.VSTS.Scheduling.StoryPoints") or 0
        changed_raw = f.get("System.ChangedDate", "")
        tags = (f.get("System.Tags") or "").lower()
        assignee_raw = f.get("System.AssignedTo") or {}
        assignee = assignee_raw.get("uniqueName", assignee_raw) if isinstance(assignee_raw, dict) else str(assignee_raw)

        if wit not in type_state_counts:
            type_state_counts[wit] = {}
        type_state_counts[wit][state] = type_state_counts[wit].get(state, 0) + 1

        total_pts += pts
        if state in done_states:
            done_pts += pts

        # Blocker detection
        if state == "Active":
            stale = False
            days_stale = None
            if changed_raw:
                try:
                    changed = datetime.fromisoformat(changed_raw.rstrip("Z")).date()
                    days_stale = (today - changed).days
                    stale = changed <= three_days_ago
                except Exception:
                    pass
            is_blocked = "blocked" in tags or "impediment" in tags
            if stale or is_blocked:
                at_risk.append({
                    "id": item.id,
                    "title": f.get("System.Title", ""),
                    "assignee": assignee,
                    "days_stale": days_stale,
                    "flag": "BLOCKED" if is_blocked else "STALE",
                })

    total_items = len(items)
    done_items = sum(
        cnt for states in type_state_counts.values()
        for st, cnt in states.items() if st in done_states
    )
    completion_pct = int(done_items / total_items * 100) if total_items else 0
    pts_pct = int(done_pts / total_pts * 100) if total_pts else 0

    # Sprint health
    if sprint_start and sprint_end:
        try:
            start = datetime.fromisoformat(sprint_start).date()
            end = datetime.fromisoformat(sprint_end).date()
            total_days = max((end - start).days, 1)
            elapsed_days = (today - start).days
            expected_rate = min(int(elapsed_days / total_days * 100), 100)
        except Exception:
            expected_rate = 50
    else:
        expected_rate = 50

    at_risk_count = len(at_risk)
    if completion_pct >= expected_rate and at_risk_count <= 2:
        health = "Healthy"
    elif completion_pct < expected_rate - 20 or at_risk_count > 5:
        health = "Critical"
    else:
        health = "At Risk"

    # Print report
    date_range = f"{sprint_start} → {sprint_end}" if sprint_start and sprint_end else ""
    print(f"\nSprint Status — {sprint_name}")
    if date_range:
        print(f"{date_range} | {days_remaining} days remaining")
    print()
    print("Progress")
    print(f"  By Count:        [{done_items}/{total_items}] {completion_pct}%  {bar(done_items, total_items)}")
    if total_pts:
        print(f"  By Story Points: [{done_pts}/{total_pts} pts] {pts_pct}%  {bar(done_pts, total_pts)}")
    print()

    # Work item breakdown table
    all_states = ["New", "Active", "Resolved", "Closed"]
    all_types = sorted(type_state_counts.keys())
    header = f"{'Type':<15}" + "".join(f"{s:>10}" for s in all_states) + f"{'Total':>8}"
    print("Work Item Breakdown")
    print(header)
    print("-" * len(header))
    for wit in all_types:
        row = f"{wit:<15}"
        counts = type_state_counts[wit]
        total_row = sum(counts.values())
        for s in all_states:
            row += f"{counts.get(s, 0):>10}"
        row += f"{total_row:>8}"
        print(row)
    print()

    if at_risk:
        print("At-Risk / Blocked Items")
        print(f"{'ID':<8} {'Title':<40} {'Assignee':<25} {'Days Stale':>10} {'Flag':<10}")
        print("-" * 100)
        for item in at_risk:
            stale_str = f"{item['days_stale']} days" if item['days_stale'] is not None else "—"
            title = item['title'][:38] + ".." if len(item['title']) > 40 else item['title']
            assignee = (item['assignee'] or "Unassigned")[:23]
            print(f"#{item['id']:<7} {title:<40} {assignee:<25} {stale_str:>10} {item['flag']:<10}")
        print()

    print(f"Sprint Health: {health}")
    print(f"({completion_pct}% complete, {at_risk_count} items at risk, {days_remaining} days left)")


if __name__ == "__main__":
    main()
