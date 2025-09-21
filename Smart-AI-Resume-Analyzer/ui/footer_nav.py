"""
Footer Navigation Component for Smart Resume AI
Modern, responsive bottom navigation bar
"""

import streamlit as st

class FooterNavigation:
    def __init__(self):
        self.nav_items = [
            {"id": "home", "icon": "🏠", "label": "Home", "key": "home"},
            {"id": "analyzer", "icon": "🔍", "label": "Analyzer", "key": "resume_analyzer"},
            {"id": "radar", "icon": "⌖", "label": "Radar", "key": "resume_radar"},
            {"id": "builder", "icon": "📝", "label": "Builder", "key": "resume_builder"},
            {"id": "dashboard", "icon": "📊", "label": "Dashboard", "key": "dashboard"},
            {"id": "jobs", "icon": "🎯", "label": "Jobs", "key": "job_search"},
            {"id": "feedback", "icon": "💬", "label": "Feedback", "key": "feedback_page"},
            {"id": "about", "icon": "ℹ️", "label": "About", "key": "about"}
        ]
    
    def render(self, current_page="home"):
        """Render the footer navigation"""
        
        # Create navigation buttons in the footer
        st.markdown("""
        <div class="footer-nav">
            <div class="footer-nav-container">
        """, unsafe_allow_html=True)
        
        # Create columns for navigation items
        cols = st.columns(len(self.nav_items))
        
        for i, item in enumerate(self.nav_items):
            with cols[i]:
                # Determine if this is the active page
                active_class = "active" if item["key"] == current_page else ""
                
                # Create clickable navigation item
                if st.button(
                    f"{item['icon']}\n{item['label']}", 
                    key=f"nav_{item['id']}",
                    help=f"Navigate to {item['label']}",
                    use_container_width=True
                ):
                    st.session_state.page = item["key"]
                    st.rerun()
        
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add spacing for fixed footer
        st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)

def create_floating_nav_buttons():
    """Create floating navigation buttons as an alternative"""
    
    # Create floating navigation in sidebar
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        
        nav_items = [
            ("🏠 Home", "home"),
            ("🔍 Resume Analyzer", "resume_analyzer"),
            ("⌖ Resume Radar", "resume_radar"),
            ("📝 Resume Builder", "resume_builder"),
            ("📊 Dashboard", "dashboard"),
            ("🎯 Job Search", "job_search"),
            ("💬 Feedback", "feedback_page"),
            ("ℹ️ About", "about")
        ]
        
        for label, key in nav_items:
            if st.button(label, use_container_width=True, key=f"sidebar_nav_{key}"):
                st.session_state.page = key
                st.rerun()

