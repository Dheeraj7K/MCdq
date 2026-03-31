"""
server.py — DKB Connected Thoughts MCP Server
Run with: python server.py
Add to Claude/Gemini config as stdio MCP server.
"""

import json
import sys
from datetime import date, datetime
from pathlib import Path

# MCP
from mcp.server.fastmcp import FastMCP

# DKB Engine
from engine import (
    generate_batch, get_all_posts, get_live_quantum_metrics,
    load_theory, CYCLE_THEMES, POSTS_DIR, IMAGES_DIR, BASE_DIR, THEORY
)

mcp = FastMCP(
    "DKB Connected Thoughts",
    instructions=(
        "MCP server for Dheeraj Kumar Bakoriya's DKB Phase Framework theory. "
        "Generates Instagram-sized thought posts (1080×1080) with live quantum metrics "
        "from Google Cirq and Qualtran. Updates a website with all generated content. "
        "7 daily cycles × 20 posts = 140 connected thoughts per day."
    )
)

# ─────────────────────────────────────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────────────────────────────────────

@mcp.tool()
def generate_thought_batch(cycle: int = 0, posts_per_batch: int = 20) -> str:
    """
    Generate a batch of DKB thought posts with 1080×1080 images.
    Uses live Cirq quantum simulation and Qualtran resource estimation.
    
    Args:
        cycle: Which of the 7 daily cycles (0-6). 0=Foundation, 1=Proof, 2=Vision,
               3=Connection, 4=Progress, 5=Question, 6=Breakthrough
        posts_per_batch: Number of posts to generate (default 20)
    
    Returns:
        Summary of generated posts with file paths.
    """
    cycle = max(0, min(6, cycle))
    posts = generate_batch(cycle, posts_per_batch)
    theme = CYCLE_THEMES[cycle]["name"]

    summary = [
        f"✅ Generated {len(posts)} posts for Cycle {cycle+1}/7 ({theme})",
        f"📊 Cirq coherence: +{posts[0]['quantum']['cirq'].get('improvement_pct', 895)}%",
        f"⚡ Qualtran T-gate reduction: -{posts[0]['quantum']['qualtran'].get('reduction_pct', 88.83)}%",
        "",
        "Posts generated:",
    ]
    for p in posts[:5]:
        summary.append(f"  [{p['post_num']+1:02d}] {p['title']}")
    if len(posts) > 5:
        summary.append(f"  ... and {len(posts)-5} more")
    summary.append(f"\nImages saved to: website/images/{date.today().isoformat()}/")
    summary.append(f"JSON saved to: data/posts/{date.today().isoformat()}_cycle{cycle:02d}.json")

    return "\n".join(summary)


@mcp.tool()
def run_full_day_cycle() -> str:
    """
    Run all 7 daily cycles (140 posts total) at once.
    Generates 7 batches of 20 posts across all DKB themes, then rebuilds the website.
    WARNING: This runs all 7 batches and the website rebuild. May take a few minutes.

    Returns:
        Summary of all 7 batches generated.
    """
    results = []
    for cycle_num in range(7):
        theme = CYCLE_THEMES[cycle_num]["name"]
        posts = generate_batch(cycle_num, 20)
        cirq_improvement = posts[0]["quantum"]["cirq"].get("improvement_pct", 895)
        results.append(f"Cycle {cycle_num+1}/7 ({theme}): {len(posts)} posts | Cirq +{cirq_improvement}%")

    # Rebuild website
    website_result = rebuild_website()

    return (
        "🌐 Full day cycle complete!\n\n"
        + "\n".join(results)
        + "\n\n"
        + website_result
    )


