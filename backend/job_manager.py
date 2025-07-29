#!/usr/bin/env python3
"""
Command-line tool for viewing and managing LinkedIn Agent job results.
Provides formatted output for job data stored in the storage folder.
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.storage_manager import JobStorageManager
from src.schemas_output import JobStatus

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Agent Job Manager")
    parser.add_argument("--storage-dir", default="../storage/data", 
                       help="Storage directory path (default: ../storage/data)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List jobs command
    list_parser = subparsers.add_parser("list", help="List all jobs")
    list_parser.add_argument("--status", choices=["pending", "processing", "completed", "failed", "cancelled"],
                            help="Filter by job status")
    list_parser.add_argument("--limit", type=int, default=20, help="Maximum number of jobs to show")
    
    # Show job command
    show_parser = subparsers.add_parser("show", help="Show detailed job result")
    show_parser.add_argument("job_id", help="Job ID to display")
    show_parser.add_argument("--format", choices=["json", "summary", "csv"], default="summary",
                            help="Output format")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export jobs to Excel")
    export_parser.add_argument("job_ids", nargs="+", help="Job IDs to export")
    export_parser.add_argument("--output", help="Output file path")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test scraping a URL")
    test_parser.add_argument("url", help="URL to test scrape")
    
    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean old jobs")
    clean_parser.add_argument("--days", type=int, default=30, 
                             help="Remove jobs older than this many days")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize storage manager
    storage_manager = JobStorageManager(args.storage_dir)
    
    try:
        if args.command == "list":
            list_jobs(storage_manager, args)
        elif args.command == "show":
            show_job(storage_manager, args)
        elif args.command == "export":
            export_jobs(storage_manager, args)
        elif args.command == "test":
            test_scrape(storage_manager, args)
        elif args.command == "clean":
            clean_jobs(storage_manager, args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def list_jobs(storage_manager, args):
    """List jobs with optional filtering"""
    status_filter = JobStatus(args.status) if args.status else None
    jobs = storage_manager.list_jobs(status=status_filter, limit=args.limit)
    
    if not jobs:
        print("No jobs found.")
        return
    
    print(f"{'Job ID':<15} {'Status':<12} {'URL':<50} {'Contacts':<10} {'Created'}")
    print("-" * 100)
    
    for job in jobs:
        created_str = job.created_at.strftime("%Y-%m-%d %H:%M")
        url_short = job.input_url[:47] + "..." if len(job.input_url) > 50 else job.input_url
        print(f"{job.job_id:<15} {job.status.value:<12} {url_short:<50} {job.total_contacts:<10} {created_str}")

def show_job(storage_manager, args):
    """Show detailed job information"""
    job_result = storage_manager.load_job_result(args.job_id)
    
    if not job_result:
        print(f"Job {args.job_id} not found.", file=sys.stderr)
        sys.exit(1)
    
    if args.format == "json":
        print(json.dumps(job_result.dict(), indent=2, default=str))
    elif args.format == "csv":
        csv_data = job_result.to_csv_data()
        if csv_data:
            import csv
            import io
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=csv_data[0].keys())
            writer.writeheader()
            writer.writerows(csv_data)
            print(output.getvalue())
        else:
            print("No contact data available for CSV export.")
    else:  # summary format
        summary = storage_manager._generate_text_summary(job_result)
        print(summary)

def export_jobs(storage_manager, args):
    """Export jobs to Excel"""
    try:
        output_file = storage_manager.export_jobs_to_excel(args.job_ids, args.output)
        print(f"Jobs exported to: {output_file}")
    except ImportError:
        print("Error: pandas and openpyxl are required for Excel export.", file=sys.stderr)
        print("Install with: pip install pandas openpyxl", file=sys.stderr)
        sys.exit(1)

def test_scrape(storage_manager, args):
    """Test scraping a URL and save the result"""
    from src.tools_simple import SimpleWebScraper
    from src.adapters.simple_local_adapter import SimpleLocalAdapter
    
    print(f"Testing scrape of: {args.url}")
    
    scraper = SimpleWebScraper()
    result = scraper.scrape_contact_details(args.url)
    
    # Save the result
    adapter = SimpleLocalAdapter(storage_manager.storage_dir)
    job_id = await_sync(adapter.push_data(result, input_url=args.url))
    
    print(f"Test completed. Job ID: {job_id}")
    print(f"Contacts found: {len(result.get('contacts', []))}")
    
    if result.get('error'):
        print(f"Error: {result['error']}")

def clean_jobs(storage_manager, args):
    """Clean old jobs"""
    count = storage_manager.cleanup_old_jobs(args.days)
    print(f"Cleaned up {count} jobs older than {args.days} days.")

def await_sync(awaitable):
    """Helper to run async function in sync context"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(awaitable)

if __name__ == "__main__":
    main()
