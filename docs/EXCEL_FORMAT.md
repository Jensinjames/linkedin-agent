# Excel Format Guide for LinkedIn Agent

This guide explains the proper format for Excel files used with the LinkedIn Agent batch processing system.

## Overview

The LinkedIn Agent supports Excel files (`.xlsx` and `.xls`) for batch processing of LinkedIn profiles and company
pages. Excel files must follow a specific structure with designated tabs and column names.

## File Structure

### Required Tabs

Excel files must contain one or both of the following tabs:

1. **Company_Profiles** - For LinkedIn company page scraping
2. **Individual_Profiles** - For LinkedIn individual profile scraping

### Tab Naming Conventions

- Tab names are case-sensitive and must match exactly: `Company_Profiles` and `Individual_Profiles`
- Use underscores, not spaces or hyphens
- No special characters or extra spaces

## Column Specifications

### Company_Profiles Tab

| Column Name              | Required  | Description                     | Example                                       |
|--------------------------|-----------|---------------------------------|-----------------------------------------------|
| **LinkedIn Company URL** | ✅ **Yes** | Valid LinkedIn company page URL | `https://www.linkedin.com/company/apifytech/` |
| Company Name             | No        | Company name for reference      | `Apify`                                       |
| Industry                 | No        | Industry classification         | `Technology`                                  |
| Location                 | No        | Company location                | `Prague, Czech Republic`                      |
| Notes                    | No        | Additional notes or comments    | `Web scraping platform`                       |

### Individual_Profiles Tab

| Column Name              | Required  | Description                  | Example                                  |
|--------------------------|-----------|------------------------------|------------------------------------------|
| **LinkedIn Profile URL** | ✅ **Yes** | Valid LinkedIn profile URL   | `https://www.linkedin.com/in/johnsmith/` |
| Full Name                | No        | Person's full name           | `John Smith`                             |
| Company                  | No        | Current company              | `Apify`                                  |
| Position                 | No        | Current job title            | `Software Engineer`                      |
| Location                 | No        | Person's location            | `Prague, Czech Republic`                 |
| Notes                    | No        | Additional notes or comments | `Backend specialist`                     |

## URL Format Requirements

### Company URL Format

Valid LinkedIn company URLs must follow this pattern:

```
https://www.linkedin.com/company/[company-name]/
```

**Valid Examples:**

- `https://www.linkedin.com/company/apifytech/`
- `https://www.linkedin.com/company/openai/`
- `https://www.linkedin.com/company/meta/`

**Invalid Examples:**

- `linkedin.com/company/apifytech/` (missing https://www.)
- `https://linkedin.com/company/apifytech/` (missing www.)
- `https://www.linkedin.com/company/` (missing company name)

### Individual Profile URL Format

Valid LinkedIn profile URLs must follow this pattern:

```
https://www.linkedin.com/in/[profile-name]/
```

**Valid Examples:**

- `https://www.linkedin.com/in/johnsmith/`
- `https://www.linkedin.com/in/jane-doe-123/`
- `https://www.linkedin.com/in/mike-johnson-456789/`

**Invalid Examples:**

- `linkedin.com/in/johnsmith/` (missing https://www.)
- `https://linkedin.com/in/johnsmith/` (missing www.)
- `https://www.linkedin.com/in/` (missing profile name)

## Data Validation Guidelines

### Required Data

- At least one LinkedIn URL column must be present and populated
- URLs must be valid LinkedIn URLs (see format requirements above)
- Empty rows are automatically skipped

### Optional Data

- All other columns are optional and can be left empty
- Optional columns help organize and categorize your data
- Notes column is useful for tracking processing status

### Data Types

- URLs: Text strings (must be valid LinkedIn URLs)
- Names/Text: Text strings (any characters allowed)
- Notes: Text strings (any characters allowed)

## File Templates

### Using the Template Files

1. **Main Template** (`examples/linkedin_template.xlsx`)
    - Clean template with proper headers
    - Empty rows for user input
    - Use this as a starting point for new projects

2. **Sample Input** (`examples/sample_input.xlsx`)
    - Contains example data showing proper format
    - Demonstrates both company and individual profiles
    - Use this to understand the expected format

### Creating Your Own Files

1. Start with the template file
2. Add your LinkedIn URLs to the appropriate tab
3. Fill in optional columns as needed
4. Save as `.xlsx` format (recommended) or `.xls` (legacy support)

## Common Issues and Troubleshooting

### Format Errors

**Problem:** "Invalid LinkedIn URL format"

- **Solution:** Ensure URLs start with `https://www.linkedin.com/`
- **Check:** URLs end with `/` and contain proper company/profile names

**Problem:** "Tab not found"

- **Solution:** Verify tab names are exactly `Company_Profiles` and `Individual_Profiles`
- **Check:** No extra spaces, correct capitalization, use underscores

**Problem:** "Required column missing"

- **Solution:** Ensure `LinkedIn Company URL` or `LinkedIn Profile URL` columns exist
- **Check:** Column names match exactly (case-sensitive)

### Data Issues

**Problem:** "No data found"

- **Solution:** Check that URLs are in the correct columns
- **Check:** Remove completely empty rows
- **Verify:** At least one valid URL exists in the file

**Problem:** "Batch processing failed"

- **Solution:** Verify file is saved as `.xlsx` or `.xls`
- **Check:** File is not corrupted or password-protected
- **Ensure:** File size is reasonable (< 100MB recommended)

## Best Practices

### File Organization

- Use descriptive file names (e.g., `tech_companies_2024.xlsx`)
- Keep files under 100MB for optimal processing
- Organize data by project or campaign

### Data Quality

- Validate URLs before processing
- Remove duplicate URLs
- Use consistent formatting in optional columns
- Add meaningful notes for tracking

### Batch Processing

- Test with small batches first (< 100 URLs)
- Monitor processing logs for errors
- Keep backup copies of original files
- Use the sample file to verify format before large batches

## Integration with Batch Processing

The Excel files are processed by the enhanced `batch_scrape_excel_enhanced.sh` script, which:

1. **Multi-tab Processing**: Automatically detects and processes both Company_Profiles and Individual_Profiles tabs
2. **URL Validation**: Validates LinkedIn URL formats before processing
3. **Error Reporting**: Provides detailed error messages for invalid URLs and format issues
4. **Batch Splitting**: Splits large datasets into manageable batches for processing
5. **Progress Tracking**: Tracks progress and allows resuming interrupted processing
6. **Excel Output**: Outputs results in Excel format with detailed profile information

### Usage

```bash
# Process Excel file with multiple tabs
./src/batch_scrape_excel_enhanced.sh input.xlsx input.json batch_logs

# Process single CSV file (legacy mode)
./src/batch_scrape_excel_enhanced.sh input.csv input.json batch_logs
```

### Enhanced Features

- **Automatic Tab Detection**: Automatically processes Company_Profiles and Individual_Profiles tabs
- **URL Validation**: Validates LinkedIn URLs before processing to prevent errors
- **Detailed Logging**: Comprehensive logging of processing steps and errors
- **Error Recovery**: Retry mechanism for failed batches
- **Progress Reporting**: Shows progress and allows resuming interrupted jobs

For technical details on batch processing, refer to the batch processing documentation.

## Support

If you encounter issues with Excel file formatting:

1. Check this guide for common solutions
2. Verify your file against the sample template
3. Test with a small subset of your data first
4. Review the batch processing logs for specific error messages