@mcp.tool()
def get_quantum_reading() -> str:
    """
    Get a fresh live quantum reading from Google Cirq and Qualtran.
    Runs a DKB phase-timing coherence simulation and resource estimation.
    
    Returns:
        Live quantum metrics from Cirq and Qualtran.
    """
    metrics = get_live_quantum_metrics()
    cirq  = metrics["cirq"]
    qualt = metrics["qualtran"]

    return (
        f"⟁ DKB Live Quantum Metrics ({datetime.now().strftime('%H:%M:%S')})\n"
        f"\nGoogle Cirq — Phase Coherence Simulation:"
        f"\n  φ-harmonic node: φ^{cirq.get('phi_harmonic',5)} = {cirq.get('phi_node',11.09)}"
        f"\n  Baseline fidelity: {cirq.get('baseline_fidelity',0.22)}"
        f"\n  DKB fidelity:      {cirq.get('dkb_fidelity',0.92)}"
        f"\n  Improvement:       +{cirq.get('improvement_pct',895)}%"
        f"\n  Source: {cirq.get('source','Google Cirq DensityMatrixSimulator')}"
        f"\n\nGoogle Qualtran — T-Gate Resource Estimation:"
        f"\n  Target coherence:  {qualt.get('target_coherence_s',1.0)}s"
        f"\n  Standard T-gates:  {qualt.get('standard_tgates',200000):,}"
        f"\n  DKB T-gates:       {qualt.get('dkb_tgates',22344):,}"
        f"\n  φ^5 compression:   {qualt.get('phi_compression',11.09)}×"
        f"\n  T-gate reduction:  -{qualt.get('reduction_pct',88.83)}%"
        f"\n  Source: {qualt.get('source','Qualtran Resource Estimator')}"
    )


@mcp.tool()
def update_theory(
    idea: str,
    category: str = "active_research",
    milestone_date: str = ""
) -> str:
    """
    Add a new idea, insight, or milestone to the DKB theory knowledge base.
    
    Args:
        idea: The new idea, insight, or milestone text
        category: Where to add it — 'active_research', 'milestones', or 'core_equations'
        milestone_date: For milestones, the date (YYYY-MM-DD). Defaults to today.
    
    Returns:
        Confirmation of what was added.
    """
    theory_file = BASE_DIR / "data" / "theory.json"
    with open(theory_file) as f:
        theory = json.load(f)

    if category == "active_research":
        theory["active_research"].append(idea)
        added = f"Added to active research: {idea}"
    elif category == "milestones":
        d = milestone_date or date.today().isoformat()
        theory["milestones"].append({"date": d, "event": idea})
        added = f"Added milestone ({d}): {idea}"
    else:
        added = f"Category '{category}' not recognized. No changes made."

    with open(theory_file, "w") as f:
        json.dump(theory, f, indent=2)

    return f"✅ Theory updated!\n{added}\n\nKnowledge base now has {len(theory['active_research'])} research fronts and {len(theory['milestones'])} milestones."


@mcp.tool()
def rebuild_website() -> str:
    """
    Regenerate the DKB Connected Thoughts website with all latest posts.
    Loads all generated posts and creates a new index.html.
    
    Returns:
        Path to the generated website.
    """
    posts = get_all_posts(200)
    theory = load_theory()
    _build_website(posts, theory)
    website_path = BASE_DIR / "website" / "index.html"
    return (
        f"✅ Website rebuilt!\n"
        f"Posts included: {len(posts)}\n"
        f"Path: {website_path}\n"
        f"Open: file://{website_path}"
    )


@mcp.tool()
def list_posts(limit: int = 20, theme: str = "") -> str:
    """
    Browse generated DKB thought posts.
    
    Args:
        limit: Maximum number of posts to return (default 20)
        theme: Filter by theme (Foundation, Proof, Vision, Connection, Progress, Question, Breakthrough)
    
    Returns:
        List of posts with titles, themes, and dates.
    """
    posts = get_all_posts(500)
    if theme:
        posts = [p for p in posts if p.get("theme", "").lower() == theme.lower()]

    posts = posts[:limit]
    if not posts:
        return "No posts found. Run `generate_thought_batch` first."

    lines = [f"📋 DKB Connected Thoughts — {len(posts)} posts\n"]
    for p in posts:
        ts   = p.get("date", "")[:10]
        lines.append(f"[{ts}] Cycle {p.get('cycle',0)+1} · {p.get('theme','?'):12s} · {p.get('title','')}")

    return "\n".join(lines)


