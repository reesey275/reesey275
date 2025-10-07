# OpenAI Models Reference

This document provides comprehensive information about available OpenAI models, their token limits, and rate limits.

## Model Categories

### Chat Models

| Model | Token Limits | Request and Other Limits | Batch Queue Limits |
|-------|-------------|-------------------------|-------------------|
| gpt-3.5-turbo | 200,000 TPM | 500 RPM, 10,000 RPD | 2,000,000 TPD |
| gpt-3.5-turbo-0125 | 200,000 TPM | 500 RPM, 10,000 RPD | 2,000,000 TPD |
| gpt-3.5-turbo-1106 | 200,000 TPM | 500 RPM, 10,000 RPD | 2,000,000 TPD |
| gpt-3.5-turbo-16k | 200,000 TPM | 500 RPM, 10,000 RPD | 2,000,000 TPD |
| gpt-3.5-turbo-instruct | 90,000 TPM | 3,500 RPM | 200,000 TPD |
| gpt-3.5-turbo-instruct-0914 | 90,000 TPM | 3,500 RPM | 200,000 TPD |
| gpt-4 | 10,000 TPM | 500 RPM, 10,000 RPD | 100,000 TPD |
| gpt-4-0613 | 10,000 TPM | 500 RPM, 10,000 RPD | 100,000 TPD |

#### GPT-4 Turbo (Shared Limits)
- **Models**: gpt-4-turbo, gpt-4-turbo-2024-04-09, gpt-4-turbo-preview, gpt-4-0125-preview, gpt-4-1106-preview
- **Limits**: 30,000 TPM, 500 RPM, 90,000 TPD

#### GPT-4.1 Models
- **gpt-4.1** (gpt-4.1-2025-04-14): 30,000 TPM, 500 RPM, 900,000 TPD
- **gpt-4.1 (long context)**: 200,000 TPM, 100 RPM, 2,000,000 TPD
- **gpt-4.1-mini** (gpt-4.1-mini-2025-04-14): 200,000 TPM, 500 RPM, 2,000,000 TPD
- **gpt-4.1-mini (long context)**: 400,000 TPM, 200 RPM, 4,000,000 TPD
- **gpt-4.1-nano** (gpt-4.1-nano-2025-04-14): 200,000 TPM, 500 RPM, 2,000,000 TPD
- **gpt-4.1-nano (long context)**: 400,000 TPM, 200 RPM, 4,000,000 TPD

#### GPT-4o Models (Shared Limits)
- **Models**: gpt-4o-2024-05-13, gpt-4o-2024-08-06, gpt-4o-2024-11-20,
  gpt-4o-audio-preview, gpt-4o-audio-preview-2024-10-01,
  gpt-4o-audio-preview-2024-12-17
- **Limits**: 30,000 TPM, 500 RPM, 90,000 TPD
- **gpt-4o-audio-preview-2025-06-03**: 250,000 TPM, 3,000 RPM

#### GPT-4o Mini Models
- **Models**: gpt-4o-mini-2024-07-18, gpt-4o-mini-audio-preview, gpt-4o-mini-audio-preview-2024-12-17
- **Limits**: 200,000 TPM, 500 RPM, 10,000 RPD, 2,000,000 TPD

#### GPT-4o Search and Transcribe Models
- **gpt-4o-mini-search-preview**: 6,000 TPM, 100 RPM
- **gpt-4o-mini-search-preview-2025-03-11**: 6,000 TPM, 100 RPM
- **gpt-4o-mini-transcribe**: 50,000 TPM, 500 RPM
- **gpt-4o-search-preview**: 6,000 TPM, 100 RPM
- **gpt-4o-search-preview-2025-03-11**: 6,000 TPM, 100 RPM
- **gpt-4o-transcribe**: 10,000 TPM, 500 RPM

### GPT-5 Models

| Model | Token Limits | Request and Other Limits | Batch Queue Limits |
|-------|-------------|-------------------------|-------------------|
| gpt-5 (gpt-5-2025-08-07) | 500,000 TPM | 500 RPM | 1,500,000 TPD |
| gpt-5-chat-latest | 30,000 TPM | 500 RPM | 900,000 TPD |
| **gpt-5-codex** | **500,000 TPM** | **500 RPM** | **900,000 TPD** |
| gpt-5-mini | 500,000 TPM | 500 RPM | 5,000,000 TPD |
| gpt-5-mini-2025-08-07 | 500,000 TPM | 500 RPM | 5,000,000 TPD |
| gpt-5-nano | 200,000 TPM | 500 RPM | 2,000,000 TPD |
| gpt-5-nano-2025-08-07 | 200,000 TPM | 500 RPM | 2,000,000 TPD |
| gpt-5-pro | 30,000 TPM | 500 RPM | 90,000 TPD |
| gpt-5-pro-2025-10-06 | 30,000 TPM | 500 RPM | 90,000 TPD |

### Audio Models
- **gpt-audio**: 250,000 TPM, 3,000 RPM
- **gpt-audio-2025-08-28**: 250,000 TPM, 3,000 RPM
- **gpt-audio-mini**: 250,000 TPM, 3,000 RPM
- **gpt-audio-mini-2025-10-06**: 250,000 TPM, 3,000 RPM

