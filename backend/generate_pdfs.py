# generate_pdfs.py
# Run: pip install reportlab && python generate_pdfs.py
# Outputs 5 PDFs into ./data/pdfs/

# if you want to have a ease understanding , trying running it function by function in notebook 

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
import os

OUTPUT_DIR = "./data/pdfs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Shared helpers 
def base_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="DocTitle",
        fontSize=22, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=6, leading=28
    ))
    styles.add(ParagraphStyle(
        name="DocSubtitle",
        fontSize=12, fontName="Helvetica",
        textColor=colors.HexColor("#4a4a6a"),
        spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontSize=14, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#16213e"),
        spaceBefore=18, spaceAfter=8,
        borderPad=4
    ))
    styles.add(ParagraphStyle(
        name="Body",
        fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#2d2d2d"),
        leading=16, spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name="Bullet",
        fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#2d2d2d"),
        leading=15, leftIndent=20,
        bulletIndent=8, spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name="Caption",
        fontSize=8, fontName="Helvetica-Oblique",
        textColor=colors.HexColor("#888888"),
        spaceAfter=12
    ))
    return styles

def divider():
    return HRFlowable(width="100%", thickness=0.5,
                      color=colors.HexColor("#cccccc"), spaceAfter=10)

def table_style():
    return TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  colors.HexColor("#16213e")),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0),  9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor("#f5f5f5"), colors.white]),
        ("FONTNAME",    (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 1), (-1, -1), 9),
        ("GRID",        (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ])

def build(filename, story):
    path = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=0.9*inch, rightMargin=0.9*inch,
        topMargin=0.9*inch, bottomMargin=0.9*inch
    )
    doc.build(story)
    print(f"  ✓  {filename}")

