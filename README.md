# DKB Connected Thoughts — MCP Server

Automated thought-publishing system for the **DKB Phase Framework** (Reality = O(∇θ)).

Generates 7 batches × 20 posts per day = **140 Instagram-sized (1080×1080) thought posts daily**, each carrying live quantum simulation data from **Google Cirq** and **Google Qualtran**.

---

## Quick Start

```bash
# 1. Activate the virtual environment
source .venv/bin/activate

# 2. Generate one batch immediately (cycle 1 = Proof theme)
python scheduler.py --cycle 1

# 3. Run all 7 cycles at once (full day simulation)
python scheduler.py --all

# 4. Start the daily auto-scheduler (runs in background)
python scheduler.py

# 5. View schedule status
python scheduler.py --status

# 6. Start the MCP server (for Claude/Gemini integration)
python server.py
```

---

## File Structure

```
mcdp/
├── server.py          ← MCP server (8 tools)
├── engine.py          ← Content + Image + Quantum engine
├── scheduler.py       ← 7×daily auto-runner
├── mcp_config.json    ← Add to Claude Desktop or Gemini config
├── .venv/             ← Python venv with all deps
├── data/
│   ├── theory.json    ← DKB theory knowledge base
│   ├── posts/         ← Generated post JSON (by date/cycle)
│   └── schedule.json  ← Scheduler state
└── website/
    ├── index.html     ← Auto-generated live website
    └── images/        ← 1080×1080 post images (by date)
```

---

## MCP Tools

| Tool | Description |
|------|-------------|
| `generate_thought_batch` | Generate 20 posts for one cycle (with Cirq + Qualtran data) |
| `run_full_day_cycle` | Run all 7 cycles (140 posts) + rebuild website |
| `get_quantum_reading` | Live Cirq coherence sim + Qualtran resource estimate |
| `update_theory` | Add new DKB ideas/milestones to knowledge base |
| `rebuild_website` | Regenerate website from all posts |
| `list_posts` | Browse generated posts with filters |
| `get_theory_status` | Current theory summary + metrics |
| `get_schedule` | Today's cycle status |

---

## Daily Schedule (7 Cycles)

| Time  | Cycle | Theme        | Focus |
|-------|-------|--------------|-------|
| 06:00 | 1     | Foundation   | Core equations and the phase field |
| 09:00 | 2     | Proof        | Quantum coherence results (Cirq/Qualtran) |
| 12:00 | 3     | Vision       | Where DKB is heading |
| 15:00 | 4     | Connection   | Physics, consciousness, mathematics |
| 18:00 | 5     | Progress     | What was built today |
| 21:00 | 6     | Question     | Open problems and frontiers |
| 00:00 | 7     | Breakthrough | Key insights and moments of clarity |

---

## Quantum Integration (Google Tools)

### Google Cirq (coherence simulation)
- Runs `DensityMatrixSimulator` with `PhaseDampingChannel`
- Measures `|dm[0,1]|` — off-diagonal coherence (what phase damping actually suppresses)
- **γ_std = 0.8** (standard, rapid decoherence)
- **γ_dkb = 1/(10 × φⁿ)** — reduced at harmonic node
- Result: ~100-900% improvement depending on φ-harmonic used

### Google Qualtran (resource estimation)
- Estimates T-gate count for fault-tolerant computation
- DKB protocol uses φ⁵ ≈ 11.09× compression factor
- **~90% T-gate reduction** vs standard surface code protocol

---

## Add to Claude Desktop

Copy this into `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dkb-connected-thoughts": {
      "command": "/Users/dbakoriya/mcdp/.venv/bin/python3",
      "args": ["/Users/dbakoriya/mcdp/server.py"],
      "env": {
        "MPLCONFIGDIR": "/tmp/mpl",
        "PYTHONPATH": "/Users/dbakoriya/mcdp"
      }
    }
  }
}
```

---

## View the Website

```bash
open website/index.html
```
Or deploy to Vercel: `vercel --prod website/`
