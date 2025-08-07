# Log Whisperer Usage Guide

## Quick Start

### 1. Install the Package
```bash
pip install log-whisperer
```

### 2. Configure Your LLM Provider
```bash
log-whisperer configure
```

**Example configuration for OpenAI:**
```
Select LLM provider: openai
Model name: gpt-3.5-turbo
Api Key: sk-your-openai-key-here
Temperature (0.0-1.0): 0.7
Max Tokens: 2000
Top P (0.0-1.0): [Enter to skip]
```

### 3. Analyze Your Logs
```bash
log-whisperer chat --log-file /path/to/your/logfile.log --save conversation.json
```

## Example Session

```
$ log-whisperer chat --log-file application.log --save analysis.json

✓ Loaded log file: application.log
Log file size: 2847 characters
✓ Initialized openai with model gpt-3.5-turbo

┌─ Agent ──────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  🔍 Welcome to Log Whisperer!                                               │
│                                                                              │
│  I'm ready to help you analyze your log file: application.log               │
│                                                                              │
│  You can ask me questions like:                                             │
│  • "What errors do you see in this log?"                                    │
│  • "Summarize the main events"                                              │
│  • "Are there any patterns or anomalies?"                                   │
│  • "What happened around timestamp X?"                                      │
│                                                                              │
│  Type 'quit', 'exit', or press Ctrl+C to end the session.                  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

You: What errors do you see in this log?

Analyzing...

┌─ Agent ──────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  Based on my analysis of the log file, I found several types of errors:     │
│                                                                              │
│  ## Database Connection Errors                                              │
│  • **Timeline**: 10:30:45 - 10:30:52                                        │
│  • **Issue**: Connection timeouts to the database                           │
│  • **Impact**: Failed after 3 retry attempts, caused 500 errors            │
│                                                                              │
│  ## Security Issues                                                         │
│  • **Timeline**: 16:45:22 - 16:45:29                                        │
│  • **Issue**: Multiple failed authentication attempts from IP 192.168.1.100 │
│  • **Action**: IP was automatically blocked                                 │
│                                                                              │
│  ## Key Recommendations                                                     │
│  1. Monitor database connection stability                                   │
│  2. Review security logs for the blocked IP                                 │
│  3. Database was restored at 11:45:12, but investigate root cause          │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

You: What was the overall system health?

Analyzing...

┌─ Agent ──────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  ## Overall System Health Assessment                                        │
│                                                                              │
│  **Uptime**: 99.7% (as reported in daily statistics)                       │
│                                                                              │
│  ### Positive Indicators                                                    │
│  • Successful application startup (5 seconds)                              │
│  • Normal API response times (45-234ms)                                    │
│  • Automated recovery (database connection restored)                       │
│  • Successful daily backup operations                                      │
│  • Active security monitoring (blocked suspicious IP)                      │
│                                                                              │
│  ### Areas of Concern                                                       │
│  • Brief database outage (~15 minutes)                                     │
│  • High memory usage spike (85% heap)                                      │
│  • Security attack attempts                                                │
│                                                                              │
│  **Overall Assessment**: Good system health with minor incidents handled   │
│  appropriately by automated systems.                                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

You: quit

Goodbye! Your conversation has been saved.
```

## Commands Reference

### `log-whisperer configure`
Interactive setup wizard for LLM providers.

**Supported Providers:**
- **OpenAI**: GPT-3.5, GPT-4 models
- **Anthropic**: Claude 3 models  
- **Google**: Gemini Pro models
- **Cohere**: Command models
- **Hugging Face**: Various open-source models
- **Ollama**: Local models (no API key needed)

### `log-whisperer chat`
Start interactive log analysis session.

**Options:**
- `--log-file PATH`: Log file to analyze (required)
- `--save PATH`: Save conversation to JSON file (optional)

### `log-whisperer status`
Show current configuration.

### `log-whisperer reset`
Reset all configuration settings.

## Advanced Usage

### Environment Variables
Set API keys via environment variables:
```bash
export OPENAI_API_KEY="sk-your-key"
export ANTHROPIC_API_KEY="sk-ant-your-key"
export GOOGLE_API_KEY="your-google-key"
```

### Batch Installation with Provider
```bash
pip install log-whisperer[openai]     # For OpenAI
pip install log-whisperer[anthropic]  # For Anthropic
pip install log-whisperer[all]        # All providers
```

### Configuration File
Location: `~/.log-whisperer/config.yaml`

Example:
```yaml
provider:
  provider: openai
  model: gpt-3.5-turbo
  api_key: sk-your-key
  temperature: 0.7
  max_tokens: 2000
```

## Tips for Better Analysis

1. **Large Files**: Tool loads first 10,000 characters. For huge logs, consider splitting.

2. **Specific Questions**: Ask targeted questions like:
   - "Show me all ERROR level messages"
   - "What happened between 10:30 and 11:00?"
   - "Are there any performance issues?"

3. **Follow-up Questions**: Tool maintains conversation context, so ask follow-ups:
   - "Can you elaborate on that?"
   - "What caused those errors?"
   - "How can I fix this?"

4. **Save Sessions**: Use `--save` to resume analysis later:
   ```bash
   log-whisperer chat --log-file app.log --save session.json
   ```