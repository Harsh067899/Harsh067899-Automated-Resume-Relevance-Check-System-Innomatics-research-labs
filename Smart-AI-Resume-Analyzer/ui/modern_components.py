"""
Modern UI Components for Smart Resume AI
Professional styling with footer navigation and smooth transitions
"""

import streamlit as st

def apply_modern_styles():
    """Apply modern professional CSS styles with footer navigation"""
    st.markdown("""
    <style>
    /* Import professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Root variables for consistent theming */
    :root {
        --primary-color: #2563eb;
        --primary-dark: #1d4ed8;
        --secondary-color: #0f172a;
        --accent-color: #06b6d4;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --background-dark: #0f172a;
        --background-card: #1e293b;
        --background-card-hover: #334155;
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --border-color: #334155;
        --border-hover: #475569;
        --gradient-primary: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        --gradient-secondary: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        --gradient-accent: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    /* Global base styling */
    .main {
        background: var(--background-dark);
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu, footer, header, .stDeployButton {
        visibility: hidden !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--background-card);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-color);
        border-radius: 4px;
        transition: background 0.3s ease;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-dark);
    }
    
    /* Professional header styling */
    .professional-header {
        background: var(--gradient-secondary);
        padding: 2rem 0;
        border-radius: 0 0 24px 24px;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-xl);
        border-bottom: 1px solid var(--border-color);
        position: relative;
        overflow: hidden;
    }
    
    .professional-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--gradient-primary);
    }
    
    .professional-header h1 {
        color: var(--text-primary);
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        text-align: center;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .professional-header .subtitle {
        color: var(--text-secondary);
        font-size: 1.1rem;
        text-align: center;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Modern card styling */
    .modern-card {
        background: var(--background-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-lg);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .modern-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: var(--gradient-primary);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .modern-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl);
        border-color: var(--border-hover);
    }
    
    .modern-card:hover::before {
        opacity: 1;
    }
    
    .modern-card h3 {
        color: var(--text-primary);
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.25rem;
    }
    
    .modern-card p {
        color: var(--text-secondary);
        line-height: 1.6;
        margin-bottom: 0;
    }
    
    /* Modern button styling */
    .modern-btn {
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: var(--shadow-md) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .modern-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-xl) !important;
    }
    
    .modern-btn::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.2) 50%, transparent 100%);
        transition: left 0.6s ease;
    }
    
    .modern-btn:hover::before {
        left: 100%;
    }
    
    /* Professional metrics cards */
    .metric-card {
        background: var(--background-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--gradient-accent);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        border-color: var(--accent-color);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color);
        font-family: 'Poppins', sans-serif;
    }
    
    .metric-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
    }
    
    /* Footer Navigation - Modern Bottom Nav */
    .footer-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: var(--background-card);
        border-top: 1px solid var(--border-color);
        padding: 1rem 0;
        box-shadow: 0 -4px 6px -1px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        z-index: 1000;
    }
    
    .footer-nav-container {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.5rem;
        padding: 0 1rem;
    }
    
    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        transition: all 0.3s ease;
        cursor: pointer;
        text-decoration: none;
        color: var(--text-muted);
        min-width: 80px;
        position: relative;
        overflow: hidden;
    }
    
    .nav-item::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: var(--gradient-primary);
        opacity: 0;
        border-radius: 12px;
        transition: opacity 0.3s ease;
    }
    
    .nav-item:hover {
        color: var(--text-primary);
        background: var(--background-card-hover);
        transform: translateY(-2px);
    }
    
    .nav-item.active {
        color: var(--primary-color);
        background: rgba(37, 99, 235, 0.1);
        border: 1px solid rgba(37, 99, 235, 0.3);
    }
    
    .nav-item.active::before {
        opacity: 0.1;
    }
    
    .nav-icon {
        font-size: 1.2rem;
        margin-bottom: 0.25rem;
        position: relative;
        z-index: 1;
    }
    
    .nav-label {
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        position: relative;
        z-index: 1;
    }
    
    /* Content area with bottom padding for footer nav */
    .main-content {
        padding-bottom: 120px;
    }
    
    /* Feature grid for modern layout */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: var(--background-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 2rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--gradient-primary);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl);
        border-color: var(--primary-color);
    }
    
    .feature-card:hover::before {
        opacity: 1;
    }
    
    .feature-icon {
        font-size: 2.5rem;
        color: var(--primary-color);
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .feature-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        font-family: 'Poppins', sans-serif;
        text-align: center;
    }
    
    .feature-description {
        color: var(--text-secondary);
        line-height: 1.6;
        text-align: center;
    }
    
    /* Status indicators */
    .status-good {
        color: var(--success-color) !important;
        background: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
    }
    
    .status-warning {
        color: var(--warning-color) !important;
        background: rgba(245, 158, 11, 0.1) !important;
        border: 1px solid rgba(245, 158, 11, 0.3) !important;
    }
    
    .status-error {
        color: var(--error-color) !important;
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
    }
    
    /* Loading animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-pulse {
        animation: pulse 2s infinite;
    }
    
    .animate-slide-up {
        animation: slideInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Professional form styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: var(--background-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        padding: 0.75rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
        outline: none !important;
    }
    
    /* File upload styling */
    .stFileUploader > div {
        background: var(--background-card) !important;
        border: 2px dashed var(--border-color) !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--primary-color) !important;
        background: rgba(37, 99, 235, 0.05) !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .footer-nav-container {
            gap: 0.25rem;
            padding: 0 0.5rem;
        }
        
        .nav-item {
            min-width: 60px;
            padding: 0.5rem 0.5rem;
        }
        
        .nav-label {
            font-size: 0.65rem;
        }
        
        .nav-icon {
            font-size: 1rem;
        }
        
        .feature-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
        }
        
        .professional-header h1 {
            font-size: 2rem;
        }
    }
    
    /* Dark theme adjustments */
    .stMarkdown, .stText {
        color: var(--text-primary) !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, 
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: var(--text-primary) !important;
        font-family: 'Poppins', sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)

def create_footer_navigation(current_page="home"):
    """Create modern footer navigation"""
    
    nav_items = [
        {"id": "home", "icon": "🏠", "label": "Home", "page": "render_home"},
        {"id": "analyzer", "icon": "🔍", "label": "Analyzer", "page": "render_analyzer"},
        {"id": "radar", "icon": "⌖", "label": "Radar", "page": "render_resume_radar"},
        {"id": "builder", "icon": "📝", "label": "Builder", "page": "render_builder"},
        {"id": "dashboard", "icon": "📊", "label": "Dashboard", "page": "render_dashboard"},
        {"id": "jobs", "icon": "🎯", "label": "Jobs", "page": "render_job_search"},
        {"id": "feedback", "icon": "💬", "label": "Feedback", "page": "render_feedback_page"},
        {"id": "about", "icon": "ℹ️", "label": "About", "page": "render_about"}
    ]
    
    # Create navigation HTML
    nav_html = """
    <div class="footer-nav">
        <div class="footer-nav-container">
    """
    
    for item in nav_items:
        active_class = "active" if item["id"] == current_page else ""
        nav_html += f"""
        <div class="nav-item {active_class}" onclick="setPage('{item['id']}')">
            <div class="nav-icon">{item['icon']}</div>
            <div class="nav-label">{item['label']}</div>
        </div>
        """
    
    nav_html += """
        </div>
    </div>
    
    <script>
    function setPage(pageId) {
        // Map page IDs to Streamlit session state values
        const pageMapping = {
            'home': 'home',
            'analyzer': 'resume_analyzer',
            'radar': 'resume_radar',
            'builder': 'resume_builder',
            'dashboard': 'dashboard',
            'jobs': 'job_search',
            'feedback': 'feedback_page',
            'about': 'about'
        };
        
        // Send message to Streamlit to change page
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: pageMapping[pageId]
        }, '*');
    }
    </script>
    """
    
    st.markdown(nav_html, unsafe_allow_html=True)

def render_modern_header(title, subtitle=None):
    """Create professional header section"""
    header_html = f"""
    <div class="professional-header animate-slide-up">
        <h1>{title}</h1>
        {f'<div class="subtitle">{subtitle}</div>' if subtitle else ''}
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def create_modern_card(title, content, icon=None):
    """Create modern card component"""
    icon_html = f'<div class="feature-icon">{icon}</div>' if icon else ''
    
    card_html = f"""
    <div class="modern-card animate-slide-up">
        {icon_html}
        <h3>{title}</h3>
        <p>{content}</p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def create_metric_cards(metrics):
    """Create professional metric cards"""
    cols = st.columns(len(metrics))
    
    for i, metric in enumerate(metrics):
        with cols[i]:
            # Handle both tuple formats: (label, value) or (label, value, delta)
            if len(metric) == 2:
                label, value = metric
                delta = None
            else:
                label, value, delta = metric
                
            delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ''
            
            metric_html = f"""
            <div class="metric-card animate-slide-up">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
                {delta_html}
            </div>
            """
            st.markdown(metric_html, unsafe_allow_html=True)

def create_feature_grid(features):
    """Create feature grid layout"""
    st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
    
    cols = st.columns(min(len(features), 3))  # Max 3 columns
    
    for i, feature in enumerate(features):
        col_index = i % len(cols)
        with cols[col_index]:
            create_modern_card(
                feature.get('title', ''),
                feature.get('description', ''),
                feature.get('icon', '')
            )
    
    st.markdown('</div>', unsafe_allow_html=True)


class FooterNavigation:
    """Modern footer navigation component with clean integration"""
    
    def __init__(self):
        self.navigation_items = [
            {"key": "home", "label": "Home", "icon": "🏠"},
            {"key": "analyzer", "label": "Analyzer", "icon": "🔍"},
            {"key": "radar", "label": "Radar", "icon": "⌖"},
            {"key": "placement", "label": "Placement", "icon": "🎯"},
            {"key": "builder", "label": "Builder", "icon": "📝"},
            {"key": "dashboard", "label": "Dashboard", "icon": "📊"},
            {"key": "job-search", "label": "Jobs", "icon": "💼"},
            {"key": "about", "label": "About", "icon": "ℹ️"}
        ]
    
    def get_current_page(self) -> str:
        """Get the currently selected page"""
        if 'footer_nav_page' not in st.session_state:
            st.session_state.footer_nav_page = 'home'
        return st.session_state.footer_nav_page
    
    def set_current_page(self, page: str):
        """Set the currently selected page"""
        st.session_state.footer_nav_page = page
    
    def render(self):
        """Render the footer navigation using Streamlit columns"""
        current_page = self.get_current_page()
        
        # Create the footer navigation container
        st.markdown("""
        <div style="
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--background-card);
            border-top: 1px solid var(--border-color);
            padding: 0.75rem 0;
            box-shadow: 0 -4px 6px -1px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            z-index: 1000;
        ">
        </div>
        """, unsafe_allow_html=True)
        
        # Use Streamlit columns for navigation buttons
        with st.container():
            st.markdown('<div style="position: fixed; bottom: 0; left: 0; right: 0; background: rgba(30, 30, 30, 0.95); padding: 1rem 0; z-index: 1000; border-top: 1px solid var(--border-color);">', unsafe_allow_html=True)
            
            # Center the navigation
            col_left, nav_col, col_right = st.columns([1, 6, 1])
            
            with nav_col:
                # Create columns for each navigation item
                nav_cols = st.columns(len(self.navigation_items))
                
                for i, item in enumerate(self.navigation_items):
                    with nav_cols[i]:
                        # Use button type based on current page
                        button_type = "primary" if item["key"] == current_page else "secondary"
                        
                        if st.button(
                            f"{item['icon']} {item['label']}", 
                            key=f"footer_nav_{item['key']}", 
                            help=f"Navigate to {item['label']} page",
                            type=button_type,
                            use_container_width=True
                        ):
                            self.set_current_page(item["key"])
                            st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)


def feature_card(icon: str, title: str, description: str):
    """Render a feature card component"""
    st.markdown(f"""
    <div class="feature-card animate-slide-up">
        <div class="feature-icon">{icon}</div>
        <div class="feature-title">{title}</div>
        <div class="feature-description">{description}</div>
    </div>
    """, unsafe_allow_html=True)


def hero_section(title: str, description: str):
    """Render a hero section with call-to-action"""
    render_modern_header(title, description)
