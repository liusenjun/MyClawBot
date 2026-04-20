# AGENTS.md — Elias Character Session

## On Startup
1. Read `SOUL.md`
2. Read `IDENTITY.md`
3. Check `memory/` for recent context if it exists

## Communication
To reach the co-narrator:
sessions_send(label="main", message="...")

## Image Generation (via MCP)
mcporter call "https://polyu-storyworld.tail9683c.ts.net/mcp.flux2_single_image_edit" \
  reference_image_filename=6092g_ref.png \
  prompt="<scene description>" \
  output_filename_prefix=<name>_<scene>

## Memory
Write session notes to `memory/YYYY-MM-DD.md`.
