# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python library for crawling academic papers from PubMed using the NCBI Entrez API. The main module is `ArtiCraw.py`, which provides functions to search for articles by keyword and year range, and fetch detailed article metadata including abstracts, authors, titles, DOIs, and publication information.

## Environment Setup

The project uses a Python virtual environment located at `paper-craw/`:

```bash
# Activate the virtual environment
source paper-craw/bin/activate

# The venv uses Python 3.14 and includes biopython 1.87
```

## Core Architecture

### Main Module: ArtiCraw.py

The library is organized around two primary workflows:

1. **Search workflow**: `search_articles()` → returns list of PMIDs
2. **Fetch workflow**: Individual fetch functions retrieve specific article data by PMID

**Key functions:**

- `set_email(email, api_key)` - Must be called first to configure Entrez credentials
- `search_articles(keyword, year_range=None, retmax=10)` - Search PubMed and return PMIDs
  - `year_range` can be: `None` (current year), single int (specific year), or tuple `(start_year, end_year)`
  - Uses `_normalize_year_range()` helper for year validation
- `get_abstract(pmid)` - Fetch abstract text for a PMID
- `get_authors(pmid)` - Fetch author information
- `get_title(pmid)` - Fetch article title

### Alternative Implementation: ArtiCraw copy.py

This file contains an extended version with additional features:

- `fetch_article(pmid, author=None, publication_year=None)` - Returns structured article data with optional validation
- `_extract_article_data()` - Parses XML response into structured dict with PMID, Title, Abstract, Journal, PublicationDate, Authors, DOI
- `fetch_abstract(pmid)` - Same as main module
- Includes placeholder for impact factor filtering (not yet implemented)

**Note**: The "copy" version appears to be a more feature-complete implementation. Consider consolidating these files.

## Development Notes

- All functions interact with NCBI's Entrez API via the `Bio.Entrez` module from biopython
- API calls require proper email and API key configuration via `set_email()`
- The library uses synchronous API calls (no async support currently)
- Year range validation is centralized in `_normalize_year_range()` helper
- Chinese comments indicate this may be developed by Chinese-speaking developers

## Testing

The `test.py` file imports the module but contains no test cases yet. When adding tests, ensure you:

- Mock Entrez API calls to avoid hitting rate limits
- Test year range normalization edge cases
- Validate PMID list parsing and article data extraction
