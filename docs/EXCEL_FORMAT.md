# Excel Format Requirements for LinkedIn Agent

## Overview

The LinkedIn Agent supports batch processing of LinkedIn profiles and company pages using Excel files. This document describes the expected format and structure for Excel input files.

## File Structure

Excel files should contain separate tabs for different types of LinkedIn profiles:

- **Company_Profiles**: For LinkedIn company pages
- **Individual_Profiles**: For LinkedIn personal profiles
- **Instructions**: Optional tab with field descriptions (for reference)

## Required Fields

### Company Profiles Tab

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| LinkedIn URL | ✅ Yes | Full LinkedIn company URL | `https://www.linkedin.com/company/apifytech/` |
| Company Name | ❌ No | Company name for reference | `Apify Technologies` |
| Industry | ❌ No | Industry category | `Web Scraping & Automation` |
| Location | ❌ No | Company location | `Prague, Czech Republic` |
| Notes | ❌ No | Additional notes | `Priority contact` |

### Individual Profiles Tab

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| LinkedIn URL | ✅ Yes | Full LinkedIn profile URL | `https://www.linkedin.com/in/john-doe/` |
| Full Name | ❌ No | Person's name for reference | `John Doe` |
| Company | ❌ No | Current company | `Example Corp` |
| Position | ❌ No | Job title | `Software Engineer` |
| Location | ❌ No | Location | `San Francisco, CA` |
| Notes | ❌ No | Additional notes | `Follow up in Q2` |

## LinkedIn URL Format

### Valid Company URLs
- `https://www.linkedin.com/company/company-name/`
- `https://linkedin.com/company/company-name/`
- `https://www.linkedin.com/company/1234567/` (with company ID)

### Valid Individual Profile URLs
- `https://www.linkedin.com/in/profile-name/`
- `https://linkedin.com/in/profile-name/`
- `https://www.linkedin.com/profile/view?id=profile-name`

## Output Format

After processing, the system will extract the following information:

### For All Profiles
- Full Name
- Headline
- Company
- Location
- Connections
- About
- Experience
- Education
- Skills

## File Templates

### linkedin_template.xlsx
- Empty template with proper headers
- Example data structure
- Instructions tab with field descriptions
- Separate tabs for Company and Individual profiles

### sample_input.xlsx
- Sample file with realistic data
- Ready-to-use examples
- Demonstrates proper formatting
- Real LinkedIn URLs for testing

### linkedin_template.csv
- Simple CSV template for users who prefer CSV format
- Mixed company and individual profile URLs
- Ready to use with batch processing

## Usage with Batch Processing

To process Excel files with the batch script:

```bash
# Navigate to backend directory
cd backend

# Process Excel file (recommended)
./batch_scrape_excel.sh ../examples/sample_input.xlsx ../examples/input.json batch_logs

# Process CSV file (alternative)
./batch_scrape_excel.sh ../examples/linkedin_template.csv ../examples/input.json batch_logs
```

The script will:
1. **Excel Processing**: Read all sheets, extract LinkedIn URLs, combine into CSV
2. **CSV Conversion**: Convert Excel to CSV format (if needed)
3. **Batch Creation**: Split into batches (10,000 profiles per batch)
4. **URL Processing**: Process each batch of LinkedIn URLs
5. **Data Extraction**: Scrape profile information from LinkedIn
6. **Excel Output**: Convert results back to Excel format
7. **Final Merge**: Combine all results into a single output file

### Multi-Sheet Processing

The system automatically:
- Reads all sheets in the Excel file
- Skips the "Instructions" sheet
- Looks for "LinkedIn URL" columns (case-insensitive)
- Combines URLs from all sheets into a single processing queue
- Preserves the order: Company profiles first, then Individual profiles

## Processing Flow

1. **Excel Input**: Upload Excel file with LinkedIn URLs
2. **CSV Conversion**: System converts Excel to CSV format
3. **Batch Processing**: Split into manageable batches
4. **URL Extraction**: Extract LinkedIn URLs from first column
5. **Profile Scraping**: Scrape each LinkedIn profile
6. **Data Enrichment**: Extract profile information
7. **Excel Output**: Convert results back to Excel format

## Best Practices

### Data Preparation
- Ensure LinkedIn URLs are complete and valid
- Remove duplicate URLs before processing
- Use consistent URL formats (include https://)
- Keep optional fields for reference but don't rely on them

### File Organization
- Use descriptive sheet names (Company_Profiles, Individual_Profiles)
- Keep LinkedIn URLs in the first column of each sheet
- Limit to 10,000 URLs per file for optimal performance
- Use separate files for different campaigns or projects

### Quality Control
- Validate URLs before processing
- Check for broken or redirected LinkedIn pages
- Remove private profiles that may not be accessible
- Test with a small sample before processing large batches

## Error Handling

The system will handle various error scenarios:

- **Invalid URLs**: Logged and skipped
- **Private Profiles**: Logged with access restriction note
- **Network Issues**: Automatic retry with exponential backoff
- **Rate Limiting**: Automatic throttling to respect LinkedIn's limits

## Common Issues and Solutions

### Issue: "No LinkedIn URLs found"
**Solution**: Check that URLs are in the first column and properly formatted.

### Issue: "Empty results"
**Solution**: Verify that LinkedIn URLs are accessible and not private profiles.

### Issue: "Rate limiting errors"
**Solution**: Reduce batch size or add delays between requests.

## Technical Requirements

- **File Format**: .xlsx (Excel 2007+)
- **Maximum File Size**: 50MB recommended
- **Maximum Rows**: 100,000 per sheet
- **Required Libraries**: pandas, openpyxl, polars
- **Supported Platforms**: Linux, macOS, Windows (with WSL)

## Support

For additional support or questions:
1. Check the examples directory for template files
2. Review the batch processing logs for error details
3. Ensure all dependencies are installed correctly
4. Verify LinkedIn URLs are publicly accessible