# ── PDF 1 — Quarterly Executive Report 
def pdf_quarterly_report():
    s = base_styles()
    story = []

    story += [
        Paragraph("CineVerse Entertainment", s["DocTitle"]),
        Paragraph("Quarterly Executive Report — Q1 2025", s["DocSubtitle"]),
        divider(),
        Paragraph("Executive Summary", s["SectionHeader"]),
        Paragraph(
            "Q1 2025 has been a landmark quarter for CineVerse Entertainment. "
            "Total platform revenue grew 38% year-on-year, driven primarily by "
            "the extraordinary performance of <b>Stellar Run</b>, which became "
            "our highest-grossing release in the streaming era. Subscription "
            "additions reached 4.2 million — our strongest quarter since launch. "
            "Premium tier uptake rose to 34% of the active user base, up from "
            "26% in Q4 2024.", s["Body"]),
        Paragraph(
            "Comedy as a genre continues to underperform expectations. Despite "
            "aggressive marketing spend on <b>Hasee Toh Phasee 2</b> and "
            "<b>Comedy Circus</b>, both titles posted completion rates below 55% "
            "and audience ratings in the 5.5–6.2 range. Leadership has flagged "
            "this trend for strategic review in Q2.", s["Body"]),
        Spacer(1, 8),

        Paragraph("Key Performance Metrics — Q1 2025", s["SectionHeader"]),
    ]

    metrics = [
        ["Metric", "Q1 2025", "Q4 2024", "Change"],
        ["Total Revenue (INR Cr)", "₹8,420 Cr", "₹6,100 Cr", "+38%"],
        ["New Subscriptions", "4.2 M", "2.8 M", "+50%"],
        ["Premium Tier Share", "34%", "26%", "+8pp"],
        ["Avg. Completion Rate", "82%", "74%", "+8pp"],
        ["Active Viewers (Monthly)", "62 M", "48 M", "+29%"],
        ["NPS Score", "71", "64", "+7"],
    ]
    story.append(Table(metrics, colWidths=[200, 90, 90, 80], style=table_style()))
    story.append(Spacer(1, 14))

    story += [
        Paragraph("Top Performing Titles", s["SectionHeader"]),
        Paragraph(
            "<b>Stellar Run</b> (Action, Jan 2025) — Collected ₹520 Cr gross "
            "revenue with a 98% completion rate on premium devices. Viral social "
            "media momentum — particularly a celebrity collaboration campaign — "
            "drove 85 million impressions in the pre-release window. The film "
            "trended on Twitter/X for 11 consecutive days post-release. Mumbai "
            "and Delhi accounted for 42% of total views.", s["Body"]),
        Paragraph(
            "<b>Last Kingdom</b> (Action, Nov 2024) — Continued strong performance "
            "into Q1 2025 with repeat viewership up 22%. Engagement scores remain "
            "above 8.4 across all major cities. Kabir Khan's direction has been "
            "widely praised in critical circles.", s["Body"]),
        Paragraph(
            "<b>Mitti Ki Khushboo</b> (Romance, Feb 2025) — Imtiaz Ali delivered "
            "a critically acclaimed romance with ₹180 Cr revenue and strong "
            "engagement in Tier-1 cities. Female viewers aged 25–40 were the "
            "dominant audience segment.", s["Body"]),

        Paragraph("Underperforming Titles & Concerns", s["SectionHeader"]),
        Paragraph(
            "<b>Dark Orbit</b> (Sci-Fi, Mar 2025) — Despite the highest production "
            "budget of the quarter at ₹150 Cr, the film posted a mixed critical "
            "response (7.8 rating) and below-target completion rates of 65–72%. "
            "Audience feedback cited a convoluted second-half plot. ROI on "
            "marketing spend was the lowest of any 2025 release at 7.2x.", s["Body"]),
        Paragraph(
            "<b>Comedy genre</b> — All three comedy releases in the past two "
            "quarters (Hasee Toh Phasee 2, Comedy Circus, Jugaad Junction) have "
            "underperformed. Common factors include weak scripts, low social media "
            "engagement, and poor word-of-mouth. Marketing ROI for these titles "
            "averaged just 4.6x versus the platform average of 14.8x.", s["Body"]),

        Paragraph("Regional Highlights", s["SectionHeader"]),
        Paragraph(
            "Mumbai leads all cities in views and engagement score (9.6 for "
            "Stellar Run in February). Delhi is a close second. Bangalore is "
            "the fastest-growing market, with engagement scores rising 18% "
            "quarter-on-quarter. Southern markets (Chennai, Hyderabad) show "
            "strong appetite for action and drama but remain underpenetrated "
            "for comedy.", s["Body"]),

        Paragraph("Strategic Priorities for Q2 2025", s["SectionHeader"]),
    ]

    for pt in [
        "Commission at least 3 new action/drama projects following Stellar Run's blueprint.",
        "Suspend greenlight of comedy projects until genre strategy is reviewed.",
        "Increase marketing investment in Bangalore and Hyderabad — fastest-growing markets.",
        "Investigate Dark Orbit audience drop-off in second half — apply learnings to Sci-Fi pipeline.",
        "Expand Celebrity Collaboration campaigns — highest ROI channel at 32x.",
        "Target Premium tier conversion in Tier-2 cities (Jaipur, Lucknow, Agra).",
    ]:
        story.append(Paragraph(f"• {pt}", s["Bullet"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Prepared by: Office of the CEO | CineVerse Entertainment | Confidential",
        s["Caption"]))

    build("quarterly_executive_report.pdf", story)

# ── PDF 2 — Campaign Performance Summary 
def pdf_campaign_summary():
    s = base_styles()
    story = []

    story += [
        Paragraph("CineVerse Entertainment", s["DocTitle"]),
        Paragraph("Campaign Performance Summary — Q1 2025", s["DocSubtitle"]),
        divider(),
        Paragraph("Overview", s["SectionHeader"]),
        Paragraph(
            "This report summarises the marketing campaign performance across "
            "all major releases in Q1 2025. Total marketing expenditure for the "
            "quarter was ₹197 Crore across digital, out-of-home (OOH), and "
            "influencer/celebrity channels. Blended ROI across all campaigns "
            "was 14.8x, though performance varied significantly by title and "
            "channel.", s["Body"]),

        Paragraph("Campaign Summary by Title", s["SectionHeader"]),
    ]

    camps = [
        ["Title", "Total Spend (Cr)", "Impressions (M)", "Conversions", "Blended ROI"],
        ["Stellar Run", "₹80 Cr", "273 M", "17,18,000", "21.8x"],
        ["Dark Orbit", "₹59 Cr", "103 M", "4,37,000", "7.6x"],
        ["Last Kingdom", "₹41 Cr", "118 M", "7,28,000", "18.2x"],
        ["Hasee Toh Phasee 2", "₹25 Cr", "35 M", "1,38,000", "5.5x"],
        ["Comedy Circus", "₹18 Cr", "25 M", "88,000", "4.7x"],
        ["Jugaad Junction", "₹11 Cr", "14 M", "43,000", "3.9x"],
    ]
    story.append(Table(camps, colWidths=[150, 90, 90, 90, 80], style=table_style()))
    story.append(Spacer(1, 14))

    story += [
        Paragraph("Channel Analysis", s["SectionHeader"]),
        Paragraph(
            "<b>Celebrity Collaboration</b> was the standout channel of the quarter, "
            "delivering 32x ROI for Stellar Run's pre-release campaign. A coordinated "
            "push involving 14 A-list celebrities generated 85 million impressions "
            "in 10 days — unprecedented for a CineVerse release.", s["Body"]),
        Paragraph(
            "<b>YouTube</b> remained the highest-volume channel by impressions, "
            "with trailer content for Stellar Run accumulating 68 million views. "
            "YouTube ROI averaged 18.6x for top-performing titles.", s["Body"]),
        Paragraph(
            "<b>Instagram</b> drove the highest conversion rates among 18–34 "
            "demographics. Reel-format content for Stellar Run achieved a 4.4% "
            "click-through rate — 2.8x the platform benchmark.", s["Body"]),
        Paragraph(
            "<b>OOH (Out-of-Home)</b> delivered solid brand visibility for "
            "premium releases but showed weak ROI for comedy titles. Recommend "
            "reallocating OOH budget for lower-rated comedy releases to digital.", s["Body"]),

        Paragraph("Key Findings", s["SectionHeader"]),
    ]
    for pt in [
        "Stellar Run's celebrity collab campaign is a replicable template for future action releases.",
        "Comedy titles suffer from low organic amplification — paid spend cannot compensate for weak word-of-mouth.",
        "Dark Orbit's marketing ROI (7.6x) signals misalignment between campaign messaging and audience expectations.",
        "Instagram Reels outperform static posts by 3.1x on conversion for all genres.",
        "Hotstar Ads placement drove 17.9x ROI for Stellar Run — underused for other titles.",
        "Tier-2 city digital spend remains under-indexed; early tests in Jaipur and Lucknow showed positive signals.",
    ]:
        story.append(Paragraph(f"• {pt}", s["Bullet"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Prepared by: Marketing Analytics Division | CineVerse Entertainment | Confidential",
        s["Caption"]))

    build("campaign_performance_summary.pdf", story)

# ── PDF 3 — Content Roadmap
def pdf_content_roadmap():
    s = base_styles()
    story = []

    story += [
        Paragraph("CineVerse Entertainment", s["DocTitle"]),
        Paragraph("Content Roadmap — Q2 & Q3 2025", s["DocSubtitle"]),
        divider(),
        Paragraph("Strategic Direction", s["SectionHeader"]),
        Paragraph(
            "Following the exceptional performance of Stellar Run and Last Kingdom, "
            "CineVerse's content strategy for 2025 will double down on action and "
            "drama while undertaking a root-cause review of the comedy genre pipeline. "
            "The roadmap below reflects greenlit, in-production, and planned projects "
            "for Q2 and Q3 2025.", s["Body"]),

        Paragraph("Q2 2025 Releases (April – June)", s["SectionHeader"]),
    ]

    q2 = [
        ["Title", "Genre", "Director", "Budget (Cr)", "Release Target", "Status"],
        ["Paani", "Drama", "Shyam Benegal", "₹70 Cr", "May 2025", "Released"],
        ["Laal Qila", "Historical", "Ashutosh Gowariker", "₹120 Cr", "June 2025", "Post-Production"],
        ["Neon Nights", "Thriller", "Sriram Raghavan", "₹85 Cr", "June 2025", "Post-Production"],
    ]
    story.append(Table(q2, colWidths=[110, 70, 120, 70, 80, 90], style=table_style()))
    story.append(Spacer(1, 14))

    story += [
        Paragraph("Q3 2025 Releases (July – September)", s["SectionHeader"]),
    ]

    q3 = [
        ["Title", "Genre", "Director", "Budget (Cr)", "Release Target", "Status"],
        ["Stellar Run 2", "Action", "Zoya Akhtar", "₹200 Cr", "August 2025", "Pre-Production"],
        ["Dharohar", "Drama", "Neeraj Ghaywan", "₹45 Cr", "July 2025", "In Production"],
        ["Code Black", "Thriller", "Anurag Basu", "₹95 Cr", "September 2025", "Script Stage"],
        ["Ishq Wala Love", "Romance", "Imtiaz Ali", "₹60 Cr", "August 2025", "In Production"],
    ]
    story.append(Table(q3, colWidths=[110, 70, 120, 70, 80, 90], style=table_style()))
    story.append(Spacer(1, 14))

    story += [
        Paragraph("Comedy Genre Review", s["SectionHeader"]),
        Paragraph(
            "All comedy projects currently in development have been moved to "
            "'Pending Review' status. The content committee will evaluate script "
            "quality, casting alignment, and cultural relevance before any "
            "greenlight decision. Key questions to address:", s["Body"]),
    ]
    for pt in [
        "Are scripts relying on outdated comedic tropes that no longer resonate with urban audiences?",
        "Is there a mismatch between the age of comedy directors and the 18–30 target demographic?",
        "Should CineVerse commission younger writers/directors for the comedy slate?",
        "Can comedy be blended with action or romance to improve genre performance?",
    ]:
        story.append(Paragraph(f"• {pt}", s["Bullet"]))

    story += [
        Spacer(1, 10),
        Paragraph("Stellar Run Franchise Plan", s["SectionHeader"]),
        Paragraph(
            "Given the extraordinary success of Stellar Run — ₹520 Cr gross, "
            "9.4 avg engagement score, 11 days trending — the content board has "
            "approved a franchise plan. Stellar Run 2 is confirmed for August 2025 "
            "with an expanded budget of ₹200 Cr. A limited series spin-off is "
            "under discussion for the CineVerse OTT platform in 2026.", s["Body"]),
        Spacer(1, 12),
        Paragraph(
            "Prepared by: Content Strategy Division | CineVerse Entertainment | Confidential",
            s["Caption"]),
    ]

    build("content_roadmap.pdf", story)

# ── PDF 4 — Policy Guidelines
def pdf_policy_guidelines():
    s = base_styles()
    story = []

    story += [
        Paragraph("CineVerse Entertainment", s["DocTitle"]),
        Paragraph("Internal Policy Guidelines — Data, AI & Analytics", s["DocSubtitle"]),
        divider(),
        Paragraph("Purpose", s["SectionHeader"]),
        Paragraph(
            "This document outlines CineVerse's internal policies for data handling, "
            "AI system usage, and analytics access. All employees and contractors "
            "with access to internal analytics tools must adhere to these guidelines. "
            "Violations may result in access revocation and disciplinary action.", s["Body"]),

        Paragraph("1. Data Classification", s["SectionHeader"]),
        Paragraph("<b>Level 1 — Public:</b> Aggregated performance metrics shared in press releases.", s["Body"]),
        Paragraph("<b>Level 2 — Internal:</b> Detailed viewership data, regional breakdowns, engagement scores.", s["Body"]),
        Paragraph("<b>Level 3 — Confidential:</b> Viewer PII, subscription tier data, marketing budgets, contract terms.", s["Body"]),
        Paragraph("<b>Level 4 — Restricted:</b> Executive compensation, M&A discussions, unreleased content.", s["Body"]),
        Spacer(1, 8),

        Paragraph("2. AI Analytics Assistant — Permitted Uses", s["SectionHeader"]),
        Paragraph(
            "The CineVerse AI Analytics Assistant is approved for use by all "
            "employees with Level 2 clearance or above. Permitted queries include:", s["Body"]),
    ]
    for pt in [
        "Film performance metrics (revenue, ratings, completion rates).",
        "Regional engagement analysis and city-level performance breakdowns.",
        "Genre trend analysis and audience segmentation insights.",
        "Marketing ROI comparisons across campaigns and channels.",
        "Competitive benchmarking using internal historical data.",
    ]:
        story.append(Paragraph(f"• {pt}", s["Bullet"]))

    story += [
        Spacer(1, 8),
        Paragraph("3. AI Analytics Assistant — Prohibited Uses", s["SectionHeader"]),
    ]
    for pt in [
        "Querying individual viewer PII (names, contact details, payment information).",
        "Exporting raw database tables or bulk downloading viewer records.",
        "Using AI outputs in external communications without approval from Legal.",
        "Attempting to bypass tool-based access controls via prompt manipulation.",
        "Sharing AI-generated reports externally without redacting confidential fields.",
    ]:
        story.append(Paragraph(f"• {pt}", s["Bullet"]))

    story += [
        Spacer(1, 8),
        Paragraph("4. SQL & Data Query Policy", s["SectionHeader"]),
        Paragraph(
            "All database queries executed through the AI assistant are "
            "parameterised and logged. Direct database access is not permitted "
            "outside approved ETL pipelines. The AI assistant may only execute "
            "SELECT queries on approved views — no INSERT, UPDATE, DELETE, or "
            "DDL operations are permitted. Query results exceeding 10,000 rows "
            "will be automatically truncated.", s["Body"]),

        Paragraph("5. Retention & Audit", s["SectionHeader"]),
        Paragraph(
            "All AI assistant queries are logged with timestamp, user ID, query "
            "text, and tool calls executed. Logs are retained for 90 days. "
            "Sensitive fields (viewer PII) are masked in logs. The security team "
            "conducts monthly audits of query logs for policy compliance.", s["Body"]),

        Spacer(1, 12),
        Paragraph(
            "Approved by: CTO & Chief Data Officer | CineVerse Entertainment | v2.1 | March 2025",
            s["Caption"]),
    ]

    build("policy_guidelines.pdf", story)

# pdf 5 — Audience Behavior Report
def pdf_audience_report():
    s = base_styles()
    story = []

    story += [
        Paragraph("CineVerse Entertainment", s["DocTitle"]),
        Paragraph("Audience Behavior Report — H2 2024 & Q1 2025", s["DocSubtitle"]),
        divider(),
        Paragraph("Introduction", s["SectionHeader"]),
        Paragraph(
            "This report analyses viewer behaviour patterns across CineVerse's "
            "platform during H2 2024 and Q1 2025. Data is drawn from 62 million "
            "monthly active users across India. Key dimensions analysed include "
            "genre preference by age and region, device usage, completion rates, "
            "subscription tier behaviour, and repeat viewing patterns.", s["Body"]),

        Paragraph("Genre Preferences by Age Segment", s["SectionHeader"]),
    ]

    genre_age = [
        ["Genre", "18–24", "25–34", "35–44", "45+"],
        ["Action", "38%", "34%", "22%", "12%"],
        ["Drama", "18%", "28%", "34%", "42%"],
        ["Comedy", "22%", "18%", "20%", "24%"],
        ["Romance", "14%", "12%", "16%", "14%"],
        ["Thriller", "6%", "6%", "6%", "6%"],
        ["Horror/Other", "2%", "2%", "2%", "2%"],
    ]
    story.append(Table(genre_age, colWidths=[120, 80, 80, 80, 80], style=table_style()))
    story.append(Spacer(1, 14))

    story += [
        Paragraph(
            "Action dominates the 18–34 demographic, which directly explains "
            "Stellar Run's outsized performance with younger urban viewers. "
            "Drama is the top genre for viewers 35 and above. Comedy's relatively "
            "flat distribution across age groups suggests the issue is content "
            "quality rather than demographic mismatch.", s["Body"]),

        Paragraph("Regional Viewing Behaviour", s["SectionHeader"]),
        Paragraph(
            "<b>Mumbai</b> is the highest-engagement city across all genres, "
            "consistently posting engagement scores 0.3–0.5 points above the "
            "national average. Premium tier penetration in Mumbai is 48% — highest "
            "in the country. Viewers in Mumbai also show the highest repeat viewing "
            "rate at 22% of total watch sessions.", s["Body"]),
        Paragraph(
            "<b>Bangalore</b> is the fastest-growing market. Engagement scores "
            "grew 18% QoQ in Q1 2025. The 22–32 age cohort is dominant, with "
            "strong preference for action and thriller content. Premium conversion "
            "rates are improving rapidly.", s["Body"]),
        Paragraph(
            "<b>Delhi</b> shows strong absolute numbers but slightly lower "
            "engagement scores than Mumbai, partly attributed to higher free-tier "
            "usage. Comedy performs marginally better in Delhi than other metro "
            "cities.", s["Body"]),
        Paragraph(
            "<b>Tier-2 cities</b> (Jaipur, Lucknow, Agra, Ranchi) are "
            "under-penetrated but show high completion rates when content "
            "does land — suggesting strong latent demand once discovery "
            "improves.", s["Body"]),

        Paragraph("Completion Rate Analysis", s["SectionHeader"]),
    ]

    comp = [
        ["Genre", "Avg Completion Rate", "Premium Tier", "Free Tier"],
        ["Action", "91%", "97%", "82%"],
        ["Drama", "86%", "93%", "76%"],
        ["Romance", "83%", "90%", "73%"],
        ["Thriller", "88%", "94%", "79%"],
        ["Comedy", "58%", "66%", "48%"],
        ["Horror", "79%", "85%", "68%"],
    ]
    story.append(Table(comp, colWidths=[120, 130, 100, 100], style=table_style()))
    story.append(Spacer(1, 14))

    story += [
        Paragraph(
            "Comedy's 58% average completion rate is the lowest of any genre "
            "and a key signal of audience dissatisfaction. Viewers are starting "
            "comedy films but not finishing them — indicating the drop-off is "
            "a content quality issue rather than a discovery problem. "
            "This is corroborated by low NPS scores and negative review sentiment "
            "for recent comedy releases.", s["Body"]),

        Paragraph("Device & Viewing Context", s["SectionHeader"]),
        Paragraph(
            "Mobile is the dominant device at 61% of total watch sessions, "
            "followed by TV (Smart TV / Cast) at 26% and Laptop at 13%. "
            "Premium tier subscribers are 2.4x more likely to watch on TV, "
            "which correlates with higher completion rates and engagement scores. "
            "Stellar Run's premium viewership drove a record 34% of its streams "
            "on connected TVs.", s["Body"]),

        Paragraph("Key Behavioural Insights for Leadership", s["SectionHeader"]),
    ]
    for pt in [
        "Stellar Run created a new benchmark: 98% completion rate + 22% repeat view rate — study this blueprint.",
        "Comedy viewers drop off within the first 40 minutes — scripts need stronger opening acts.",
        "Bangalore is the next Mumbai — marketing spend should be reweighted accordingly.",
        "Premium tier subscribers drive disproportionate engagement; conversion incentives should be prioritised.",
        "Celebrity-driven social campaigns correlate directly with Day-1 viewership spikes.",
        "Sci-Fi (Dark Orbit) needs audience education campaigns — the genre is nascent in India.",
    ]:
        story.append(Paragraph(f"• {pt}", s["Bullet"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Prepared by: Audience Intelligence Team | CineVerse Entertainment | Confidential",
        s["Caption"]))

    build("audience_behavior_report.pdf", story)

# Main execution
if __name__ == "__main__":
    print("\n🎬 Generating PDF documents...\n")
    pdf_quarterly_report()
    pdf_campaign_summary()
    pdf_content_roadmap()
    pdf_policy_guidelines()
    pdf_audience_report()
    print(f"\nAll 5 PDFs saved to {OUTPUT_DIR}/\n")