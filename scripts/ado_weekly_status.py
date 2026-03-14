#!/usr/bin/env python3
"""
ado_weekly_status.py — Generate a leadership-ready weekly Azure DevOps status email.

Usage:
    python3 scripts/ado_weekly_status.py [--sprint "path"] [--team "name"]
        [--team-name "Display Name"] [--project name] [--week-start YYYY-MM-DD]
        [--milestone "Milestone Name"] [--description "Narrative text"]
        [--board-url "https://..."]

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

DONE_STATES = {"Closed", "Resolved"}
LEADERSHIP_TYPES = {"Feature", "User Story"}


def last_monday():
    today = date.today()
    return today - timedelta(days=today.weekday())


def week_number(d):
    return datetime.strptime(str(d), "%Y-%m-%d").isocalendar()[1]


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


def fetch_items(wit_client, wiql_str, fields):
    result = wit_client.query_by_wiql(Wiql(query=wiql_str))
    ids = [r.id for r in (result.work_items or [])]
    if not ids:
        return []
    items = []
    for i in range(0, len(ids), 200):
        items.extend(wit_client.get_work_items(ids[i:i + 200], fields=fields))
    return items


def assignee_name(raw):
    if isinstance(raw, dict):
        return raw.get("uniqueName", raw.get("displayName", "Unassigned"))
    return str(raw or "Unassigned")


def days_stale(item):
    changed = item.fields.get("System.ChangedDate", "")
    if not changed:
        return 0
    try:
        d = datetime.fromisoformat(changed.rstrip("Z")).date()
        return (date.today() - d).days
    except Exception:
        return 0


def milestone_color(completion_pct, expected_rate, capacity_ratio, long_blocked_count, scope_creep_pct):
    if (completion_pct < expected_rate - 20
            or capacity_ratio > 1.3
            or long_blocked_count > 2
            or scope_creep_pct > 20):
        return "🔴 RED"
    if (completion_pct < expected_rate
            or 1.1 < capacity_ratio <= 1.3
            or 1 <= long_blocked_count <= 2):
        return "🟡 YELLOW"
    return "🟢 GREEN"


def main():
    parser = argparse.ArgumentParser(description="Generate leadership weekly status email")
    parser.add_argument("--sprint", help="Iteration path")
    parser.add_argument("--team", help="Team name (ADO)")
    parser.add_argument("--team-name", dest="team_name", help="Display name in email (defaults to --team)")
    parser.add_argument("--project", help="ADO project name")
    parser.add_argument("--week-start", dest="week_start", help="YYYY-MM-DD (default: last Monday)")
    parser.add_argument("--milestone", help="Milestone name for subject line")
    parser.add_argument("--description", help="Executive summary narrative paragraph")
    parser.add_argument("--board-url", dest="board_url", help="Scrum board URL")
    parser.add_argument("--area-path", dest="area_path",
                        help="ADO area path to filter by (e.g. 'Product_Mgmt\\\\Core')")
    args = parser.parse_args()

    org_url = os.environ.get("AZURE_DEVOPS_ORG_URL")
    pat = os.environ.get("AZURE_PERSONAL_ACCESS_TOKEN")
    project = args.project or os.environ.get("AZURE_DEVOPS_PROJECT")

    if not org_url:
        print("ERROR: AZURE_DEVOPS_ORG_URL environment variable not set"); sys.exit(1)
    if not pat:
        print("ERROR: AZURE_PERSONAL_ACCESS_TOKEN environment variable not set"); sys.exit(1)
    if not project:
        print("ERROR: --project not provided and AZURE_DEVOPS_PROJECT env var not set"); sys.exit(1)

    week_start = args.week_start or str(last_monday())
    week_end = str(date.today())
    week_num = week_number(week_start)
    five_days_ago = str(date.today() - timedelta(days=5))
    three_days_ago = str(date.today() - timedelta(days=3))
    team_display = args.team_name or args.team or project

    credentials = BasicAuthentication("", pat)
    connection = Connection(base_url=org_url, creds=credentials)
    wit_client = connection.clients.get_work_item_tracking_client()
    work_client = connection.clients.get_work_client()

    # Resolve sprint dates
    sprint_path = args.sprint
    sprint_name = sprint_path or project
    sprint_start = sprint_end = None

    if not sprint_path:
        try:
            tc = work_models.TeamContext(project=project, team=args.team)
            iterations = work_client.get_team_iterations(tc, timeframe="current")
            if iterations:
                cur = iterations[0]
                sprint_path = cur.path
                sprint_name = cur.name
                if cur.attributes:
                    sprint_start = str(cur.attributes.start_date)[:10] if cur.attributes.start_date else None
                    sprint_end = str(cur.attributes.finish_date)[:10] if cur.attributes.finish_date else None
        except Exception:
            sprint_path = project
    else:
        sprint_name = sprint_path.split("\\")[-1]
        try:
            parts = sprint_path.split("\\")
            rel = "\\".join(parts[1:]) if len(parts) > 1 else parts[0]
            node = wit_client.get_classification_node(project, "iterations", depth=0, path=rel)
            if node and node.attributes:
                sprint_start = str(node.attributes.get("startDate", "") or "")[:10] or None
                sprint_end = str(node.attributes.get("finishDate", "") or "")[:10] or None
        except Exception:
            pass

    days_left = working_days_remaining(sprint_end) if sprint_end else 0
    available_hours = days_left * 6

    # Board URL — sprint taskboard format
    board_url = args.board_url
    if not board_url and args.team and sprint_path:
        encoded_team = args.team.replace(" ", "%20")
        parts = sprint_path.split("\\")
        rel = "/".join(parts[1:]) if len(parts) > 1 else parts[0]
        board_url = f"{org_url.rstrip('/')}/{project}/_sprints/taskboard/{encoded_team}/{project}/{rel}"

    area_path = args.area_path
    area_filter = f"AND [System.AreaPath] UNDER '{area_path}'" if area_path else ""

    base_fields = ["System.Id", "System.Title", "System.WorkItemType",
                   "System.AssignedTo", "Microsoft.VSTS.Scheduling.StoryPoints"]

    # ── Q1: Completed this week (Features + Stories only) ──────────────────
    completed = fetch_items(wit_client, (
        f"SELECT [System.Id],[System.Title],[System.WorkItemType],[System.AssignedTo],"
        f"[Microsoft.VSTS.Scheduling.StoryPoints],[Microsoft.VSTS.Common.ClosedDate] "
        f"FROM WorkItems "
        f"WHERE [System.IterationPath] UNDER '{sprint_path}' "
        f"AND [System.TeamProject]='{project}' "
        f"{area_filter} "
        f"AND [System.State] IN ('Closed','Resolved') "
        f"AND [System.WorkItemType] IN ('Feature','User Story') "
        f"AND [Microsoft.VSTS.Common.ClosedDate] >= '{week_start}' "
        f"ORDER BY [Microsoft.VSTS.Common.ClosedDate] DESC"
    ), base_fields + ["Microsoft.VSTS.Common.ClosedDate"])

    # ── Q2: In Progress (Features + Stories only) ───────────────────────────
    in_progress = fetch_items(wit_client, (
        f"SELECT [System.Id],[System.Title],[System.WorkItemType],[System.AssignedTo],"
        f"[Microsoft.VSTS.Scheduling.StoryPoints],[System.ChangedDate] "
        f"FROM WorkItems "
        f"WHERE [System.IterationPath] UNDER '{sprint_path}' "
        f"AND [System.TeamProject]='{project}' "
        f"{area_filter} "
        f"AND [System.State]='Active' "
        f"AND [System.WorkItemType] IN ('Feature','User Story') "
        f"ORDER BY [System.AssignedTo]"
    ), base_fields + ["System.ChangedDate"])

    # ── Q3: Blockers (all types, stale ≥ 3 days or tagged blocked) ─────────
    blocked_raw = fetch_items(wit_client, (
        f"SELECT [System.Id],[System.Title],[System.WorkItemType],[System.AssignedTo],"
        f"[System.ChangedDate],[System.Tags] "
        f"FROM WorkItems "
        f"WHERE [System.IterationPath] UNDER '{sprint_path}' "
        f"AND [System.TeamProject]='{project}' "
        f"{area_filter} "
        f"AND [System.State]='Active' "
        f"AND ([System.ChangedDate] <= '{three_days_ago}' OR [System.Tags] CONTAINS 'blocked')"
    ), ["System.Id", "System.Title", "System.WorkItemType",
        "System.AssignedTo", "System.ChangedDate", "System.Tags"])

    # ── Q4: Coming Up — New Features/Stories in current sprint ─────────────
    upcoming = fetch_items(wit_client, (
        f"SELECT [System.Id],[System.Title],[System.WorkItemType],[System.AssignedTo],"
        f"[Microsoft.VSTS.Scheduling.StoryPoints] "
        f"FROM WorkItems "
        f"WHERE [System.IterationPath] UNDER '{sprint_path}' "
        f"AND [System.TeamProject]='{project}' "
        f"{area_filter} "
        f"AND [System.State]='New' "
        f"AND [System.WorkItemType] IN ('Feature','User Story') "
        f"ORDER BY [System.AssignedTo]"
    ), base_fields)

    # ── Q5: Overall completion (ALL types) ──────────────────────────────────
    all_items = fetch_items(wit_client, (
        f"SELECT [System.Id],[Microsoft.VSTS.Scheduling.StoryPoints],[System.State],"
        f"[System.WorkItemType] "
        f"FROM WorkItems "
        f"WHERE [System.IterationPath] UNDER '{sprint_path}' "
        f"AND [System.TeamProject]='{project}' "
        f"{area_filter}"
    ), ["System.Id", "Microsoft.VSTS.Scheduling.StoryPoints", "System.State",
        "System.WorkItemType"])

    # ── Q6: Scope Creep ─────────────────────────────────────────────────────
    scope_creep_items = []
    if sprint_start:
        scope_creep_items = fetch_items(wit_client, (
            f"SELECT [System.Id],[System.Title],[System.WorkItemType],[System.AssignedTo],"
            f"[Microsoft.VSTS.Scheduling.OriginalEstimate] "
            f"FROM WorkItems "
            f"WHERE [System.IterationPath] UNDER '{sprint_path}' "
            f"AND [System.TeamProject]='{project}' "
            f"{area_filter} "
            f"AND [System.CreatedDate] > '{sprint_start}' "
            f"AND [System.WorkItemType] IN ('Feature','User Story','Task','Bug')"
        ), ["System.Id", "System.Title", "System.WorkItemType",
            "System.AssignedTo", "Microsoft.VSTS.Scheduling.OriginalEstimate"])

    # ── Q7: Capacity (remaining work on non-done items) ─────────────────────
    active_work = fetch_items(wit_client, (
        f"SELECT [System.Id],[Microsoft.VSTS.Scheduling.RemainingWork] "
        f"FROM WorkItems "
        f"WHERE [System.IterationPath] UNDER '{sprint_path}' "
        f"AND [System.TeamProject]='{project}' "
        f"{area_filter} "
        f"AND [System.State] NOT IN ('Closed','Resolved')"
    ), ["System.Id", "Microsoft.VSTS.Scheduling.RemainingWork"])

    # ── Q8: Features in sprint (for Executive Summary) ──────────────────────
    features = fetch_items(wit_client, (
        f"SELECT [System.Id],[System.Title],[System.State],[System.AssignedTo] "
        f"FROM WorkItems "
        f"WHERE [System.IterationPath] UNDER '{sprint_path}' "
        f"AND [System.TeamProject]='{project}' "
        f"{area_filter} "
        f"AND [System.WorkItemType]='Feature' "
        f"ORDER BY [System.State],[System.Title]"
    ), ["System.Id", "System.Title", "System.State", "System.AssignedTo"])

    # ── Calculations ────────────────────────────────────────────────────────
    total_pts = sum(i.fields.get("Microsoft.VSTS.Scheduling.StoryPoints") or 0 for i in all_items)
    done_pts = sum(
        i.fields.get("Microsoft.VSTS.Scheduling.StoryPoints") or 0
        for i in all_items if i.fields.get("System.State") in DONE_STATES
    )
    total_count = len(all_items)
    done_count = sum(1 for i in all_items if i.fields.get("System.State") in DONE_STATES)
    total_story_count = sum(
        1 for i in all_items
        if i.fields.get("System.WorkItemType") == "User Story"
    )
    completion_pct = int(done_count / total_count * 100) if total_count else 0

    total_remaining_hours = sum(
        i.fields.get("Microsoft.VSTS.Scheduling.RemainingWork") or 0 for i in active_work
    )
    capacity_ratio = total_remaining_hours / available_hours if available_hours > 0 else 0
    capacity_pct = int(capacity_ratio * 100)

    scope_creep_hours = sum(
        i.fields.get("Microsoft.VSTS.Scheduling.OriginalEstimate") or 8
        for i in scope_creep_items
    )
    sprint_total_hours = total_count * 8  # rough baseline
    scope_creep_pct = int(scope_creep_hours / sprint_total_hours * 100) if sprint_total_hours > 0 else 0

    # Expected burn rate
    if sprint_start and sprint_end:
        try:
            start = datetime.fromisoformat(sprint_start).date()
            end = datetime.fromisoformat(sprint_end).date()
            total_days = max((end - start).days, 1)
            elapsed = (date.today() - start).days
            expected_rate = min(int(elapsed / total_days * 100), 100)
        except Exception:
            expected_rate = 50
    else:
        expected_rate = 50

    # Long-blocked (≥ 5 days)
    long_blocked = sorted(
        [i for i in blocked_raw if days_stale(i) >= 5],
        key=lambda i: days_stale(i), reverse=True
    )

    # Red flags
    red_flags = []
    if scope_creep_items:
        by_type = {}
        for i in scope_creep_items:
            t = i.fields.get("System.WorkItemType", "Other")
            by_type[t] = by_type.get(t, 0) + 1
        breakdown = ", ".join(f"{v} {k}s" for k, v in sorted(by_type.items()))
        red_flags.append(
            f"🚨 **SCOPE CREEP** — {len(scope_creep_items)} items added after sprint start "
            f"(+{scope_creep_hours:.0f}h estimated work — {breakdown})"
        )
    if available_hours > 0 and capacity_ratio > 1.1:
        red_flags.append(
            f"🚨 **CAPACITY RISK** — {total_remaining_hours:.0f}h remaining, "
            f"only {available_hours:.0f}h available ({capacity_pct}% of capacity)"
        )
    if long_blocked:
        worst = long_blocked[0]
        worst_title = (worst.fields.get("System.Title") or "")[:50]
        red_flags.append(
            f"🚨 **LONG BLOCKED** — {len(long_blocked)} items blocked/stale for 5+ days "
            f"(longest: #{worst.id} \"{worst_title}\" — {days_stale(worst)} days)"
        )

    color = milestone_color(completion_pct, expected_rate, capacity_ratio,
                            len(long_blocked), scope_creep_pct)
    milestone_status = "On Track" if "GREEN" in color else ("Behind (ETA: TBD)" if "RED" in color else "At Risk")
    milestone_name = args.milestone or sprint_name

    # Auto-generate executive summary from Features
    feat_done = [f for f in features if f.fields.get("System.State") in DONE_STATES]
    feat_active = [f for f in features if f.fields.get("System.State") == "Active"]
    feat_new = [f for f in features
                if f.fields.get("System.State") not in DONE_STATES
                and f.fields.get("System.State") != "Active"]

    summary_lines = [
        f"Sprint {sprint_name} contains {len(features)} Feature(s) and {total_story_count} User "
        f"{'Story' if total_story_count == 1 else 'Stories'}.",
        "",
    ]
    if feat_done:
        names = ", ".join(
            f"\"{(f.fields.get('System.Title') or '')[:60]}\""
            for f in feat_done[:5]
        )
        summary_lines.append(f"**Completed ({len(feat_done)}):** {names}")
    if feat_active:
        names = ", ".join(
            f"\"{(f.fields.get('System.Title') or '')[:60]}\""
            for f in feat_active[:5]
        )
        summary_lines.append(f"**In Progress ({len(feat_active)}):** {names}")
    if feat_new:
        summary_lines.append(f"**Not Started ({len(feat_new)}):** {len(feat_new)} feature(s) pending.")
    if not features:
        summary_lines = ["No Features found in this sprint for the selected area path."]
    if args.description:
        summary_lines += ["", args.description]

    # Board / scrum link
    board_line = f"Scrum Board: {board_url}" if board_url else ""

    # ── Build report ────────────────────────────────────────────────────────
    lines = [
        f"Subject: {team_display} Weekly Status - {sprint_name} | Milestone: {color} {sprint_end or ''}",
        "",
        f"Hello Team,",
        f"Sharing the {team_display} weekly status update for {sprint_name}; "
        f"{week_start} – {week_end} (Week {week_num})",
        "",
        "For task-level progress, owners, and latest movement across work items, please refer to the",
    ]
    if board_line:
        lines.append(board_line)
    lines += [
        "",
        "---",
        "",
        "## Executive Summary",
        f"**Overall Status: {color}**",
        "",
    ] + summary_lines + [
        "",
        f"**Milestone:** {milestone_name} — Dev Complete: {sprint_end or 'TBD'} — {milestone_status}",
        f"**Sprint Progress:** {completion_pct}% complete "
        f"({done_count}/{total_count} items"
        + (f" | {done_pts:.0f}/{total_pts:.0f} pts" if total_pts else "")
        + ")",
        "",
        "---",
        "",
        "## 🚨 Red Flags",
        "",
    ]
    if red_flags:
        for flag in red_flags:
            lines.append(f"- {flag}")
    else:
        lines.append("No Red Flags this week.")

    # Completed table
    lines += [
        "",
        "---",
        "",
        f"## Features & User Stories — Completed This Week ({len(completed)})",
    ]
    if completed:
        lines += [
            f"| {'#':<7} | {'Title':<50} | {'Owner':<25} | {'Pts':<5} |",
            f"|{'-'*9}|{'-'*52}|{'-'*27}|{'-'*7}|",
        ]
        for item in completed:
            f = item.fields
            pts = f.get("Microsoft.VSTS.Scheduling.StoryPoints") or "—"
            lines.append(
                f"| #{item.id:<6} | {(f.get('System.Title') or '')[:50]:<50} | "
                f"{assignee_name(f.get('System.AssignedTo'))[:25]:<25} | {str(pts):<5} |"
            )
    else:
        lines.append("_No Features or User Stories closed this week._")

    # In Progress table
    lines += [
        "",
        "---",
        "",
        f"## Features & User Stories — In Progress ({len(in_progress)})",
    ]
    if in_progress:
        lines += [
            f"| {'#':<7} | {'Title':<50} | {'Owner':<25} | {'Last Updated':<14} |",
            f"|{'-'*9}|{'-'*52}|{'-'*27}|{'-'*16}|",
        ]
        for item in in_progress:
            f = item.fields
            stale = days_stale(item)
            updated = f"{stale} day{'s' if stale != 1 else ''} ago" if stale is not None else "—"
            lines.append(
                f"| #{item.id:<6} | {(f.get('System.Title') or '')[:50]:<50} | "
                f"{assignee_name(f.get('System.AssignedTo'))[:25]:<25} | {updated:<14} |"
            )
    else:
        lines.append("_No Features or User Stories currently active._")

    # Blockers table
    lines += [
        "",
        "---",
        "",
        f"## Blockers / At-Risk ({len(blocked_raw)} items, {len(long_blocked)} long-blocked ≥ 5 days)",
    ]
    if blocked_raw:
        lines += [
            f"| {'#':<7} | {'Title':<50} | {'Type':<12} | {'Owner':<25} | {'Stale':>6} | {'Flag':<12} |",
            f"|{'-'*9}|{'-'*52}|{'-'*14}|{'-'*27}|{'-'*8}|{'-'*14}|",
        ]
        for item in sorted(blocked_raw, key=lambda i: days_stale(i), reverse=True):
            f = item.fields
            stale = days_stale(item)
            tags = (f.get("System.Tags") or "").lower()
            flag = "BLOCKED" if "blocked" in tags else ("LONG STALE" if stale >= 5 else "STALE")
            lines.append(
                f"| #{item.id:<6} | {(f.get('System.Title') or '')[:50]:<50} | "
                f"{(f.get('System.WorkItemType') or '')[:12]:<12} | "
                f"{assignee_name(f.get('System.AssignedTo'))[:25]:<25} | "
                f"{stale:>5}d | {flag:<12} |"
            )
    else:
        lines.append("_No blockers or at-risk items._")

    # Coming Up table
    lines += [
        "",
        "---",
        "",
        f"## Coming Up Next ({len(upcoming)} items not yet started)",
    ]
    if upcoming:
        lines += [
            f"| {'#':<7} | {'Title':<50} | {'Owner':<25} |",
            f"|{'-'*9}|{'-'*52}|{'-'*27}|",
        ]
        for item in upcoming:
            f = item.fields
            lines.append(
                f"| #{item.id:<6} | {(f.get('System.Title') or '')[:50]:<50} | "
                f"{assignee_name(f.get('System.AssignedTo'))[:25]:<25} |"
            )
    else:
        lines.append("_No unstarted Features or User Stories._")

    # Overall metrics table
    lines += [
        "",
        "---",
        "",
        "## Overall Sprint Metrics (all work item types)",
        "",
        f"| {'Metric':<25} | {'Value':<30} |",
        f"|{'-'*27}|{'-'*32}|",
        f"| {'Total Items':<25} | {total_count:<30} |",
        f"| {'Completed':<25} | {done_count} ({completion_pct}%){'':<20} |",
        f"| {'Remaining':<25} | {total_count - done_count:<30} |",
    ]
    if total_pts:
        lines.append(f"| {'Story Points Done':<25} | {done_pts:.0f} / {total_pts:.0f}{'':<22} |")
    lines += [
        f"| {'Remaining Work':<25} | {total_remaining_hours:.0f}h{'':<27} |",
        f"| {'Available Hours':<25} | {available_hours:.0f}h ({days_left} working days){'':<10} |",
        f"| {'Capacity Utilization':<25} | {capacity_pct}%{'':<28} |",
    ]
    if scope_creep_items:
        lines.append(
            f"| {'Mid-Sprint Additions':<25} | {len(scope_creep_items)} items (+{scope_creep_hours:.0f}h){'':<15} |"
        )

    lines += [
        "",
        "---",
        f"*Generated from Azure DevOps | {project} | {sprint_name} | {date.today()}*",
    ]

    print("\n".join(lines))


if __name__ == "__main__":
    main()