def create_bottom_navigation_with_js():
    """Create bottom navigation with JavaScript for better interactivity"""
    
    nav_html = """
    <style>
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(30, 41, 59, 0.95);
        backdrop-filter: blur(20px);
        border-top: 1px solid #334155;
        padding: 0.75rem 0;
        box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.12);
        z-index: 1000;
    }
    
    .bottom-nav-container {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 0 1rem;
    }
    
    .bottom-nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0.5rem;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        text-decoration: none;
        color: #94a3b8;
        min-width: 70px;
        position: relative;
        overflow: hidden;
    }
    
    .bottom-nav-item::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        opacity: 0;
        border-radius: 12px;
        transition: opacity 0.3s ease;
        z-index: -1;
    }
    
    .bottom-nav-item:hover {
        color: #f8fafc;
        transform: translateY(-2px);
    }
    
    .bottom-nav-item:hover::before {
        opacity: 0.1;
    }
    
    .bottom-nav-item.active {
        color: #2563eb;
        background: rgba(37, 99, 235, 0.1);
        border: 1px solid rgba(37, 99, 235, 0.3);
    }
    
    .bottom-nav-icon {
        font-size: 1.25rem;
        margin-bottom: 0.25rem;
        position: relative;
        z-index: 1;
    }
    
    .bottom-nav-label {
        font-size: 0.7rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        position: relative;
        z-index: 1;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .bottom-nav-container {
            padding: 0 0.5rem;
        }
        
        .bottom-nav-item {
            min-width: 60px;
            padding: 0.4rem 0.2rem;
        }
        
        .bottom-nav-label {
            font-size: 0.65rem;
        }
        
        .bottom-nav-icon {
            font-size: 1.1rem;
        }
    }
    </style>
    
    <div class="bottom-nav">
        <div class="bottom-nav-container">
            <div class="bottom-nav-item" onclick="navigateTo('home')" id="nav-home">
                <div class="bottom-nav-icon">🏠</div>
                <div class="bottom-nav-label">Home</div>
            </div>
            <div class="bottom-nav-item" onclick="navigateTo('resume_analyzer')" id="nav-analyzer">
                <div class="bottom-nav-icon">🔍</div>
                <div class="bottom-nav-label">Analyzer</div>
            </div>
            <div class="bottom-nav-item" onclick="navigateTo('resume_radar')" id="nav-radar">
                <div class="bottom-nav-icon">⌖</div>
                <div class="bottom-nav-label">Radar</div>
            </div>
            <div class="bottom-nav-item" onclick="navigateTo('resume_builder')" id="nav-builder">
                <div class="bottom-nav-icon">📝</div>
                <div class="bottom-nav-label">Builder</div>
            </div>
            <div class="bottom-nav-item" onclick="navigateTo('dashboard')" id="nav-dashboard">
                <div class="bottom-nav-icon">📊</div>
                <div class="bottom-nav-label">Dashboard</div>
            </div>
            <div class="bottom-nav-item" onclick="navigateTo('job_search')" id="nav-jobs">
                <div class="bottom-nav-icon">🎯</div>
                <div class="bottom-nav-label">Jobs</div>
            </div>
            <div class="bottom-nav-item" onclick="navigateTo('feedback_page')" id="nav-feedback">
                <div class="bottom-nav-icon">💬</div>
                <div class="bottom-nav-label">Feedback</div>
            </div>
            <div class="bottom-nav-item" onclick="navigateTo('about')" id="nav-about">
                <div class="bottom-nav-icon">ℹ️</div>
                <div class="bottom-nav-label">About</div>
            </div>
        </div>
    </div>
    
    <script>
    function navigateTo(page) {
        // Update URL fragment to trigger page change
        window.location.hash = page;
        
        // Update active state
        document.querySelectorAll('.bottom-nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to clicked item
        const activeItem = document.getElementById('nav-' + page.replace('_', '-').replace('resume-', '').replace('page', 'feedback').replace('search', 'jobs'));
        if (activeItem) {
            activeItem.classList.add('active');
        }
        
        // Trigger Streamlit rerun by setting session state
        const event = new CustomEvent('streamlit:navChange', { 
            detail: { page: page }
        });
        window.dispatchEvent(event);
    }
    
    // Set initial active state based on current page
    function setActiveNav(currentPage) {
        document.querySelectorAll('.bottom-nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const pageMap = {
            'home': 'nav-home',
            'resume_analyzer': 'nav-analyzer', 
            'resume_radar': 'nav-radar',
            'resume_builder': 'nav-builder',
            'dashboard': 'nav-dashboard',
            'job_search': 'nav-jobs',
            'feedback_page': 'nav-feedback',
            'about': 'nav-about'
        };
        
        const activeId = pageMap[currentPage];
        if (activeId) {
            const activeItem = document.getElementById(activeId);
            if (activeItem) {
                activeItem.classList.add('active');
            }
        }
    }
    
    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        // You can set the initial page here if needed
        setActiveNav('home');
    });
    </script>
    """
    
    st.markdown(nav_html, unsafe_allow_html=True)
    
    # Add bottom padding to prevent content from being hidden
    st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)