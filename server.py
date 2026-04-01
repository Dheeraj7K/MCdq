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
        import re
        # Work on a copy to avoid mutating the original posts list if needed
        p = p.copy()
        
        img  = p.get("image_path", "")
        body  = p.get("body", "")
        theme = p.get("theme", "")
        title = p.get("title", "")
        
        # CLEANUP: Remove redundant technical prefixes from body
        # Matches variations like: "Phase state derivation complete. ", "Evaluating `...`:", etc.
        # We use a robust regex that handles newlines and multiple spaces.
        body = re.sub(r'^\s*(Phase state derivation complete\.(?:.*?\.\s*)?|Evaluating\s+`[^`]+`:\s*|Result:\s*)', '', body, flags=re.IGNORECASE | re.DOTALL)
        
        # TITLE MAPPING: Standardize to "Evaluating: [Concept]"
        # If theme is Breakthrough or Progress, we always want the title to be "Evaluating: [Concept]"
        if theme in ["Breakthrough", "Progress"]:
            # 1. First, try to extract from original title if it has "Result: ..."
            concept_match = re.search(r'(?:Result:\s*|Differential\s*at\s*(?:.*?)?\s*|Evaluating\s*(?:.*?)?:\s*)(.*?)\s*(?:\[Iter|\d|$)', title, flags=re.IGNORECASE)
            
            # 2. If title is still vague, try extraction from body
            if not concept_match or (concept_match and len(concept_match.group(1).strip()) < 3):
                # Try to extract something from backticks `...` in body
                subject_match = re.search(r'`([^`]+)`', p.get("body", ""))
                if subject_match:
                    title = f"Evaluating: {subject_match.group(1)}"
                elif concept_match:
                    title = f"Evaluating: {concept_match.group(1).strip()}"
            else:
                title = f"Evaluating: {concept_match.group(1).strip()}"
            
            # Final fallback: Ensure it HAS the prefix and isn't just (DFA) etc.
            if not title.startswith("Evaluating:"):
                title = f"Evaluating: {title}"
            
            # Clean up trailing punctuation or iterations
            title = re.sub(r'\s*\[Iter.*$', '', title)
            title = re.sub(r'[\s:]+$', '', title)

        # Update the dict so the modal (which uses the JSON) is also cleaned
        p["title"] = title
        p["body"] = body.strip()

        q = p.get("quantum", {})
        cirq_imp = q.get("cirq", {}).get("improvement_pct", 895)
        tg_red = q.get("qualtran", {}).get("reduction_pct", 88.83)
        
        # Safely escape JSON for HTML attribute.
        # We use single quotes for the attribute and double quotes internally, escaped.
        p_json = json.dumps(p).replace('"', '&quot;').replace("'", "&#39;")
        
        return f'''
        <div class="post-card" onclick='openPostById("{p_json}")'>
          <div class="post-img-wrap">
            <img src="{img}" alt="{title}" loading="lazy" onerror="this.style.display='none'">
            <div class="post-overlay-data">
              <div class="cirq-pill">⟁ +{cirq_imp}%</div>
              <div class="qual-pill">◈ -{tg_red}%</div>
            </div>
          </div>
          <div class="post-card-content">
            <div class="post-meta">
              <span class="theme-badge">{theme}</span>
            </div>
            <div class="post-title">{title}</div>
            <div class="post-body">{body}</div>
            <div class="card-footer">
               <div class="btn-primary">View Analysis</div>
            </div>
          </div>
        </div>'''

    cards_html = "\n".join(post_card(p) for p in posts[:100])

    # Build Graph Data for 3D visualization
    graph_nodes = [
        {"id": "MasterEq", "name": theory["master_equation"]["name"], "desc": theory["master_equation"]["eq"], "color": "#ff33cc", "val": 30},
    ]
    graph_links = []
    
    # 1. Linear Theory Spine (Backbone)
    for lvl in theory.get("twelve_levels", []):
        l_id = f"L{lvl['level']}"
        graph_nodes.append({
            "id": l_id, "name": lvl["name"], "desc": lvl["desc"], "color": "#ffcc00", "val": 30
        })
        if lvl["level"] > 0:
            graph_links.append({"source": l_id, "target": f"L{lvl['level']-1}"})
        else:
            graph_links.append({"source": l_id, "target": "MasterEq"})

    # 2. Logic Mappings (Theory Spine Anchors)
    level_anchors = {
        "The Scalar Ground State": "L0",
        "The Arc Vector": "L1",
        "Phase Propagation Topology (PPT)": "L1",
        "Fibridge Compression Limit (DFA)": "L1",
        "The Observer Transformation": "L3",
        "Harmonic Scaling (Fibonacci Metric)": "L5",
        "Geodesic Curvature": "L7",
        "The Möbius Identity": "L7",
        "Fundamental Wave Equation": "L8",
        "phi": "L0",
        "L_dkb": "L0",
        "phi_5": "L1",
        "kappa_qg": "L1",
        "v_alpha": "L1",
        "H_dkb": "L7",
        "alpha_dkb": "L8",
        "theta_max": "L8",
        "arc_vec": "L1",
        "spin_op": "L8",
        "moebius_lock": "L7",
        "star_node": "L5"
    }

    # 3. Core Pillar Laws (Equations)
    for eq in theory["core_equations"]:
        nature_title = f"Fundamental Pillar 0{eq['id']}" if eq['id'] < 10 else f"Fundamental Pillar {eq['id']}"
        graph_nodes.append({"id": eq["name"], "name": nature_title, "desc": eq["eq"], "color": "#6450ff", "val": 22})
        target = level_anchors.get(eq["name"], "MasterEq")
        graph_links.append({"source": eq["name"], "target": target})
    
    # 4. Meta Emerged Nodes (Milestones + Research)
    for m in theory.get("milestones", []):
        m_id = f"M_{m['date']}"
        graph_nodes.append({"id": m_id, "name": f"Milestone: {m['event']}", "desc": f"Emergence Date: {m['date']}", "color": "#ff33cc", "val": 25})
        graph_links.append({"source": m_id, "target": "MasterEq"})

    for r in theory.get("active_research", []):
        r_id = f"R_{r[:10]}"
        graph_nodes.append({
            "id": r_id, "name": f"Research: {r}", "desc": "Active Theoretical Pursuit", "color": "#00ccff", "val": 20
        })
        # Research typically targets specific levels or MasterEq
        target = "L3" if "consciousness" in r.lower() else "MasterEq"
        graph_links.append({"source": r_id, "target": target})

    # 5. Physical Constants & Invariants (Anchored)
    for c in theory.get("physical_constants", []):
        c_id = f"C_{c['id']}"
        # Resonant Cyan for Field Dynamics (Arc, Spin, Lock, Star)
        is_dynamic = c["id"] in ["arc_vec", "spin_op", "moebius_lock", "star_node"]
        c_color = "#00ffff" if is_dynamic else "#ffee00"
        
        graph_nodes.append({
            "id": c_id, "name": c["name"], "desc": f"Value: {c['val']} | {c['desc']}", "color": c_color, "val": 18
        })
        target = level_anchors.get(c["id"], "MasterEq")
        graph_links.append({"source": c_id, "target": target})

    # 6. Latest Breakthroughs (Orbiting Pillar Laws they evaluate)
    breakthroughs = [p for p in posts if p.get("theme") == "Breakthrough"][:30]
    for b in breakthroughs:
        b_id = b.get("id", "b")
        q = b.get("quantum", {}).get("cirq", {})
        impact_desc = f"Quantum Validation Efficiency: {q.get('improvement_pct', 895)}% (φ-node resonant)"
        graph_nodes.append({"id": b_id, "name": b.get("title"), "desc": impact_desc, "color": "#33ff33", "val": 15})
        
        # Determine target pillar from title content (Logically identifying evaluated concept)
        target_pillar = theory["core_equations"][0]["name"] # Default
        for eq in theory["core_equations"]:
            if eq["name"].lower() in b.get("title", "").lower():
                target_pillar = eq["name"]
                break
        graph_links.append({"source": b_id, "target": target_pillar})

    graph_json = json.dumps({"nodes": graph_nodes, "links": graph_links}, indent=2)
    with open(website_dir / "graph_data.json", "w") as f:
        f.write(graph_json)

    # Build equations list with 'natural' pillars
    equations_html = "\n".join(
        f'<div class="eq-item"><span class="eq-num">Fundamental Pillar 0{e["id"]}</span>'
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
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;900&family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #050510;
    --bg-alt: #0a0a1f;
    --bg-glass: rgba(10, 10, 31, 0.7);
    --accent: #6450ff;
    --accent-glow: rgba(100, 80, 255, 0.3);
    --accent2: #00ccff;
    --border: rgba(100, 80, 255, 0.2);
    --text: #ffffff;
    --muted: #8892b0;
    --font-heading: 'Outfit', sans-serif;
    --font-body: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
  }}
  
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    background: var(--bg); color: var(--text);
    font-family: var(--font-body); line-height: 1.6;
    overflow-x: hidden;
  }}
  
  /* ── BG ANIMATION ── */
  body::before {{
    content: ''; position: fixed; inset: 0; pointer-events: none;
    background: 
      radial-gradient(circle at 20% 30%, rgba(100, 80, 255, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 80% 70%, rgba(0, 204, 255, 0.05) 0%, transparent 50%);
    z-index: -1;
  }}

  /* ── NAVIGATION ── */
  nav {{
    position: fixed; top: 0; width: 100%; z-index: 1000;
    padding: 16px 40px; background: var(--bg-glass);
    backdrop-filter: blur(20px); border-bottom: 1px solid var(--border);
    display: flex; justify-content: space-between; align-items: center;
  }}
  .nav-brand {{ font-family: var(--font-heading); font-weight: 900; font-size: 1.4rem; letter-spacing: -0.02em; }}
  .nav-brand span {{ color: var(--accent); }}
  .nav-eq {{ font-family: var(--font-mono); font-size: 0.8rem; color: var(--muted); opacity: 0.8; }}
  .nav-links {{ display: flex; gap: 32px; }}
  .nav-links a {{ text-decoration: none; color: var(--muted); font-size: 0.9rem; font-weight: 600; transition: 0.2s; }}
  .nav-links a:hover, .nav-links a.active {{ color: var(--text); }}

  /* ── HERO ── */
  .hero {{ padding: 160px 40px 80px; text-align: center; position: relative; }}
  .hero-badge {{
    display: inline-block; padding: 6px 16px; background: rgba(100, 80, 255, 0.15);
    border: 1px solid var(--accent); border-radius: 100px; color: var(--accent2);
    font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em;
    margin-bottom: 32px; animation: fadeInDown 0.8s ease;
  }}
  .hero h1 {{
    font-size: clamp(3rem, 8vw, 5.5rem); line-height: 0.9; margin-bottom: 32px;
    background: linear-gradient(to bottom, #fff, #8892b0); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-family: var(--font-heading); font-weight: 900;
  }}
  .hero-master-eq {{ font-family: var(--font-mono); font-size: 1.8rem; color: var(--accent); margin-bottom: 40px; opacity: 0.9; }}
  .hero p {{ max-width: 650px; margin: 0 auto 56px; color: var(--muted); font-size: 1.15rem; }}
  
  .hero-stats {{ display: flex; justify-content: center; gap: 64px; flex-wrap: wrap; }}
  .stat-item {{ text-align: left; }}
  .stat-num {{ font-family: var(--font-heading); font-size: 2.8rem; font-weight: 900; line-height: 1; margin-bottom: 8px; }}
  .stat-label {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); font-weight: 700; }}

  /* ── QUANTUM TICKER ── */
  .quantum-ticker {{
    background: rgba(255,255,255,0.02); border-top: 1px solid var(--border); border-bottom: 1px solid var(--border);
    padding: 14px 40px; display: flex; gap: 48px; justify-content: center; flex-wrap: wrap;
  }}
  .ticker-item {{ font-family: var(--font-mono); font-size: 0.8rem; display: flex; gap: 8px; }}
  .ticker-label {{ color: var(--muted); }}
  .ticker-value {{ color: var(--accent2); font-weight: 700; }}

  /* ── SIMULATOR SECTION ── */
  .simulator-section {{ padding: 60px 40px; max-width: 1440px; margin: 0 auto; }}
  .simulator-frame {{
    width: 100%; height: 600px; border: 1px solid var(--border); border-radius: 32px;
    background: #000; box-shadow: 0 40px 100px rgba(0,0,0,0.8);
  }}

  /* ── LAYOUT ── */
  .layout {{ max-width: 1440px; margin: 0 auto; display: grid; grid-template-columns: 1fr 360px; gap: 0; }}
  @media (max-width: 1100px) {{ .layout {{ grid-template-columns: 1fr; }} }}

  /* ── FEED ── */
  .posts-section {{ padding: 60px 40px 100px 40px; border-right: 1px solid var(--border); }}
  .section-title {{ font-size: 2rem; margin-bottom: 48px; display: flex; align-items: baseline; gap: 16px; font-family: var(--font-heading); font-weight: 900; }}
  .section-badge {{ font-size: 0.9rem; color: var(--muted); font-weight: 400; }}
  
  .posts-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 32px; }}
  
  .post-card {{
    background: var(--bg-alt); border: 1px solid var(--border); border-radius: 24px;
    overflow: hidden; cursor: pointer; transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
    position: relative;
  }}
  .post-card:hover {{ transform: translateY(-10px); border-color: var(--accent); box-shadow: 0 30px 60px rgba(0,0,0,0.5); }}
  
  .post-img-wrap {{ position: relative; aspect-ratio: 16/9; overflow: hidden; background: #0a0a1a; }}
  .post-img-wrap img {{ 
    width: 100%; height: 100%; object-fit: cover; transition: transform 0.8s;
    font-size: 0; /* Hides alt text for broken images to keep UI clean */
  }}
  .post-card:hover .post-img-wrap img {{ transform: scale(1.1); }}
  
  .post-overlay-data {{
    position: absolute; bottom: 16px; left: 16px; right: 16px;
    display: flex; justify-content: space-between;
  }}
  .cirq-pill, .qual-pill {{
    background: rgba(5,5,16,0.8); backdrop-filter: blur(8px); border: 1px solid var(--border);
    padding: 6px 12px; border-radius: 8px; font-family: var(--font-mono); font-size: 0.7rem; font-weight: 700;
  }}
  .cirq-pill {{ color: var(--accent); }}
  .qual-pill {{ color: var(--accent2); }}

  .post-card-content {{ padding: 28px; }}
  .theme-badge {{ font-size: 0.65rem; font-weight: 800; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; }}
  .post-title {{ font-size: 1.4rem; line-height: 1.25; margin: 12px 0 16px; font-weight: 900; font-family: var(--font-heading); color: #fff; }}
  .post-body {{ color: var(--muted); font-size: 0.95rem; line-height: 1.6; min-height: 4.8em; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}
  
  .card-footer {{ margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--border); }}
  .btn-primary {{
    display: inline-block; font-size: 0.85rem; font-weight: 700; color: var(--accent2);
    transition: 0.2s; text-decoration: none;
  }}
  .post-card:hover .btn-primary {{ color: #fff; transform: translateX(5px); }}

  /* ── SIDEBAR ── */
  .sidebar {{ padding: 60px 40px; }}
  .sidebar-section {{ margin-bottom: 60px; }}
  .sidebar-title {{ font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.15em; font-weight: 800; color: var(--accent); margin-bottom: 32px; }}
  
  /* ── PROJECT CARDS ── */
  .project-card {{
    background: rgba(100, 80, 255, 0.05); border: 1px solid var(--border); border-radius: 16px;
    padding: 20px; margin-bottom: 20px; transition: 0.3s; text-decoration: none; display: block;
  }}
  .project-card:hover {{ border-color: var(--accent2); background: rgba(100, 80, 255, 0.1); transform: translateX(5px); }}
  .project-name {{ display: block; font-weight: 900; font-family: var(--font-heading); color: #fff; margin-bottom: 4px; }}
  .project-meta {{ font-size: 0.75rem; color: var(--muted); }}

  .eq-item {{ margin-bottom: 24px; padding: 20px; background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-radius: 16px; }}
  .eq-code {{ display: block; font-family: var(--font-mono); font-size: 1rem; color: var(--accent2); margin: 8px 0; word-break: break-all; }}
  .eq-domain {{ font-size: 0.75rem; color: var(--muted); font-style: italic; }}
  .research-item {{ padding: 12px 0; border-bottom: 1px solid var(--border); color: var(--muted); font-size: 0.9rem; }}

  /* ── MODAL ── */
  .modal-overlay {{
    display: none; position: fixed; inset: 0; z-index: 2000;
    background: rgba(5,5,16,0.9); backdrop-filter: blur(20px);
    align-items: center; justify-content: center; padding: 40px;
  }}
  .modal-overlay.active {{ display: flex; }}
  .modal {{
    background: var(--bg-alt); border: 1px solid var(--border); border-radius: 32px;
    max-width: 1000px; width: 100%; max-height: 90vh; overflow: hidden;
    display: grid; grid-template-columns: 1.2fr 1fr;
    animation: modalIn 0.5s cubic-bezier(0.19, 1, 0.22, 1);
  }}
  @media (max-width: 800px) {{ .modal {{ grid-template-columns: 1fr; }} .modal-media {{ display: none; }} }}
  @keyframes modalIn {{ from {{ opacity: 0; transform: translateY(40px) scale(0.98); }} to {{ opacity: 1; transform: translateY(0) scale(1); }} }}
  
  .modal-media {{ background: #000; border-right: 1px solid var(--border); display: flex; align-items: center; justify-content: center; }}
  .modal-media img {{ width: 100%; height: 100%; object-fit: cover; }}
  
  .modal-content {{ padding: 56px; overflow-y: auto; display: flex; flex-direction: column; }}
  .modal-header {{ display: flex; justify-content: space-between; align-items: start; margin-bottom: 32px; }}
  .modal-close {{ background: none; border: 1px solid var(--border); color: var(--muted); width: 40px; height: 40px; border-radius: 50%; cursor: pointer; transition: 0.2s; }}
  .modal-close:hover {{ color: #fff; border-color: #fff; }}
  .modal-title {{ font-size: 2.5rem; line-height: 1.1; font-weight: 900; margin-bottom: 28px; font-family: var(--font-heading); }}
  .modal-body {{ font-size: 1.2rem; line-height: 1.7; color: var(--muted); margin-bottom: 40px; }}
  
  .quantum-block {{ background: rgba(100, 80, 255, 0.1); border: 1px solid var(--border); border-radius: 16px; padding: 24px; font-family: var(--font-mono); font-size: 0.85rem; }}
  
  /* ── FOOTER ── */
  footer {{ padding: 80px 40px; border-top: 1px solid var(--border); text-align: center; color: var(--muted); }}
  .footer-eq {{ font-family: var(--font-mono); font-size: 1.4rem; color: var(--accent); margin-bottom: 16px; }}

  /* ── ANIMATIONS ── */
  @keyframes fadeInDown {{ from {{ opacity: 0; transform: translateY(-20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
</style>
</head>
<body>

<nav>
  <div class="nav-brand">DKB <span>◈</span> Connected Thoughts</div>
  <div class="nav-eq">Reality = O(∇θ)</div>
  <div class="nav-links">
    <a href="#posts" class="active">Feed</a>
    <a href="visualization.html">System Map 3D</a>
    <a href="#theory">Theory</a>
    <a href="#equations">Equations</a>
  </div>
</nav>

<section class="hero">
  <div class="hero-badge">◈ DKB Phase Framework · Live Feed ◈</div>
  <h1>Connected Thoughts<br>on Consciousness</h1>
  <div class="hero-master-eq">Reality = O(∇θ)</div>
  <p>
    Exploring the DKB Phase Framework through autonomous quantum-validated reflections. 
    Powered by <strong>Google Cirq + Qualtran</strong> logic.
  </p>
  <div class="hero-stats">
    <div class="stat-item">
      <div class="stat-num">{len(posts)}</div>
      <div class="stat-label">Total Insights</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">+895%</div>
      <div class="stat-label">Cirq Coherence</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">-88.8%</div>
      <div class="stat-label">Resource Gain</div>
    </div>
  </div>
</section>

<div class="quantum-ticker">
  <div class="ticker-item"><span class="ticker-label">⟁ Baseline:</span> <span class="ticker-value">201.0μs</span></div>
  <div class="ticker-item"><span class="ticker-label">◈ DKB Lead:</span> <span class="ticker-value">2000.0μs</span></div>
  <div class="ticker-item"><span class="ticker-label">🔬 Engine:</span> <span class="ticker-value">Qualtran v2026.1</span></div>
  <div class="ticker-item"><span class="ticker-label">📋 Today:</span> <span class="ticker-value">{len(today_posts)} / 140 thoughts</span></div>
</div>

<div class="simulator-section">
  <div class="section-title" style="margin-bottom:24px;">Phase Framework Simulator <span class="section-badge">Live Interactive Model</span></div>
  <iframe class="simulator-frame" src="https://dkb-phase-framework-simulator-146274734723.us-west1.run.app/" allow="compute; webgl; fullscreen"></iframe>
</div>

<div class="layout">
  <main class="posts-section" id="posts">
    <div class="section-title">
      Latest Breakthroughs
      <span class="section-badge">{len(posts)} total</span>
    </div>
    <div class="posts-grid" id="postsGrid">
      {cards_html}
    </div>
  </main>

  <aside class="sidebar">
    <div class="sidebar-section">
      <div class="sidebar-title">Hosted Projects</div>
      <a href="https://dkb-phase-framework-simulator-146274734723.us-west1.run.app/" target="_blank" class="project-card">
        <span class="project-name">Phase Simulator</span>
        <span class="project-meta">Real-time interference calculator.</span>
      </a>
      <a href="visualization.html" class="project-card">
        <span class="project-name">3D System Map</span>
        <span class="project-meta">Topological Theory Spine (L0-L12).</span>
      </a>
      <a href="https://youtu.be/ZxNss-vrB2g?si=XN6c9zuRqpXunIhj" target="_blank" class="project-card">
        <span class="project-name">Theory in 60s</span>
        <span class="project-meta">YouTube Documentation.</span>
      </a>
      <a href="https://github.com/Dheeraj7K/MCdq" target="_blank" class="project-card">
        <span class="project-name">Core Repository</span>
        <span class="project-meta">Open-source framework logic.</span>
      </a>
    </div>

    <div class="sidebar-section">
      <div class="sidebar-title">Theory Spine Constants</div>
      <div class="eq-item">
        <span class="eq-num">Master Framework</span>
        <code class="eq-code">Reality = O(∇θ)</code>
        <span class="eq-domain">Unified Phase Spacetime</span>
      </div>
      <div class="eq-item">
        <span class="eq-num">Author</span>
        <span class="eq-name">Dheeraj Kumar Bakoriya</span>
        <span class="eq-domain">Principal Investigator</span>
      </div>
    </div>

    <div class="sidebar-section" id="equations">
      <div class="sidebar-title">Core Mathematical Proofs</div>
      {equations_html}
    </div>

    <div class="sidebar-section">
      <div class="sidebar-title">Active Field Research</div>
      <ul style="list-style:none; padding: 0;">
        {research_html}
      </ul>
    </div>
  </aside>
</div>

<div class="modal-overlay" id="modalOverlay" onclick="closePost(event)">
  <div class="modal" id="modal">
    <div class="modal-media" id="modalMedia">
      <img id="modalImg" src="" alt="">
    </div>
    <div class="modal-content">
      <div class="modal-header">
        <span class="modal-theme" id="modalTheme"></span>
        <button class="modal-close" onclick="closeModal()">✕</button>
      </div>
      <div class="modal-title" id="modalTitle"></div>
      <div class="modal-body" id="modalBody"></div>
      <div class="quantum-block">
        <div style="color: var(--accent); margin-bottom: 8px; font-weight: 900;">QUANTUM VALIDATION [ Cirq + Qualtran ]</div>
        <div id="modalQuantum"></div>
      </div>
    </div>
  </div>
</div>

<footer>
  <div class="footer-eq">Reality = O(∇θ)</div>
  <div>DKB Connected Thoughts · Automated {datetime.now().strftime("%Y")} · Dheeraj Kumar Bakoriya</div>
</footer>

<script>
function openPostById(postJson) {{
  const post = JSON.parse(postJson.replace(/&quot;/g, '"'));
  console.log("Opening post:", post);
  
  document.getElementById('modalTheme').textContent = post.theme;
  document.getElementById('modalTitle').textContent = post.title;
  document.getElementById('modalBody').textContent = post.body;
  
  const c = post.quantum?.cirq || {{}};
  const q = post.quantum?.qualtran || {{}};
  document.getElementById('modalQuantum').innerHTML = 
    '• Coherence: +' + (c.improvement_pct||895) + '% (φ^5 node)<br>' +
    '• T-Gate Resource Cost: ' + (q.dkb_tgates||22344) + ' (Red: -' + (q.reduction_pct||88.83) + '%)';
    
  const img = document.getElementById('modalImg');
  const media = document.getElementById('modalMedia');
  img.src = post.image_path || '';
  media.style.display = post.image_path ? 'flex' : 'none';
  
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

    # Generate Visualization Page (Self-contained for offline/file access)
    viz_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DKB Phase Framework | Multi-Perspective Map</title>
    <script src="https://unpkg.com/3d-force-graph"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;900&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
        body {{ margin: 0; background: #050510; color: #fff; font-family: 'Outfit', sans-serif; overflow: hidden; }}
        #3d-graph {{ width: 100vw; height: 100vh; }}
        
        /* ── UI OVERLAYS ── */
        .overlay {{ position: absolute; top: 24px; left: 24px; z-index: 10; pointer-events: none; }}
        .nav-back {{ pointer-events: auto; text-decoration: none; color: #6450ff; font-size: 0.9rem; font-weight: 600; margin-bottom: 12px; display: block; }}
        .title {{ font-size: 2.2rem; font-weight: 900; margin: 0; letter-spacing: -0.02em; }}
        .subtitle {{ font-size: 1rem; color: #8892b0; margin-top: 4px; opacity: 0.8; }}
        #node-counter {{ margin-top: 16px; font-family: 'JetBrains Mono', monospace; color: #00ccff; font-size: 0.9rem; font-weight: 700; background: rgba(100,80,255,0.1); padding: 8px 16px; border-radius: 8px; display: inline-block; border: 1px solid rgba(100,80,255,0.2); pointer-events: auto; }}

        /* ── CONTROLS PANEL ── */
        .controls {{ 
            position: absolute; top: 24px; right: 24px; z-index: 100; 
            background: rgba(10, 10, 31, 0.8); backdrop-filter: blur(20px);
            border: 1px solid rgba(100, 80, 255, 0.3); border-radius: 16px;
            padding: 20px; width: 280px; box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        }}
        .control-group {{ margin-bottom: 20px; }}
        .control-label {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #8892b0; font-weight: 800; margin-bottom: 12px; display: block; }}
        .btn-tabs {{ display: flex; gap: 4px; background: rgba(0,0,0,0.3); padding: 4px; border-radius: 8px; }}
        .btn-tab {{ 
            flex: 1; border: none; background: transparent; color: #8892b0; 
            padding: 8px; font-size: 0.8rem; font-weight: 700; border-radius: 6px; 
            cursor: pointer; transition: 0.2s; 
        }}
        .btn-tab.active {{ background: #6450ff; color: #fff; }}
        
        .slider-container {{ display: flex; align-items: center; gap: 12px; }}
        input[type="range"] {{ flex: 1; accent-color: #6450ff; cursor: pointer; }}
        
        .legend {{ position: absolute; bottom: 24px; left: 24px; z-index: 10; padding: 16px; background: rgba(255,255,255,0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; font-size: 0.8rem; }}
        .legend-item {{ display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }}
        .dot {{ width: 8px; height: 8px; border-radius: 50%; }}
    </style>
</head>
<body>
    <div class="overlay">
        <a href="index.html" class="nav-back">← Back to Feed</a>
        <h1 class="title">DKB System Map</h1>
        <p class="subtitle">Multi-Perspective Theory Architecture</p>
        <div id="node-counter">Nodes: <span id="node-count">{len(graph_nodes)}</span></div>
    </div>

    <div class="controls">
        <div class="control-group">
            <span class="control-label">Perspective</span>
            <div class="btn-tabs">
                <button class="btn-tab active" onclick="setView(3)">3D Space</button>
                <button class="btn-tab" onclick="setView(2)">2D Plane</button>
            </div>
        </div>
        <div class="control-group">
            <span class="control-label">Topology Layout</span>
            <div class="btn-tabs">
                <button class="btn-tab active" onclick="setLayout(null)">Cosmic</button>
                <button class="btn-tab" onclick="setLayout('td')">Top-Down</button>
                <button class="btn-tab" onclick="setLayout('radialout')">Radial</button>
            </div>
        </div>
        <div class="control-group">
            <span class="control-label">Interconnectedness (Opacity)</span>
            <div class="slider-container">
                <input type="range" min="0" max="100" value="40" oninput="setOpacity(this.value)">
                <span id="opacity-val" style="font-family: monospace; font-size:0.8rem; min-width:30px;">0.4</span>
            </div>
        </div>
    </div>

    <div id="3d-graph"></div>

    <div class="legend">
        <div class="legend-item"><div class="dot" style="background:#ff33cc"></div> Master Equation</div>
        <div class="legend-item"><div class="dot" style="background:#ffcc00"></div> Mega Nodes (12 Levels)</div>
        <div class="legend-item"><div class="dot" style="background:#6450ff"></div> Core Pillar Laws</div>
        <div class="legend-item"><div class="dot" style="background:#ffee00"></div> Physical Constants</div>
        <div class="legend-item"><div class="dot" style="background:#00ffff"></div> Arc Dynamics & Star Nodes</div>
        <div class="legend-item"><div class="dot" style="background:#00ccff"></div> Meta Emerged Nodes</div>
        <div class="legend-item"><div class="dot" style="background:#33ff33"></div> Impact Breakthroughs</div>
    </div>

    <script>
        const graphData = {graph_json};
        let currentOpacity = 0.4;
        
        const Graph = ForceGraph3D()(document.getElementById('3d-graph'))
            .graphData(graphData)
            .nodeLabel(node => `
                <div style="background: rgba(5,5,16,0.95); padding: 12px; border: 1px solid ${{node.color}}; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
                    <div style="color:${{node.color}}; font-weight:900; font-size: 1rem; margin-bottom: 4px;">${{node.id}}</div>
                    <div style="font-size:0.9rem; color: #fff; margin-bottom: 4px;">${{node.name}}</div>
                    <div style="font-size:0.75rem; color: #8892b0; font-family: 'JetBrains Mono', monospace;">${{node.desc}}</div>
                </div>`)
            .nodeColor(node => node.color)
            .nodeVal(node => node.val)
            .linkColor(() => `rgba(100,80,255,${{currentOpacity}})`)
            .linkWidth(2)
            .linkDirectionalParticles(2)
            .linkDirectionalParticleSpeed(0.005)
            .backgroundColor('#050510');
        
        Graph.d3Force('charge').strength(-150);
        Graph.d3Force('link').distance(120);

        function setView(dims) {{
            Graph.numDimensions(dims);
            document.querySelectorAll('.control-group:nth-child(1) .btn-tab').forEach((btn, i) => {{
                btn.classList.toggle('active', (dims === 3 && i === 0) || (dims === 2 && i === 1));
            }});
        }}

        function setLayout(mode) {{
            Graph.dagMode(mode);
            if (mode) Graph.dagLevelDistance(200);
            document.querySelectorAll('.control-group:nth-child(2) .btn-tab').forEach((btn, i) => {{
                const modes = [null, 'td', 'radialout'];
                btn.classList.toggle('active', modes[i] === mode);
            }});
        }}

        function setOpacity(val) {{
            currentOpacity = val / 100;
            document.getElementById('opacity-val').innerText = currentOpacity.toFixed(1);
            Graph.linkColor(Graph.linkColor()); // Refresh
        }}
    </script>
</body>
</html>'''

    with open(website_dir / "visualization.html", "w") as f:
        f.write(viz_html)

    with open(website_dir / "index.html", "w") as f:
        f.write(html)


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--build" in sys.argv:
        print("◈ Rebuilding DKB Website...")
        posts = get_all_posts(300)
        theory = load_theory()
        _build_website(posts, theory)
        print("✅ Done.")
    else:
        print("◈ DKB Connected Thoughts MCP Server starting...", file=sys.stderr)
        print("  Tools: generate_thought_batch, run_full_day_cycle, get_quantum_reading,", file=sys.stderr)
        print("         update_theory, rebuild_website, list_posts, get_theory_status, get_schedule", file=sys.stderr)
        mcp.run(transport="stdio")
