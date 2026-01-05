"""
Adzuna Service - Integration with Adzuna Jobs API
"""
import os
import httpx
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()


class AdzunaService:
    """Service for fetching job listings from Adzuna API"""

    def __init__(self):
        self.app_id = os.getenv("ADZUNA_APP_ID")
        self.app_key = os.getenv("ADZUNA_APP_KEY")
        self.base_url = "https://api.adzuna.com/v1/api/jobs/us/search"

    async def search_jobs(
        self,
        query: Optional[str] = None,
        location: str = "United States",
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        results_per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Search for jobs using Adzuna API

        Args:
            query: Job title or keywords (optional)
            location: Location string (e.g., "Atlanta, GA")
            filters: Additional filters (salary, job type, etc.)
            page: Page number (default 1)
            results_per_page: Number of results per page (default 20)

        Returns:
            List of job dictionaries with match scores
        """
        if not self.app_id or not self.app_key:
            raise ValueError("Adzuna API credentials not configured")

        # Build URL manually with proper percent encoding (Adzuna rejects + encoding)
        # Must use %20 for spaces, not +
        # NOTE: Page number goes in URL path, NOT in query params
        query_parts = [
            f"app_id={self.app_id}",
            f"app_key={self.app_key}",
            f"results_per_page={results_per_page}"
        ]

        # Add query if provided (MUST be lowercase with %20 encoding)
        if query:
            # Adzuna requires lowercase and %20 for spaces
            encoded_query = quote(query.lower(), safe='')
            query_parts.append(f"what={encoded_query}")

        # Add location if provided
        if location:
            encoded_location = quote(location.lower(), safe='')
            query_parts.append(f"where={encoded_location}")

        # Add what_exclude if provided
        if filters and filters.get("what_exclude"):
            encoded_exclude = quote(filters["what_exclude"].lower(), safe='')
            query_parts.append(f"what_exclude={encoded_exclude}")

        # Add filters
        filters = filters or {}
        if filters.get("salary_min"):
            query_parts.append(f"salary_min={filters['salary_min']}")
        if filters.get("salary_max"):
            query_parts.append(f"salary_max={filters['salary_max']}")
        if filters.get("full_time"):
            query_parts.append("full_time=1")
        if filters.get("part_time"):
            query_parts.append("part_time=1")
        if filters.get("contract"):
            query_parts.append("contract=1")
        if filters.get("permanent"):
            query_parts.append("permanent=1")
        if filters.get("max_days_old"):
            query_parts.append(f"max_days_old={filters['max_days_old']}")
        if filters.get("sort_by"):
            query_parts.append(f"sort_by={filters['sort_by']}")

        # Build complete URL with query string
        # Page number is in the path (e.g., /search/1), not in query params
        url = f"{self.base_url}/{page}?{'&'.join(query_parts)}"

        # Set proper headers
        headers = {
            "Accept": "application/json",
            "User-Agent": "ResumeBuilder/1.0"
        }

        print(f"[ADZUNA] Making request to: {url}")

        # Make request with pre-built URL (don't use params dict to avoid + encoding)
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            print(f"[ADZUNA] Response status: {response.status_code}")

            if response.status_code != 200:
                print(f"[ADZUNA ERROR] Response body: {response.text[:500]}")

            response.raise_for_status()

        data = response.json()

        # Format results
        jobs = []
        for result in data.get("results", []):
            job = {
                "id": result.get("id"),
                "title": result.get("title"),
                "company": result.get("company", {}).get("display_name", "N/A"),
                "location": result.get("location", {}).get("display_name", "N/A"),
                "description": result.get("description", ""),
                "url": result.get("redirect_url"),
                "created": result.get("created"),
                "salary_min": result.get("salary_min"),
                "salary_max": result.get("salary_max"),
                "contract_type": result.get("contract_type"),
            }
            jobs.append(job)

        # Return both jobs and total count
        return {
            "jobs": jobs,
            "count": data.get("count", len(jobs))  # Adzuna API returns total count in "count" field
        }

    async def get_job_details(self, job_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific job

        Args:
            job_id: Adzuna job ID

        Returns:
            Job details dictionary
        """
        # Adzuna doesn't have a separate job details endpoint
        # The search results already include full details
        # This is a placeholder for future expansion
        return {}
