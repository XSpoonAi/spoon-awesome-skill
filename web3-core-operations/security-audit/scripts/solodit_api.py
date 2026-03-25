#!/usr/bin/env python3
"""
Solodit API Client - Search smart contract vulnerabilities
Requires: SOLODIT_API_KEY environment variable
"""

import os
import sys
import json
import argparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE_URL = "https://solodit.cyfrin.io/api/v1/solodit"
ENDPOINT = "/findings"


def get_api_key():
    """Get API key from environment variable."""
    key = os.environ.get("SOLODIT_API_KEY")
    if not key:
        print("Error: SOLODIT_API_KEY environment variable not set", file=sys.stderr)
        print("Get your API key at https://solodit.cyfrin.io", file=sys.stderr)
        sys.exit(1)
    return key


def search_findings(
    keywords=None,
    impact=None,
    firms=None,
    tags=None,
    protocol=None,
    category=None,
    languages=None,
    days=None,
    quality_score=None,
    rarity_score=None,
    sort_field="Recency",
    sort_direction="Desc",
    page=1,
    page_size=50,
):
    """
    Search Solodit findings with filters.
    
    Args:
        keywords: Search text in title and content
        impact: List of severity levels (HIGH, MEDIUM, LOW, GAS)
        firms: List of audit firm names
        tags: List of vulnerability tags
        protocol: Protocol name (partial match)
        category: List of protocol categories
        languages: List of programming languages
        days: Filter by recent days (30, 60, 90)
        quality_score: Minimum quality score (0-5)
        rarity_score: Minimum rarity score (0-5)
        sort_field: Sort by Recency, Quality, or Rarity
        sort_direction: Desc or Asc
        page: Page number (starts at 1)
        page_size: Results per page (max 100)
    
    Returns:
        API response dict with findings, metadata, and rateLimit
    """
    api_key = get_api_key()
    
    filters = {}
    
    if keywords:
        filters["keywords"] = keywords
    
    if impact:
        filters["impact"] = impact if isinstance(impact, list) else [impact]
    
    if firms:
        firm_list = firms if isinstance(firms, list) else [firms]
        filters["firms"] = [{"value": f} for f in firm_list]
    
    if tags:
        tag_list = tags if isinstance(tags, list) else [tags]
        filters["tags"] = [{"value": t} for t in tag_list]
    
    if protocol:
        filters["protocol"] = protocol
    
    if category:
        cat_list = category if isinstance(category, list) else [category]
        filters["protocolCategory"] = [{"value": c} for c in cat_list]
    
    if languages:
        lang_list = languages if isinstance(languages, list) else [languages]
        filters["languages"] = [{"value": l} for l in lang_list]
    
    if days:
        filters["reported"] = {"value": str(days)}
    
    if quality_score is not None:
        filters["qualityScore"] = quality_score
    
    if rarity_score is not None:
        filters["rarityScore"] = rarity_score
    
    filters["sortField"] = sort_field
    filters["sortDirection"] = sort_direction
    
    payload = {
        "page": page,
        "pageSize": min(page_size, 100),
        "filters": filters,
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Cyfrin-API-Key": api_key,
    }
    
    try:
        req = Request(
            f"{BASE_URL}{ENDPOINT}",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"HTTP Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def format_finding(finding, verbose=False):
    """Format a single finding for display."""
    output = []
    output.append(f"[{finding.get('impact', 'N/A')}] {finding.get('title', 'No title')}")
    output.append(f"  ID: {finding.get('id', 'N/A')}")
    output.append(f"  Firm: {finding.get('firm_name', 'N/A')}")
    output.append(f"  Protocol: {finding.get('protocol_name', 'N/A')}")
    output.append(f"  Quality: {finding.get('quality_score', 'N/A')}/5")
    output.append(f"  Rarity: {finding.get('general_score', 'N/A')}/5")
    
    if finding.get('source_link'):
        output.append(f"  Link: {finding.get('source_link')}")
    
    tags = finding.get('issues_issuetagscore', [])
    if tags:
        tag_names = [t.get('tags_tag', {}).get('title', '') for t in tags]
        output.append(f"  Tags: {', '.join(filter(None, tag_names))}")
    
    if verbose and finding.get('content'):
        output.append(f"\n  Content:\n  {finding.get('content')[:500]}...")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Search Solodit smart contract vulnerabilities"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    search_parser = subparsers.add_parser("search", help="Search findings")
    search_parser.add_argument("--keywords", "-k", help="Search keywords")
    search_parser.add_argument(
        "--impact", "-i",
        help="Severity levels (comma-separated: HIGH,MEDIUM,LOW,GAS)"
    )
    search_parser.add_argument(
        "--firms", "-f",
        help="Audit firms (comma-separated)"
    )
    search_parser.add_argument(
        "--tags", "-t",
        help="Vulnerability tags (comma-separated)"
    )
    search_parser.add_argument("--protocol", "-p", help="Protocol name")
    search_parser.add_argument(
        "--category", "-c",
        help="Protocol categories (comma-separated)"
    )
    search_parser.add_argument(
        "--languages", "-l",
        help="Programming languages (comma-separated)"
    )
    search_parser.add_argument(
        "--days", "-d",
        type=int,
        choices=[30, 60, 90],
        help="Recent days filter"
    )
    search_parser.add_argument(
        "--quality",
        type=int,
        choices=[0, 1, 2, 3, 4, 5],
        help="Minimum quality score"
    )
    search_parser.add_argument(
        "--rarity",
        type=int,
        choices=[0, 1, 2, 3, 4, 5],
        help="Minimum rarity score"
    )
    search_parser.add_argument(
        "--sort",
        choices=["Recency", "Quality", "Rarity"],
        default="Recency",
        help="Sort field"
    )
    search_parser.add_argument(
        "--order",
        choices=["Desc", "Asc"],
        default="Desc",
        help="Sort order"
    )
    search_parser.add_argument(
        "--page",
        type=int,
        default=1,
        help="Page number"
    )
    search_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Results per page (max 100)"
    )
    search_parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON"
    )
    search_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show content preview"
    )
    
    args = parser.parse_args()
    
    if args.command == "search":
        impact = args.impact.split(",") if args.impact else None
        firms = args.firms.split(",") if args.firms else None
        tags = args.tags.split(",") if args.tags else None
        category = args.category.split(",") if args.category else None
        languages = args.languages.split(",") if args.languages else None
        
        result = search_findings(
            keywords=args.keywords,
            impact=impact,
            firms=firms,
            tags=tags,
            protocol=args.protocol,
            category=category,
            languages=languages,
            days=args.days,
            quality_score=args.quality,
            rarity_score=args.rarity,
            sort_field=args.sort,
            sort_direction=args.order,
            page=args.page,
            page_size=args.limit,
        )
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            metadata = result.get("metadata", {})
            rate_limit = result.get("rateLimit", {})
            findings = result.get("findings", [])
            
            print(f"Found {metadata.get('totalResults', 0)} findings "
                  f"(page {metadata.get('currentPage', 1)}/{metadata.get('totalPages', 1)})")
            print(f"Rate limit: {rate_limit.get('remaining', 'N/A')}/{rate_limit.get('limit', 'N/A')}")
            print("-" * 60)
            
            for finding in findings:
                print(format_finding(finding, verbose=args.verbose))
                print("-" * 60)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