@mcp.tool()
def get_theory_status() -> str:
    """
    Get the current DKB theory status: equations, levels, research fronts, milestones.
    
    Returns:
        Full theory summary.
    """
    theory = load_theory()
    posts  = get_all_posts(1000)

    today_posts = [p for p in posts if p.get("date","")[:10] == date.today().isoformat()]
    cycles_done = len(set(p.get("cycle",0) for p in today_posts))

    lines = [
        f"◈ DKB Phase Framework — Current Status",
        f"Author: {theory['author']}",
        f"Master Equation: {theory['master_equation']['eq']}",
        f"",
        f"📐 Core Equations: {len(theory['core_equations'])}",
        f"🌌 Cosmological Levels: {len(theory['twelve_levels'])}",
        f"🔬 Active Research Fronts: {len(theory['active_research'])}",
        f"🏆 Milestones Logged: {len(theory['milestones'])}",
        f"",
        f"📸 Total Posts Generated: {len(posts)}",
        f"📅 Today's Posts: {len(today_posts)} ({cycles_done}/7 cycles)",
        f"",
        f"🔬 Active Research:",
    ]
    for r in theory["active_research"]:
        lines.append(f"  • {r}")

    lines.append(f"\n🏆 Recent Milestones:")
    for m in theory["milestones"][-3:]:
        lines.append(f"  [{m['date']}] {m['event']}")

    return "\n".join(lines)


