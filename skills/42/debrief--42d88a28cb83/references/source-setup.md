# Source access for customer notes

Use this guide when `connect` needs a source and when `ingest` cannot reach requested material. Configure only the named source. FDEOps does not bundle source authentication or silently install integrations.

## Start with what is already available

Inspect the current host's tools. Name which requested source can be read and what remains unavailable. A server appearing in a configuration file is not proof that its credentials or scopes work.

For setup, use the source provider's current official documentation and the host's documented connector or MCP configuration. Do not invent package names, API methods, secret values or installation flags. Prefer an existing authenticated connector over adding a second one. Put credentials in the host's supported secret storage; never paste them into a customer record, prompt or report.

## Choose the source path

| Material | First check | If unavailable |
|---|---|---|
| Pasted notes or a local export | The user permits this content in the agent; identify the relevant file or text | Ask for the specific missing material, not an integration installation |
| Meeting notes, such as Granola | A notes tool can read the selected meeting and its source identifier | Use a permitted export or the provider's supported setup |
| Slack or another chat system | Read access to the specified thread or channel and date range | Ask the user or workspace owner to resolve access; a copied thread is an alternative |
| Notion or another document system | Read access to the specified page and its linked content when required | Use a permitted document export or resolve the missing page access |

Test a configured source with the smallest requested read. Report setup, connectivity and successful retrieval separately. Do not widen access to an entire inbox or workspace just because one item is unavailable.

## Keep setup separate from record updates

Configuring or testing a source does not require a customer record. Reading requested material does not authorize applying it to one.

For a review-only request, use the permitted supplied or fetched text and return a sourced draft. For staging or saving, select the intended customer record first, then follow [ingest](ingest.md): stage → propose → review → explicit confirmation → apply. Source permissions do not authorize a record update, and the FDEOps CLI itself makes no network calls.

Short notes can use [debrief](debrief.md) directly. Large files should be staged through the CLI when a customer record has been selected. Preserve source IDs and dates when available; absence of a source remains explicit.

FDEOps does not post messages, change source documents, background-sync channels or make recurring pulls through this path. Use the requested read scope only.
