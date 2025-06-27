# Webhook/CLI Trigger for n8n & Zapier

Use `apify_wrapper.py` to integrate with automation workflows.

## Synchronous (wait for result)

```bash
python apify_wrapper.py --input input.json
```
Output is printed to stdout.

## Asynchronous (callback via webhook)

```bash
python apify_wrapper.py --input input.json --webhook <your_n8n_or_zapier_webhook_url>
```
Results are POSTed to the webhook URL as JSON.

## REST API

To expose as a REST endpoint, run:

```bash
python apify_rest_server.py
# then POST input JSON to http://localhost:8000/run
```

---

This enables full compatibility with n8n, Zapier, and custom backend automation flows.