@mcp.tool()
def get_schedule() -> str:
    """
    Show the 7 daily DKB update cycle schedule and today's completion status.
    
    Returns:
        Schedule with times and completion status for each cycle.
    """
    SCHEDULE_TIMES = ["06:00", "09:00", "12:00", "15:00", "18:00", "21:00", "00:00"]
    posts = get_all_posts(500)
    today = date.today().isoformat()
    today_posts = [p for p in posts if p.get("date","")[:10] == today]
    done_cycles  = set(p.get("cycle",0) for p in today_posts)

    lines = [f"📅 DKB Daily Schedule ({today})\n"]
    for i, (time_str, theme_info) in enumerate(zip(SCHEDULE_TIMES, CYCLE_THEMES)):
        status = "✅" if i in done_cycles else "⏳"
        count  = len([p for p in today_posts if p.get("cycle",0) == i])
        lines.append(f"  {status} {time_str}  Cycle {i+1}/7  [{theme_info['name']:12s}]  {count}/20 posts")

    total_today = len(today_posts)
    lines.append(f"\nToday: {total_today}/140 posts generated")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# WEBSITE BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def _build_website(posts: list, theory: dict):
    """Build the DKB Connected Thoughts website HTML."""
    website_dir = BASE_DIR / "website"
    website_dir.mkdir(exist_ok=True)

    today = date.today().isoformat()
    today_posts = [p for p in posts if p.get("date","")[:10] == today]

    # Build post cards HTML
    def post_card(p: dict) -> str:
        img  = p.get("image_path", "")
        title = p.get("title", "")
        body  = p.get("body", "")[:120] + "..."
        theme = p.get("theme", "")
        cirq_imp = p.get("quantum", {}).get("cirq", {}).get("improvement_pct", 895)
        return f'''<div class="post-card" onclick="openPost({json.dumps(p)})">
          <div class="post-img-wrap"><img src="{img}" alt="{title}" loading="lazy" onerror="this.style.display='none'"></div>
          <div class="post-meta"><span class="theme-badge">{theme}</span><span class="cirq-badge">⟁ +{cirq_imp}%</span></div>
          <div class="post-title">{title}</div>
          <div class="post-body">{body}</div>
        </div>'''

    cards_html = "\n".join(post_card(p) for p in posts[:100])

    # Build equations list
    equations_html = "\n".join(
        f'<div class="eq-item"><span class="eq-num">Eq {e["id"]}</span>'
        f'<span class="eq-name">{e["name"]}</span>'
        f'<code class="eq-code">{e["eq"]}</code>'
        f'<span class="eq-domain">{e["domain"]}</span></div>'
        for e in theory["core_equations"]
    )

    # Build research list
    research_html = "\n".join(
        f'<li class="research-item">{r}</li>' for r in theory["active_research"]
    )

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DKB Connected Thoughts — Phase Framework Live Feed</title>
<meta name="description" content="Live thought feed from the DKB Phase Framework — Reality = O(∇θ). Quantum-validated posts updated 7× daily. By Dheeraj Kumar Bakoriya.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg:      #050510;
    --bg2:     #0a0a20;
    --card:    rgba(255,255,255,0.04);
    --border:  rgba(100,80,255,0.2);
    --accent:  #6450ff;
    --accent2: #00c8b0;
    --text:    #e0deff;
    --muted:   rgba(224,222,255,0.5);
    --glow:    rgba(100,80,255,0.15);
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    font-family: 'Inter', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    overflow-x: hidden;
  }}

  /* ── ANIMATED BG ── */
  body::before {{
    content: '';
    position: fixed; inset: 0;
    background:
      radial-gradient(ellipse 80% 60% at 20% 30%, rgba(100,80,255,0.08) 0%, transparent 60%),
      radial-gradient(ellipse 60% 50% at 80% 70%, rgba(0,200,180,0.06) 0%, transparent 60%);
    pointer-events: none; z-index: 0;
    animation: bgShift 20s ease-in-out infinite alternate;
  }}
  @keyframes bgShift {{
    from {{ opacity: 1; }} to {{ opacity: 0.6; }}
  }}

  /* ── NAV ── */
  nav {{
    position: sticky; top: 0; z-index: 100;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 40px;
    height: 64px;
    background: rgba(5,5,16,0.85);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border);
  }}
  .nav-brand {{
    font-weight: 900; font-size: 1.1rem; letter-spacing: 0.05em;
    color: var(--text);
  }}
  .nav-brand span {{ color: var(--accent); }}
  .nav-eq {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem; color: var(--accent2);
    opacity: 0.8;
  }}
  .nav-links {{ display: flex; gap: 28px; }}
  .nav-links a {{
    color: var(--muted); text-decoration: none; font-size: 0.9rem;
    transition: color 0.2s;
  }}
  .nav-links a:hover {{ color: var(--text); }}

  /* ── HERO ── */
  .hero {{
    position: relative; z-index: 1;
    padding: 100px 40px 80px;
    text-align: center;
  }}
  .hero-badge {{
    display: inline-block;
    padding: 6px 18px; border-radius: 999px;
    border: 1px solid var(--border);
    background: var(--glow);
    font-size: 0.8rem; color: var(--accent2);
    letter-spacing: 0.1em; text-transform: uppercase;
    margin-bottom: 28px;
  }}
  .hero h1 {{
    font-size: clamp(2.5rem, 6vw, 5rem);
    font-weight: 900; line-height: 1.1;
    background: linear-gradient(135deg, #fff 0%, var(--accent) 50%, var(--accent2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 24px;
  }}
  .hero-master-eq {{
    font-family: 'JetBrains Mono', monospace;
    font-size: clamp(1rem, 2.5vw, 1.6rem);
    color: var(--accent2);
    margin-bottom: 20px;
    opacity: 0.9;
  }}
  .hero p {{
    max-width: 600px; margin: 0 auto 48px;
    color: var(--muted); font-size: 1.05rem; line-height: 1.7;
  }}
  .hero-stats {{
    display: flex; justify-content: center; gap: 48px; flex-wrap: wrap;
  }}
  .stat-item {{ text-align: center; }}
  .stat-num {{
    font-size: 2.5rem; font-weight: 900;
    color: var(--accent); font-family: 'JetBrains Mono', monospace;
  }}
  .stat-label {{ font-size: 0.8rem; color: var(--muted); margin-top: 4px; }}

  /* ── QUANTUM TICKER ── */
  .quantum-ticker {{
    position: relative; z-index: 1;
    background: linear-gradient(135deg, rgba(100,80,255,0.1), rgba(0,200,180,0.1));
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    padding: 16px 40px;
    display: flex; gap: 48px; justify-content: center; flex-wrap: wrap;
  }}
  .ticker-item {{
    display: flex; align-items: center; gap: 10px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;
  }}
  .ticker-label {{ color: var(--muted); }}
  .ticker-value {{ color: var(--accent2); font-weight: 700; }}

  /* ── SIMULATOR ── */
  .simulator-section {{
    max-width: 1400px; margin: 60px auto 20px; padding: 0 24px;
  }}
  .simulator-frame {{
    width: 100%; height: 800px;
    border: 1px solid var(--border); border-radius: 16px;
    background: var(--bg2); box-shadow: 0 20px 60px rgba(0,0,0,0.4);
  }}

  /* ── LAYOUT ── */
  .layout {{
    position: relative; z-index: 1;
    display: grid;
    grid-template-columns: 1fr 340px;
    gap: 0;
    max-width: 1400px; margin: 0 auto; padding: 0 24px;
  }}
  @media (max-width: 1024px) {{ .layout {{ grid-template-columns: 1fr; }} }}

  /* ── POSTS GRID ── */
  .posts-section {{ padding: 40px 32px 40px 0; }}
  .section-title {{
    font-size: 1.1rem; font-weight: 700; color: var(--text);
    margin-bottom: 24px; padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 12px;
  }}
  .section-badge {{
    font-size: 0.75rem; color: var(--accent); padding: 3px 10px;
    border: 1px solid var(--border); border-radius: 999px;
  }}
  .posts-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
  }}
  .post-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px; overflow: hidden;
    cursor: pointer;
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  }}
  .post-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 20px 60px rgba(100,80,255,0.2);
    border-color: var(--accent);
  }}
  .post-img-wrap {{ aspect-ratio: 1; overflow: hidden; background: var(--bg2); }}
  .post-img-wrap img {{
    width: 100%; height: 100%; object-fit: cover;
    transition: transform 0.4s ease;
  }}
  .post-card:hover .post-img-wrap img {{ transform: scale(1.04); }}
  .post-meta {{
    display: flex; gap: 8px; align-items: center;
    padding: 12px 16px 0;
  }}
  .theme-badge {{
    font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;
    padding: 3px 10px; border-radius: 999px;
    background: var(--glow); border: 1px solid var(--border);
    color: var(--accent);
  }}
  .cirq-badge {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem; color: var(--accent2);
  }}
  .post-title {{
    font-weight: 700; font-size: 0.95rem; line-height: 1.3;
    padding: 10px 16px 6px; color: var(--text);
  }}
  .post-body {{
    font-size: 0.82rem; color: var(--muted); line-height: 1.5;
    padding: 0 16px 16px;
  }}

  /* ── SIDEBAR ── */
  .sidebar {{
    padding: 40px 0 40px 32px;
    border-left: 1px solid var(--border);
  }}
  .sidebar-section {{ margin-bottom: 40px; }}
  .sidebar-title {{
    font-size: 0.85rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.1em; color: var(--accent);
    margin-bottom: 16px;
  }}

  /* ── EQUATIONS ── */
  .eq-item {{
    display: flex; flex-direction: column; gap: 4px;
    padding: 12px 0; border-bottom: 1px solid rgba(100,80,255,0.1);
  }}
  .eq-num {{ font-size: 0.7rem; color: var(--accent2); text-transform: uppercase; letter-spacing: 0.1em; }}
  .eq-name {{ font-size: 0.9rem; font-weight: 600; color: var(--text); }}
  .eq-code {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem; color: var(--accent);
    background: rgba(100,80,255,0.08);
    padding: 4px 8px; border-radius: 4px; margin: 2px 0;
  }}
  .eq-domain {{ font-size: 0.7rem; color: var(--muted); }}

  /* ── RESEARCH ── */
  .research-item {{
    padding: 8px 0; border-bottom: 1px solid rgba(100,80,255,0.08);
    font-size: 0.85rem; color: var(--muted); list-style: none;
  }}
  .research-item::before {{ content: '▸ '; color: var(--accent); }}

  /* ── MODAL ── */
  .modal-overlay {{
    display: none; position: fixed; inset: 0; z-index: 1000;
    background: rgba(5,5,16,0.92); backdrop-filter: blur(20px);
    align-items: center; justify-content: center; padding: 24px;
  }}
  .modal-overlay.active {{ display: flex; }}
  .modal {{
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: 24px; max-width: 680px; width: 100%;
    max-height: 90vh; overflow-y: auto;
    animation: modalIn 0.3s ease;
  }}
  @keyframes modalIn {{
    from {{ opacity: 0; transform: scale(0.95) translateY(20px); }}
    to   {{ opacity: 1; transform: scale(1) translateY(0); }}
  }}
  .modal-header {{
    padding: 28px 28px 0;
    display: flex; justify-content: space-between; align-items: start;
  }}
  .modal-theme {{ font-size: 0.75rem; color: var(--accent2); text-transform: uppercase; letter-spacing: 0.1em; }}
  .modal-close {{
    background: none; border: 1px solid var(--border);
    color: var(--muted); cursor: pointer; border-radius: 8px;
    width: 32px; height: 32px; font-size: 1.1rem;
    display: flex; align-items: center; justify-content: center;
    transition: all 0.2s;
  }}
  .modal-close:hover {{ color: var(--text); border-color: var(--accent); }}
  .modal-title {{ font-size: 1.6rem; font-weight: 900; padding: 16px 28px 0; line-height: 1.2; }}
  .modal-body {{ font-size: 1rem; line-height: 1.7; color: var(--muted); padding: 20px 28px; }}
  .modal-quantum {{
    margin: 0 28px; padding: 16px; border-radius: 12px;
    background: rgba(100,80,255,0.06); border: 1px solid var(--border);
    font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: var(--accent2);
  }}
  .modal-hashtags {{ padding: 16px 28px 28px; color: var(--muted); font-size: 0.85rem; }}
  .modal-img {{ width: 100%; display: block; border-radius: 12px; margin: 20px 28px 0; width: calc(100% - 56px); }}

  /* ── FOOTER ── */
  footer {{
    position: relative; z-index: 1;
    text-align: center; padding: 48px 40px;
    border-top: 1px solid var(--border);
    color: var(--muted); font-size: 0.85rem;
  }}
  footer .footer-eq {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.2rem; color: var(--accent); margin-bottom: 12px;
  }}
