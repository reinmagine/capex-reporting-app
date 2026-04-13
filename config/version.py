"""
Version tracking for CAPEX Reporting Tool
Update VERSION with each release
"""

# Current application version - UPDATE THIS WITH EACH RELEASE
VERSION = "1.0.2"

# GitHub repository information
GITHUB_REPO = "ludreinsalvador/capex-reporting-app"
GITHUB_OWNER = "ludreinsalvador"
GITHUB_REPO_NAME = "capex-reporting-app"

# Auto-update endpoint - points to version.json in main branch
VERSION_CHECK_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/version.json"

# Release information
RELEASE_INFO = {
    "version": VERSION,
    "github_repo": GITHUB_REPO,
    "check_url": VERSION_CHECK_URL,
}
