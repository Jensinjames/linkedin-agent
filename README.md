# 🚀 Advanced LinkedIn Scraping Agent

A powerful, production-ready LinkedIn scraping agent built with LlamaIndex, featuring advanced anti-detection measures, data persistence, and intelligent AI orchestration.

## ✨ Key Features

### 🎯 **Enhanced LinkedIn Scraping**
- **Direct Profile & Company Scraping**: Extract comprehensive data from LinkedIn profiles and company pages
- **Anti-Detection Technology**: Advanced browser fingerprint randomization, human-like behavior simulation
- **Playwright Integration**: Headless browser automation with stealth capabilities
- **Rate Limiting**: Intelligent request throttling to avoid detection
- **Proxy Support**: Optional proxy rotation for enhanced anonymity

### 🛡️ **Advanced Anti-Detection Features**
- **Randomized User Agents**: Multiple realistic browser fingerprints
- **Dynamic Viewports**: Random screen resolutions (1200-1920x800-1080)
- **Human Behavior Simulation**: Random scrolling, mouse movements, delays
- **Browser Stealth**: Advanced fingerprint masking and webdriver property removal
- **Rate Limiting**: Configurable requests per minute with intelligent waiting
- **Proxy Support**: Optional proxy rotation for IP anonymity

### 🤖 **AI-Powered Agent**
- **LlamaIndex Integration**: Intelligent task orchestration with ReAct agent pattern
- **Multiple Tools**: Enhanced toolset for various LinkedIn scraping scenarios
- **Natural Language Interface**: Chat with the agent using plain English
- **Legacy Support**: Backward compatibility with existing Apify integrations

### 🔧 **Enterprise-Ready**
- **Error Handling**: Robust error management with graceful degradation
- **Configuration Management**: Environment-based configuration with validation
- **Logging**: Comprehensive logging for monitoring and debugging
- **Scalability**: Designed for both individual and bulk scraping operations

## 🛠️ Available Tools

### Core LinkedIn Scraping
1. **`run_linkedin_crawler`** - Enhanced LinkedIn scraping with anti-detection features
2. **`call_contact_details_scraper`** - External Apify actor integration (legacy)
3. **`summarize_contact_information`** - AI-powered data summarization

## 🎯 Sample Use Cases

### Basic Profile Scraping
```
"Scrape the LinkedIn profile https://linkedin.com/in/example-person"
```

### Company Intelligence
```
"Scrape company information from https://linkedin.com/company/example-company"
```

### Advanced Features
```
"Scrape LinkedIn profiles using anti-detection measures"
"Extract data from multiple LinkedIn company pages"
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API Key
- Apify Token (optional, for external integrations)

### Installation

1. **Clone and Install Dependencies**
   ```bash
   git clone <repository-url>
   cd linkedin-agent
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Required Environment Variables**
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   APIFY_TOKEN=your_apify_token_here  # Optional
   ```

### 💻 Usage

#### Local Development
```bash
# Run with input file
python -m src.cli input.json

# Or with stdin
echo '{"query": "Scrape https://linkedin.com/company/openai"}' | python -m src.cli
```

#### Apify Platform
```bash
# Build and run on Apify
apify run
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for LLM functionality |
| `APIFY_TOKEN` | No | - | Apify token for external integrations |
| `LINKEDIN_HEADLESS` | No | `true` | Run browser in headless mode |
| `LINKEDIN_TIMEOUT` | No | `30000` | Browser timeout in milliseconds |
| `LINKEDIN_DELAY` | No | `3` | Delay between requests in seconds |
| `MAX_REQUESTS_PER_MINUTE` | No | `10` | Rate limiting parameter |
| `DEFAULT_MODEL_NAME` | No | `gpt-4o` | OpenAI model to use |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### Anti-Detection Configuration

The enhanced LinkedIn crawler includes sophisticated anti-detection measures:

- **Randomized User Agents**: Rotates between realistic browser fingerprints
- **Dynamic Viewports**: Random screen resolutions for each session
- **Human Behavior Simulation**: Random scrolling, mouse movements, and realistic delays
- **Browser Stealth Mode**: Removes webdriver properties and mocks browser objects
- **Rate Limiting**: Configurable requests per minute with intelligent waiting
- **Proxy Support**: Optional proxy rotation for enhanced anonymity

## 🔍 Technical Architecture

### Core Components

1. **LinkedInCrawler Class**: Main scraping engine with Playwright integration
2. **Anti-Detection System**: Advanced fingerprint randomization and behavior simulation
3. **Rate Limiter**: Intelligent request throttling to avoid detection
4. **Data Extraction**: Specialized extractors for profiles and company pages
5. **Error Handling**: Comprehensive error management with graceful degradation

### Data Extraction Capabilities

#### Profile Data
- Name, headline, location
- About section and summary
- Experience and education (expandable)
- Skills and endorsements
- Contact information

#### Company Data
- Company name and tagline
- Industry and company size
- Headquarters and website
- Description and specialties
- Founded year and key metrics

## ⚠️ Important Notes

### Legal Compliance
- **Respect robots.txt**: Always check LinkedIn's robots.txt
- **Rate Limiting**: Built-in rate limiting to avoid overwhelming servers
- **Terms of Service**: Ensure compliance with LinkedIn's Terms of Service
- **Data Privacy**: Handle scraped data responsibly