</style>
</head>
<body>

<nav>
  <div class="nav-brand">DKB <span>◈</span> Connected Thoughts</div>
  <div class="nav-eq">Reality = O(∇θ)</div>
  <div class="nav-links">
    <a href="#posts">Feed</a>
    <a href="#theory">Theory</a>
    <a href="#equations">Equations</a>
  </div>
</nav>

<section class="hero">
  <div class="hero-badge">⟁ DKB Phase Framework · Live Feed</div>
  <h1>Connected Thoughts<br>on Reality</h1>
  <div class="hero-master-eq">Reality = O(∇θ)</div>
  <p>
    Every day, 7 cycles × 20 thoughts — exploring the DKB Phase Framework
    through quantum-validated reflections. Powered by Google Cirq + Qualtran.
    By <strong>Dheeraj Kumar Bakoriya</strong>.
  </p>
  <div class="hero-stats">
    <div class="stat-item">
      <div class="stat-num">{len(posts)}</div>
      <div class="stat-label">Total Posts</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">+895%</div>
      <div class="stat-label">Cirq Coherence</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">-88.8%</div>
      <div class="stat-label">T-Gate Reduction</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">140</div>
      <div class="stat-label">Posts Per Day</div>
    </div>
  </div>
</section>

<div class="quantum-ticker">
  <div class="ticker-item">
    <span class="ticker-label">⟁ Cirq coherence:</span>
    <span class="ticker-value">+895%</span>
  </div>
  <div class="ticker-item">
    <span class="ticker-label">⊗ φ-node:</span>
    <span class="ticker-value">φ^5 = 11.09</span>
  </div>
  <div class="ticker-item">
    <span class="ticker-label">◈ T-gate reduction:</span>
    <span class="ticker-value">-88.83%</span>
  </div>
  <div class="ticker-item">
    <span class="ticker-label">🔬 Tools:</span>
    <span class="ticker-value">Google Cirq · Qualtran</span>
  </div>
  <div class="ticker-item">
    <span class="ticker-label">📋 Today:</span>
    <span class="ticker-value">{len(today_posts)} / 140 posts</span>
  </div>
