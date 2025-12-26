import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Social Media Automation Cost Dashboard",
    page_icon="💰",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
    .section-header {
        background: rgba(255, 255, 255, 0.9);
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("💰 Social Media Automation Cost Dashboard")
st.markdown("**Complete cost analysis for Badges, Memes & Blog automation**")
st.markdown("---")

# Sidebar controls
st.sidebar.header("⚙️ Configuration")

st.sidebar.subheader("🎯 Badge Posting")
badge_count = st.sidebar.slider(
    "Badges per Day",
    min_value=1,
    max_value=1000,
    value=100,
    step=1
)
badge_retry_scenario = st.sidebar.selectbox(
    "Badge Retry Scenario",
    ["Best Case (1 attempt)", "Worst Case (5 retries)"],
    key="badge_retry"
)

st.sidebar.subheader("🎨 Meme Generation")
meme_count = st.sidebar.slider(
    "Memes per Day",
    min_value=1,
    max_value=500,
    value=50,
    step=1
)
instagram_refresh = st.sidebar.selectbox(
    "Instagram Data Refresh",
    ["Daily", "Weekly", "Monthly"],
    key="ig_refresh"
)

st.sidebar.subheader("📰 Blog Posting")
blog_count = st.sidebar.slider(
    "Blogs per Day",
    min_value=1,
    max_value=100,
    value=10,
    step=1
)
news_refresh = st.sidebar.selectbox(
    "News Data Refresh",
    ["Daily", "Weekly", "Monthly"],
    key="news_refresh"
)

# ============= BADGE COSTS =============
badge_costs = {
    "scraping": 0.00605,
    "search": 0.00001,
    "caption_single": 0.00189,
    "caption_retry": 0.00945,
    "posting": 0.00
}

badge_caption_cost = badge_costs["caption_single"] if "Best" in badge_retry_scenario else badge_costs["caption_retry"]
badge_cost_per_item = badge_costs["scraping"] + badge_costs["search"] + badge_caption_cost + badge_costs["posting"]
badge_daily_cost = badge_cost_per_item * badge_count

# ============= MEME COSTS =============
# One-time scraping costs (prorated based on refresh frequency)
instagram_scraping_cost = 0.69  # One run
instagram_embedding_cost = 0.00648  # One run

refresh_days = {
    "Daily": 1,
    "Weekly": 7,
    "Monthly": 30
}

ig_daily_scraping = instagram_scraping_cost / refresh_days[instagram_refresh]
ig_daily_embedding = instagram_embedding_cost / refresh_days[instagram_refresh]

# Per-meme generation costs (Gemini for meme creation)
meme_query_embedding_cost = 0.000004  # Query embedding (negligible)
meme_text_generation_cost = 0.012  # Gemini 2.5 Pro (idea + caption)
meme_image_generation_cost = 0.039  # Gemini Flash Image (actual image)

meme_cost_per_item = meme_query_embedding_cost + meme_text_generation_cost + meme_image_generation_cost
meme_daily_generation = meme_cost_per_item * meme_count
meme_daily_cost = meme_daily_generation + ig_daily_scraping + ig_daily_embedding

# ============= BLOG COSTS =============
# One-time scraping costs (prorated based on refresh frequency)
news_scraping_cost = 1.60  # One run (Google News)
news_embedding_cost = 0.00115  # One run (News embeddings)

news_daily_scraping = news_scraping_cost / refresh_days[news_refresh]
news_daily_embedding = news_embedding_cost / refresh_days[news_refresh]

# Per-blog generation costs (Multi-source: Book + YouTube + News)
# Source embeddings (per blog)
book_embedding_cost = 0.0012  # ~10,000 tokens from book
youtube_embedding_cost = 0.00096  # ~8,000 tokens from YouTube transcript
blog_source_embeddings = book_embedding_cost + youtube_embedding_cost  # Total: 0.00216

# CrewAI blog generation (Gemini 2.5 Pro)
blog_gemini_input_cost = 0.005  # Context + instructions (~4,000 tokens)
blog_gemini_output_cost = 0.012  # Blog content (~1,200 tokens)
blog_generation_cost = blog_gemini_input_cost + blog_gemini_output_cost  # Total: 0.017

# Total per blog
blog_cost_per_item = blog_source_embeddings + blog_generation_cost
blog_daily_generation = blog_cost_per_item * blog_count
blog_daily_cost = blog_daily_generation + news_daily_scraping + news_daily_embedding

# ============= TOTALS =============
total_daily_cost = badge_daily_cost + meme_daily_cost + blog_daily_cost
total_monthly_cost = total_daily_cost * 30
total_monthly_posts = (badge_count + meme_count + blog_count) * 30

# ============= KEY METRICS =============
st.markdown("### 📊 Overall Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💵 Total Daily Cost",
        value=f"${total_daily_cost:.2f}",
        delta=f"{badge_count + meme_count + blog_count} posts/day"
    )

with col2:
    st.metric(
        label="📈 Monthly Cost",
        value=f"${total_monthly_cost:.2f}",
        delta="30 days projection"
    )

with col3:
    st.metric(
        label="📮 Total Posts/Month",
        value=f"{total_monthly_posts:,}",
        delta="all platforms"
    )

with col4:
    avg_cost_per_post = total_daily_cost / (badge_count + meme_count + blog_count)
    st.metric(
        label="⚡ Avg Cost/Post",
        value=f"${avg_cost_per_post:.4f}",
        delta="blended rate"
    )

st.markdown("---")

# ============= COST DISTRIBUTION PIE CHART =============
st.markdown("### 🥧 Daily Cost Distribution")

fig_pie = go.Figure(data=[go.Pie(
    labels=['Badges', 'Memes', 'Blogs'],
    values=[badge_daily_cost, meme_daily_cost, blog_daily_cost],
    hole=.4,
    marker_colors=['#667eea', '#f093fb', '#4facfe']
)])

fig_pie.update_layout(
    showlegend=True,
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ============= DETAILED BREAKDOWNS =============
tab1, tab2, tab3 = st.tabs(["🎯 Badge Posting", "🎨 Meme Generation", "📰 Blog Posting"])

# --- BADGE TAB ---
with tab1:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("#### 💡 Cost Breakdown per Badge")
        
        badge_breakdown = {
            "Component": [
                "🏷️ Hashtag Scraping",
                "🔍 Viral Hashtag Search",
                "✍️ Caption Generation",
                "📤 Social Media Posting"
            ],
            "Cost": [
                f"${badge_costs['scraping']:.5f}",
                f"${badge_costs['search']:.5f}",
                f"${badge_caption_cost:.5f}",
                f"${badge_costs['posting']:.2f}"
            ],
            "Percentage": [
                f"{(badge_costs['scraping'] / badge_cost_per_item * 100):.1f}%",
                f"{(badge_costs['search'] / badge_cost_per_item * 100):.1f}%",
                f"{(badge_caption_cost / badge_cost_per_item * 100):.1f}%",
                f"{(badge_costs['posting'] / badge_cost_per_item * 100):.1f}%"
            ]
        }
        
        st.dataframe(pd.DataFrame(badge_breakdown), use_container_width=True, hide_index=True)
        st.markdown(f"**Per Badge: ${badge_cost_per_item:.5f}**")
        st.markdown(f"**Daily Total: ${badge_daily_cost:.2f}**")
    
    with col_right:
        st.markdown("#### 📊 Badge Scaling")
        
        badge_volumes = [10, 50, 100, 500, 1000]
        badge_scaling = pd.DataFrame({
            "Volume": [f"{v:,}" for v in badge_volumes],
            "Daily Cost": [f"${(v * badge_cost_per_item):.2f}" for v in badge_volumes],
            "Monthly Cost": [f"${(v * badge_cost_per_item * 30):.2f}" for v in badge_volumes]
        })
        
        st.dataframe(badge_scaling, use_container_width=True, hide_index=True)

# --- MEME TAB ---
with tab2:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("#### 💡 Meme Cost Breakdown")
        
        st.markdown("**Infrastructure Costs (Prorated)**")
        infra_breakdown = {
            "Component": [
                "📸 Instagram Scraping",
                "🧠 Instagram Embeddings",
                "💾 Pinecone Storage"
            ],
            "Per Day": [
                f"${ig_daily_scraping:.4f}",
                f"${ig_daily_embedding:.5f}",
                "$0.00"
            ],
            "Refresh": [
                instagram_refresh,
                instagram_refresh,
                "Real-time"
            ]
        }
        st.dataframe(pd.DataFrame(infra_breakdown), use_container_width=True, hide_index=True)
        
        st.markdown("**Per-Meme Generation Costs**")
        meme_gen_breakdown = {
            "Component": [
                "🔍 Query Embedding",
                "🧠 AI Idea & Caption (Gemini Pro)",
                "🎨 Image Generation (Gemini Flash)"
            ],
            "Cost": [
                f"${meme_query_embedding_cost:.6f}",
                f"${meme_text_generation_cost:.5f}",
                f"${meme_image_generation_cost:.5f}"
            ],
            "Share": [
                f"{(meme_query_embedding_cost / meme_cost_per_item * 100):.1f}%",
                f"{(meme_text_generation_cost / meme_cost_per_item * 100):.1f}%",
                f"{(meme_image_generation_cost / meme_cost_per_item * 100):.1f}%"
            ]
        }
        st.dataframe(pd.DataFrame(meme_gen_breakdown), use_container_width=True, hide_index=True)
        
        st.markdown(f"**Per Meme: ${meme_cost_per_item:.4f}** (~5.1¢)")
        st.markdown(f"**Daily Total: ${meme_daily_cost:.2f}**")
        
        st.caption("💡 76% of meme cost is AI image generation, 24% is reasoning & copywriting")
    
    with col_right:
        st.markdown("#### 📊 Meme Scaling")
        
        meme_volumes = [10, 25, 50, 100, 250]
        meme_scaling = pd.DataFrame({
            "Volume": [f"{v:,}" for v in meme_volumes],
            "Generation Cost": [f"${(v * meme_cost_per_item):.2f}" for v in meme_volumes],
            "Total Daily": [f"${(v * meme_cost_per_item + ig_daily_scraping + ig_daily_embedding):.2f}" for v in meme_volumes]
        })
        
        st.dataframe(meme_scaling, use_container_width=True, hide_index=True)
        
        st.info(f"""
        💡 **Instagram data refreshes {instagram_refresh.lower()}**
        - One-time scrape: ${instagram_scraping_cost:.2f}
        - Prorated daily: ${ig_daily_scraping:.4f}
        - Total items: 300 (3 accounts × 100 items)
        
        **Per-Meme Breakdown:**
        - 🎨 Image generation: ${meme_image_generation_cost:.3f} (76%)
        - 🧠 AI reasoning: ${meme_text_generation_cost:.3f} (24%)
        - 🔍 Data retrieval: Included in infrastructure
        """)

# --- BLOG TAB ---
with tab3:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("#### 💡 Blog Cost Breakdown")
        
        st.markdown("**Infrastructure Costs (Prorated)**")
        blog_infra_breakdown = {
            "Component": [
                "📰 Google News Scraping",
                "🧠 News Embeddings",
                "💾 Pinecone Storage"
            ],
            "Per Day": [
                f"${news_daily_scraping:.4f}",
                f"${news_daily_embedding:.5f}",
                "$0.00"
            ],
            "Refresh": [
                news_refresh,
                news_refresh,
                "Real-time"
            ]
        }
        st.dataframe(pd.DataFrame(blog_infra_breakdown), use_container_width=True, hide_index=True)
        
        st.markdown("**Per-Blog Generation Costs**")
        blog_gen_breakdown = {
            "Component": [
                "📚 Book Embedding (~10k tokens)",
                "🎥 YouTube Transcript Embedding (~8k tokens)",
                "🤖 AI Writing - Input (CrewAI + Gemini Pro)",
                "✍️ AI Writing - Output (Blog Content)",
                "📤 Publishing (AyeShare)"
            ],
            "Cost": [
                f"${book_embedding_cost:.5f}",
                f"${youtube_embedding_cost:.5f}",
                f"${blog_gemini_input_cost:.5f}",
                f"${blog_gemini_output_cost:.5f}",
                "$0.00"
            ],
            "Share": [
                f"{(book_embedding_cost / blog_cost_per_item * 100):.1f}%",
                f"{(youtube_embedding_cost / blog_cost_per_item * 100):.1f}%",
                f"{(blog_gemini_input_cost / blog_cost_per_item * 100):.1f}%",
                f"{(blog_gemini_output_cost / blog_cost_per_item * 100):.1f}%",
                "0%"
            ]
        }
        st.dataframe(pd.DataFrame(blog_gen_breakdown), use_container_width=True, hide_index=True)
        
        st.markdown(f"**Per Blog: ${blog_cost_per_item:.4f}** (~1.9¢)")
        st.markdown(f"**Daily Total: ${blog_daily_cost:.2f}**")
        
        st.caption("💡 90% of blog cost is AI writing & reasoning, 10% is multi-source embeddings")
    
    with col_right:
        st.markdown("#### 📊 Blog Scaling")
        
        blog_volumes = [5, 10, 25, 50, 100]
        blog_scaling = pd.DataFrame({
            "Volume": [f"{v:,}" for v in blog_volumes],
            "Generation Cost": [f"${(v * blog_cost_per_item):.2f}" for v in blog_volumes],
            "Total Daily": [f"${(v * blog_cost_per_item + news_daily_scraping + news_daily_embedding):.2f}" for v in blog_volumes]
        })
        
        st.dataframe(blog_scaling, use_container_width=True, hide_index=True)
        
        st.info(f"""
        💡 **News data refreshes {news_refresh.lower()}**
        - One-time scrape: ${news_scraping_cost:.2f}
        - Prorated daily: ${news_daily_scraping:.4f}
        - Total articles: 80 (4 queries × 20 results)
        
        **Per-Blog Breakdown:**
        - ✍️ AI writing (CrewAI + Gemini): ${blog_generation_cost:.3f} (~90%)
        - 📚 Multi-source embeddings: ${blog_source_embeddings:.3f} (~10%)
        - 📤 Publishing: Included in AyeShare subscription
        
        **Sources per blog:** Book content + YouTube transcript + News context
        """)

st.markdown("---")

# ============= MONTHLY PROJECTION =============
st.markdown("### 📈 Monthly Cost Projection")

monthly_data = pd.DataFrame({
    'Category': ['Badges', 'Memes', 'Blogs', 'Total'],
    'Daily Cost': [badge_daily_cost, meme_daily_cost, blog_daily_cost, total_daily_cost],
    'Monthly Cost': [badge_daily_cost * 30, meme_daily_cost * 30, blog_daily_cost * 30, total_monthly_cost]
})

fig_bar = px.bar(
    monthly_data[monthly_data['Category'] != 'Total'],
    x='Category',
    y='Monthly Cost',
    color='Category',
    color_discrete_sequence=['#667eea', '#f093fb', '#4facfe'],
    text='Monthly Cost'
)

fig_bar.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
fig_bar.update_layout(
    showlegend=False,
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    yaxis_title="Monthly Cost ($)"
)

st.plotly_chart(fig_bar, use_container_width=True)

# ============= KEY INSIGHTS =============
st.markdown("### 💡 Key Insights")

col1, col2 = st.columns(2)

with col1:
    st.success(f"""
    **💰 Cost Efficiency**
    - Blended rate: ${avg_cost_per_post:.4f} per post
    - Badges are most cost-effective: ${badge_cost_per_item:.5f}
    - Memes cost ~5.1¢ each (mostly AI image generation)
    - Blogs cost ~1.9¢ each (multi-source AI writing)
    - Infrastructure costs optimized with refresh scheduling
    """)

with col2:
    st.info(f"""
    **🎯 Optimization Tips**
    - Switch meme data to weekly: Save ${ig_daily_scraping * 30 * 0.85:.2f}/month
    - Switch news to weekly: Save ${news_daily_scraping * 30 * 0.85:.2f}/month
    - Batch blog posts (5-10 daily) for best ROI
    - Badge retries can increase costs by {((badge_costs['caption_retry'] - badge_costs['caption_single']) / badge_costs['caption_single'] * 100):.0f}%
    """)

# ============= DETAILED STATS =============
with st.expander("📊 View Detailed Statistics"):
    st.markdown("#### Volume & Cost Matrix")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.metric("Daily Posts", f"{badge_count + meme_count + blog_count:,}")
        st.metric("Monthly Posts", f"{total_monthly_posts:,}")
    
    with col_b:
        st.metric("Daily Infrastructure", f"${ig_daily_scraping + ig_daily_embedding + news_daily_scraping + news_daily_embedding:.2f}")
        st.metric("Daily Generation", f"${badge_daily_cost + meme_daily_generation + blog_daily_generation:.2f}")
    
    with col_c:
        st.metric("Yearly Projection", f"${total_monthly_cost * 12:.2f}")
        st.metric("Cost per 1K posts", f"${(total_daily_cost / (badge_count + meme_count + blog_count) * 1000):.2f}")

# Footer
st.markdown("---")
st.markdown("**💡 Tip:** Adjust the configuration in the sidebar to see real-time cost changes across all automation types!")
