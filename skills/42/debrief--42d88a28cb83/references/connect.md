# connect - Connect a source

**Enter when:** the user asks to connect a notes, chat or document source, or an expected source cannot be read.

Apply [task context](task-context.md). Source setup can run independently of a customer record. Follow [source setup](source-setup.md) for permitted tools, credentials, connectivity checks and export alternatives.

## Method

1. Identify the source and the material the user wants to read. Inspect the host's actual available tools before recommending setup.
2. If the source already works, use a narrowly scoped requested read. Do not install another connector.
3. If setup is needed, verify current provider and host documentation, explain the required access, and make only authorized configuration changes. Never put credentials into prompts or customer records.
4. Test the selected source and distinguish configuration from successful retrieval. If access is blocked, report the specific limitation and an available file or paste alternative.
5. If the user also wants to update a customer record, continue with [ingest](ingest.md) after selecting that record. Otherwise stop after the requested setup or read.

## Checkpoint

Return what is connected, what read was verified, any access gap, and how to request the next pull. Do not claim an integration works from configuration alone or write customer records during setup.

## Principles

- Existing source tools first; configuration only when needed.
- Minimum requested read, no ambient synchronization.
- Credentials stay in supported secret storage.
- Record updates require their own review and confirmation.