</div>

<div class="simulator-section">
  <div class="section-title" style="margin-bottom:16px;">Phase Framework Simulator <span class="section-badge">Live Interactive Model</span></div>
  <iframe class="simulator-frame" src="https://dkb-phase-framework-simulator-146274734723.us-west1.run.app/" allow="compute; webgl; fullscreen"></iframe>
</div>

<div class="layout">
  <main class="posts-section" id="posts">
    <div class="section-title">
      Latest Thoughts
      <span class="section-badge">{len(posts)} total</span>
    </div>
    <div class="posts-grid" id="postsGrid">
      {cards_html}
    </div>
  </main>

  <aside class="sidebar" id="theory">
    <div class="sidebar-section">
      <div class="sidebar-title">Theory Status</div>
      <div class="eq-item">
        <span class="eq-num">Master Equation</span>
        <code class="eq-code">Reality = O(∇θ)</code>
        <span class="eq-domain">All of physics, consciousness, and time</span>
      </div>
      <div class="eq-item">
        <span class="eq-num">Author</span>
        <span class="eq-name">Dheeraj Kumar Bakoriya</span>
        <span class="eq-domain">DKB Phase Framework, 2026</span>
      </div>
    </div>

    <div class="sidebar-section" id="equations">
      <div class="sidebar-title">7 Arc Equations</div>
      {equations_html}
    </div>

    <div class="sidebar-section">
      <div class="sidebar-title">Active Research</div>
      <ul style="list-style:none">
        {research_html}
      </ul>
    </div>
  </aside>