### Text Models
- **babbage-002**: 250,000 TPM, 3,000 RPM
- **chatgpt-4o-latest**: 500,000 TPM, 200 RPM
- **davinci-002**: 250,000 TPM, 3,000 RPM

### O-Series Models
- **o1**: 30,000 TPM, 500 RPM, 90,000 TPD
- **o1-2024-12-17**: 30,000 TPM, 500 RPM, 90,000 TPD
- **o1-mini**: 200,000 TPM, 500 RPM, 2,000,000 TPD
- **o1-mini-2024-09-12**: 200,000 TPM, 500 RPM, 2,000,000 TPD
- **o1-pro** (o1-pro-2025-03-19): 30,000 TPM, 500 RPM, 90,000 TPD
- **o3** (o3-2025-04-16): 30,000 TPM, 500 RPM, 90,000 TPD
- **o3-mini** (o3-mini-2025-01-31): 200,000 TPM, 500 RPM, 2,000,000 TPD
- **o4-mini** (o4-mini-2025-04-16): 200,000 TPM, 500 RPM, 2,000,000 TPD

### Embedding Models
- **text-embedding-3-large**: 1,000,000 TPM, 3,000 RPM, 3,000,000 TPD
- **text-embedding-3-small**: 1,000,000 TPM, 3,000 RPM, 3,000,000 TPD
- **text-embedding-ada-002**: 1,000,000 TPM, 3,000 RPM, 3,000,000 TPD

### Realtime Models
- **gpt-4o-mini-realtime-preview** (gpt-4o-mini-realtime-preview-2024-12-17): 40,000 TPM, 200 RPM, 1,000 RPD
- **gpt-realtime** (Shared limits): 250,000 TPM, 3,000 RPM
  - gpt-realtime-2025-08-28
  - gpt-4o-realtime-preview
  - gpt-4o-realtime-preview-latest
  - gpt-4o-realtime-preview-2024-10-01
  - gpt-4o-realtime-preview-2024-12-17
  - gpt-4o-realtime-preview-2025-06-03
- **gpt-realtime-mini**: 250,000 TPM, 3,000 RPM
- **gpt-realtime-mini-2025-10-06**: 250,000 TPM, 3,000 RPM

### Moderation Models
- **omni-moderation-2024-09-26**: 10,000 TPM, 500 RPM, 10,000 RPD
- **omni-moderation-latest**: 10,000 TPM, 500 RPM, 10,000 RPD
- **text-moderation-latest**: 150,000 TPM, 1,000 RPM
- **text-moderation-stable**: 150,000 TPM, 1,000 RPM

### Image Models
- **dall-e-2**: 500 RPM, 5 images per minute
- **dall-e-3**: 500 RPM, 5 images per minute
- **gpt-image-1**: 100,000 TPM, 5 images per minute
- **gpt-image-1-mini**: 100,000 TPM, 5 images per minute

### Video Models
- **sora-2**: 2 RPM
- **sora-2-pro**: 1 RPM

### Text-to-Speech and Speech Models
- **gpt-4o-mini-tts**: 50,000 TPM, 500 RPM
- **tts-1**: 500 RPM
- **tts-1-1106**: 500 RPM
- **tts-1-hd**: 500 RPM
- **tts-1-hd-1106**: 500 RPM
- **whisper-1**: 500 RPM

### Fine-Tuning Models
#### Fine-Tuning Inference (shares limits with base model)
- **babbage-002**: 250,000 TPM, 3,000 RPM
- **davinci-002**: 250,000 TPM, 3,000 RPM
- **gpt-3.5-turbo-0125**: 200,000 TPM, 500 RPM
- **gpt-3.5-turbo-0613**: 200,000 TPM, 500 RPM
- **gpt-3.5-turbo-1106**: 200,000 TPM, 500 RPM
- **gpt-4-0613**: 10,000 TPM, 500 RPM
- **gpt-4o-2024-05-13**: 30,000 TPM, 500 RPM
- **gpt-4o-mini-2024-07-18**: 200,000 TPM, 500 RPM

#### Fine-tuning Training
- **Active/Queued Jobs**: 3 per model
- **Jobs per day**: 48 per model
- **Supported models**: babbage-002, davinci-002, gpt-3.5-turbo-0613

## Abbreviations
- **TPM**: Tokens Per Minute
- **RPM**: Requests Per Minute
- **RPD**: Requests Per Day
- **TPD**: Tokens Per Day

## Notes

### gpt-5-codex Model
The `gpt-5-codex` model appears to be a specialized model that may require
different API endpoints than standard chat completions. When using this model
with tools like OpenAI Codex CLI, it may not work with standard
`v1/chat/completions` endpoint and might require `v1/responses` or other
specialized endpoints.

### Model Compatibility
When integrating with GitHub Actions or CI/CD pipelines, consider using models
that are well-supported by standard endpoints:
- **Recommended for CI/CD**: gpt-4o-mini, gpt-4o, gpt-3.5-turbo
- **High performance options**: gpt-4o, gpt-5 (if accessible)
- **Cost-effective**: gpt-4o-mini, gpt-3.5-turbo

### Default Limits
All other models not explicitly listed default to: 250,000 TPM, 3,000 RPM
