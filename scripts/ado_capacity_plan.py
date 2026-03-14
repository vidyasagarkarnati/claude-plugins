#!/usr/bin/env python3
"""
ado_capacity_plan.py — Show team capacity vs workload for the current or specified sprint.

Usage:
    python3 scripts/ado_capacity_plan.py [--sprint "path"] [--team "name"]
                                          [--project name] [--hours-per-day n]

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
        return 0
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


def utilization_status(pct):
    if pct > 110:
        return "OVER-ALLOCATED"
    elif pct >= 90:
        return "Fully Loaded"
    elif pct >= 60:
        return "On Track"
    else:
        return "Under-allocated"


def main():
    parser = argparse.ArgumentParser(description="Show Azure DevOps sprint capacity plan")
    parser.add_argument("--sprint", help="Iteration path")
    parser.add_argument("--team", help="Team name")
    parser.add_argument("--project", help="ADO project name")
    parser.add_argument("--hours-per-day", dest="hours_per_day", type=float, default=6,
                        help="Working hours per day (default: 6)")
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
    finish_date_str = None

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
            if current.attributes and current.attributes.finish_date:
                finish_date_str = str(current.attributes.finish_date)[:10]
        except Exception as e:
            print(f"ERROR: Could not resolve current sprint — {e}")
            sys.exit(1)
    else:
        sprint_name = sprint_path.split("\\")[-1]
        try:
            parts = sprint_path.split("\\")
            relative_path = "\\".join(parts[1:]) if len(parts) > 1 else parts[0]
            node = wit_client.get_classification_node(project, "iterations", depth=0, path=relative_path)
            if node and node.attributes:
                finish_date_str = str(node.attributes.get("finishDate", "") or "")[:10] or None
        except Exception:
            pass

    days_remaining = working_days_remaining(finish_date_str) if finish_date_str else "?"
    available_hours = (days_remaining * args.hours_per_day) if isinstance(days_remaining, int) else None

    # Query active work items in sprint with remaining work
    wiql_str = (
        f"SELECT [System.Id],[System.Title],[System.State],[System.AssignedTo],"
        f"[System.WorkItemType],[Microsoft.VSTS.Scheduling.RemainingWork] "
        f"FROM WorkItems "
        f"WHERE [System.IterationPath]='{sprint_path}' "
        f"AND [System.TeamProject]='{project}' "
        f"AND [System.State] NOT IN ('Closed','Resolved','Done') "
        f"ORDER BY [System.AssignedTo]"
    )
    try:
        result = wit_client.query_by_wiql(Wiql(query=wiql_str))
        ids = [r.id for r in (result.work_items or [])]
    except Exception as e:
        print(f"ERROR: WIQL query failed — {e}")
        sys.exit(1)

    fields = [
        "System.Id", "System.Title", "System.State", "System.AssignedTo",
        "System.WorkItemType", "Microsoft.VSTS.Scheduling.RemainingWork"
    ]
    items = []
    for i in range(0, len(ids), 200):
        items.extend(wit_client.get_work_items(ids[i:i+200], fields=fields))

    # Group by assignee
    by_assignee = {}  # email -> {items: [], remaining: float}
    for item in items:
        f = item.fields
        assignee_raw = f.get("System.AssignedTo") or {}
        assignee = assignee_raw.get("uniqueName", "Unassigned") if isinstance(assignee_raw, dict) else str(assignee_raw or "Unassigned")
        remaining = f.get("Microsoft.VSTS.Scheduling.RemainingWork") or 0
        if assignee not in by_assignee:
            by_assignee[assignee] = {"count": 0, "remaining": 0.0}
        by_assignee[assignee]["count"] += 1
        by_assignee[assignee]["remaining"] += remaining

    # Print report
    print(f"\nSprint Capacity Plan — {sprint_name}")
    print(f"Sprint End: {finish_date_str or '?'} | Days Remaining: {days_remaining} | Hours/Day: {args.hours_per_day}")
    print()

    col1, col2, col3, col4, col5, col6 = 30, 14, 15, 15, 13, 20
    header = (f"{'Assignee':<{col1}} {'Active Items':>{col2}} {'Remaining Hrs':>{col3}} "
              f"{'Available Hrs':>{col4}} {'Utilization':>{col5}} {'Status':<{col6}}")
    print(header)
    print("-" * len(header))

    total_items = total_remaining = 0
    recommendations = []

    for assignee in sorted(by_assignee.keys()):
        data = by_assignee[assignee]
        count = data["count"]
        remaining = data["remaining"]
        total_items += count
        total_remaining += remaining

        if assignee == "Unassigned" or available_hours is None:
            util_str = "—"
            status = "NEEDS ASSIGNMENT" if assignee == "Unassigned" else "—"
        else:
            util = (remaining / available_hours * 100) if available_hours > 0 else 0
            util_str = f"{util:.0f}%"
            status = utilization_status(util)
            if status == "OVER-ALLOCATED":
                recommendations.append(f"- Reduce load for {assignee} ({remaining:.0f}h remaining vs {available_hours:.0f}h available)")
            elif status == "Under-allocated" and count > 0:
                recommendations.append(f"- {assignee} has capacity ({remaining:.0f}h remaining, {available_hours:.0f}h available)")

        avail_str = f"{available_hours:.0f}h" if available_hours is not None else "—"
        print(f"{assignee:<{col1}} {count:>{col2}} {remaining:>{col3}.0f}h "
              f"{avail_str:>{col4}} {util_str:>{col5}} {status:<{col6}}")

    if "Unassigned" in by_assignee:
        recommendations.append(f"- Assign {by_assignee['Unassigned']['count']} unassigned items before sprint end")

    print(f"\nTeam Total: {total_items} items | {total_remaining:.0f}h remaining")

    if recommendations:
        print("\nRecommendations:")
        for r in recommendations:
            print(r)


if __name__ == "__main__":
    main()