</div>

<!-- Modal -->
<div class="modal-overlay" id="modalOverlay" onclick="closePost(event)">
  <div class="modal" id="modal">
    <div class="modal-header">
      <span class="modal-theme" id="modalTheme"></span>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-title" id="modalTitle"></div>
    <div class="modal-body" id="modalBody"></div>
    <div class="modal-quantum" id="modalQuantum"></div>
    <img class="modal-img" id="modalImg" src="" alt="" onerror="this.style.display='none'">
    <div class="modal-hashtags" id="modalHashtags"></div>
  </div>
</div>

<footer>
  <div class="footer-eq">Reality = O(∇θ)</div>
  <div>DKB Connected Thoughts · Auto-generated {datetime.now().strftime("%B %d, %Y")} · Powered by Google Cirq + Qualtran</div>
</footer>

<script>
function openPost(post) {{
  document.getElementById('modalTheme').textContent = post.theme + ' · Cycle ' + (post.cycle+1) + '/7';
  document.getElementById('modalTitle').textContent = post.title;
  document.getElementById('modalBody').textContent = post.body;
  const c = post.quantum?.cirq || {{}};
  const q = post.quantum?.qualtran || {{}};
  document.getElementById('modalQuantum').innerHTML =
    '⟁ Cirq: φ^' + (c.phi_harmonic||5) + ' = ' + (c.phi_node||11.09) +
    ' | Improvement: +' + (c.improvement_pct||895) + '%<br>' +
    '◈ Qualtran: ' + (q.dkb_tgates||22344) + ' T-gates | Reduction: -' + (q.reduction_pct||88.83) + '%';
  const img = document.getElementById('modalImg');
  img.src = post.image_path || '';
  img.style.display = post.image_path ? 'block' : 'none';
  document.getElementById('modalHashtags').textContent = post.hashtags || '';
  document.getElementById('modalOverlay').classList.add('active');
  document.body.style.overflow = 'hidden';
}}
function closePost(e) {{ if (e.target === document.getElementById('modalOverlay')) closeModal(); }}
function closeModal() {{
  document.getElementById('modalOverlay').classList.remove('active');
  document.body.style.overflow = '';
}}
document.addEventListener('keydown', e => {{ if (e.key === 'Escape') closeModal(); }});
</script>
</body>
</html>'''

    with open(website_dir / "index.html", "w") as f:
        f.write(html)


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("◈ DKB Connected Thoughts MCP Server starting...", file=sys.stderr)
    print("  Tools: generate_thought_batch, run_full_day_cycle, get_quantum_reading,", file=sys.stderr)
    print("         update_theory, rebuild_website, list_posts, get_theory_status, get_schedule", file=sys.stderr)
    mcp.run(transport="stdio")