### Best Practices
- Start with small batches to test configuration
- Use proxy rotation for large-scale operations
- Monitor success rates and adjust rate limiting
- Regularly update anti-detection measures

### Troubleshooting

#### Common Issues
1. **Browser Installation**: Run `playwright install chromium`
2. **Memory Issues**: Reduce concurrent operations
3. **Rate Limiting**: Decrease `requests_per_minute` if getting blocked
4. **Timeout Errors**: Increase `LINKEDIN_TIMEOUT` value

#### Debug Mode
```bash
# Enable verbose logging
LOG_LEVEL=DEBUG python -m src.cli input.json

# Run in non-headless mode for debugging
LINKEDIN_HEADLESS=false python -m src.cli input.json
```

### Summarization

Set `summarizeResults` to `true` in the Actor input to generate a short summary of the scraped contact details using the configured OpenAI model. When the flag is omitted or `false`, only raw results are stored.

### CSV input

You can also provide LinkedIn URLs via a CSV file. Set `inputType` to `csv` and specify `inputPath` pointing to the file. Each row should contain a single URL. The crawler will read the file, build the query string, and retry failed requests up to three times with exponential backoff.

### Sample queries:

- Find contact details for `apify.com` and provide raw results.
- Find contact details for `apify.com` and summarize them.

## Before you start

To run this template locally or on the Apify platform, you need:

- An [Apify account](https://console.apify.com/) and an [Apify API token](https://docs.apify.com/platform/integrations/api#api-token).
- An [OpenAI](https://openai.com/) account and API key.

## Monetization

This template uses the [Pay Per Event](https://docs.apify.com/platform/actors/publishing/monetize#pay-per-event-pricing-model) (PPE) monetization model, which provides flexible pricing based on defined events.

To charge users, define events in JSON format and save them on the Apify platform. Here is an example of [pay_per_event.json](.actor/pay_per_event.json) with the `task-completed` event:

```json
[
    {
        "task-completed": {
            "eventTitle": "Task completed",
            "eventDescription": "Cost per query answered.",
            "eventPriceUsd": 0.1
        }
    }
]
```

In the Actor, trigger the event with:

```javascript
await Actor.charge({ eventName: 'task-completed' });
```

This approach allows you to programmatically charge users directly from your Actor, covering the costs of execution and related services, such as LLM input/output tokens.

## Resources

Useful resources to help you get started:

- [Apify Actors](https://docs.apify.com/platform/actors)
- [LlamaIndex agent](https://docs.llamaindex.ai/en/stable/use_cases/agents/)
- [Building a basic agent](https://docs.llamaindex.ai/en/stable/understanding/agent/)
- [What are AI agents?](https://blog.apify.com/what-are-ai-agents/)
- [11 AI agent use cases on Apify](https://blog.apify.com/ai-agent-use-cases/)

Additional material:
[Web Scraping Data for Generative AI](https://www.youtube.com/watch?v=8uvHH-ocSes)


## Getting started

For complete information [see this article](https://docs.apify.com/platform/actors/development#build-actor-at-apify-console). In short, you will:

1. Build the Actor
2. Run the Actor

## Request flow

For a step-by-step overview of how a query is processed by this project, see [docs/REQUEST_FLOW.md](docs/REQUEST_FLOW.md).

## Pull the Actor for local development

If you would like to develop locally, you can pull the existing Actor from Apify console using Apify CLI:

1. Install `apify-cli`

    **Using Homebrew**

    ```bash
    brew install apify-cli
    ```

    **Using NPM**

    ```bash
    npm -g install apify-cli
    ```

2. Pull the Actor by its unique `<ActorId>`, which is one of the following:

    - unique name of the Actor to pull (e.g. "apify/hello-world")
    - or ID of the Actor to pull (e.g. "E2jjCZBezvAZnX8Rb")

    You can find both by clicking on the Actor title at the top of the page, which will open a modal containing both Actor unique name and Actor ID.

    This command will copy the Actor into the current directory on your local machine.


    ```bash
    apify pull <ActorId>
    ```

## Local setup

Use the Makefile to install dependencies and run the project locally:

```bash
make install  # set up a virtual environment and install requirements
make run      # execute the CLI with input.json
# For CSV input (input.json must specify inputType="csv" and inputPath)
python -m src.cli input.json
```

## Run with Docker

Build the Docker image and execute the crawler locally:

```bash
docker build -t linkedin-agent .
docker run --rm -v $(pwd)/input.json:/usr/src/app/input.json linkedin-agent \
  python -m src.cli input.json
# Using CSV input
# docker run --rm -v $(pwd)/input.json:/usr/src/app/input.json \
#   -v $(pwd)/input.csv:/usr/src/app/input.csv linkedin-agent \
#   python -m src.cli input.json
```

## Documentation reference

To learn more about Apify and Actors, take a look at the following resources:

- [Apify SDK for JavaScript documentation](https://docs.apify.com/sdk/js)
- [Apify SDK for Python documentation](https://docs.apify.com/sdk/python)
- [Apify Platform documentation](https://docs.apify.com/platform)
- [Join our developer community on Discord](https://discord.com/invite/jyEM2PRvMU)
## License

This project is licensed under the [MIT License](LICENSE).
