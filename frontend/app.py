import streamlit as st
import requests
from datetime import datetime
from typing import Dict, List

st.set_page_config(
    page_title="FinGuard AI Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://localhost:8000"
NAMESPACES = {
    "general": "General Information",
    "finance": "Financial Data",
    "hr": "Human Resources", 
    "marketing": "Marketing & Sales",
    "engineering": "Engineering & Tech"
}

USER_ROLES = {
    "finance": "Finance Team",
    "marketing": "Marketing Team", 
    "hr": "HR Team",
    "engineering": "Engineering Team",
    "c_level": "C-Level Executive",
    "employee": "General Employee"
}

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .login-container {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        margin: 2rem auto;
        max-width: 950px;
        border: 3px solid rgba(59, 130, 246, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .login-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #3b82f6, #10b981, #8b5cf6, #3b82f6);
        background-size: 200% 100%;
        animation: gradientShift 3s ease-in-out infinite;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-title {
        font-size: 2rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .login-subtitle {
        color: #7f8c8d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .demo-credentials {
        background: rgba(255,255,255,0.98);
        padding: 2.5rem;
        border-radius: 18px;
        margin-bottom: 2rem;
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
        border: 3px solid rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(20px);
        position: relative;
    }
    
    .demo-credentials::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #3b82f6, #10b981, #8b5cf6, #3b82f6);
        border-radius: 18px 18px 0 0;
        background-size: 200% 100%;
        animation: gradientShift 3s ease-in-out infinite;
    }
    
    .demo-title {
        color: #2c3e50;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .credential-card {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #10b981 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 0.5rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
        transition: all 0.3s ease;
        border: 3px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(15px);
        position: relative;
        overflow: hidden;
    }
    
    .credential-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #fff, transparent, #fff);
        opacity: 0.6;
    }
    
    .credential-card:hover {
        transform: translateY(-5px) scale(1.03);
        box-shadow: 0 15px 40px rgba(59, 130, 246, 0.5);
        border-color: rgba(255, 255, 255, 0.5);
    }
    
    .credential-role {
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .credential-info {
        font-size: 0.85rem;
        opacity: 0.9;
    }
    
    .login-form {
        background: rgba(255,255,255,0.98);
        padding: 2.5rem;
        border-radius: 18px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
        border: 3px solid rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(20px);
        position: relative;
    }
    
    .login-form::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #10b981, #8b5cf6);
        border-radius: 18px 18px 0 0;
    }
    
    .quick-login-section {
        background: rgba(255,255,255,0.98);
        padding: 2rem;
        border-radius: 16px;
        border: 3px solid rgba(16, 185, 129, 0.3);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.15);
        backdrop-filter: blur(15px);
        position: relative;
    }
    
    .quick-login-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #10b981, #3b82f6, #10b981);
        border-radius: 16px 16px 0 0;
        background-size: 200% 100%;
        animation: gradientShift 3s ease-in-out infinite;
    }
    
    .quick-login-title {
        color: #2c3e50;
        font-weight: 600;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        border-color: rgba(255, 255, 255, 0.3);
    }
    
    .main-login-btn {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        font-size: 1.2rem !important;
        padding: 1rem 2.5rem !important;
        border-radius: 12px !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    .chat-message {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border: 2px solid transparent;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        position: relative;
    }
    
    .user-message {
        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
        border-color: #3b82f6;
        margin-left: 2rem;
    }
    
    .user-message::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #1d4ed8);
        border-radius: 15px 15px 0 0;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        border-color: #10b981;
        margin-right: 2rem;
    }
    
    .assistant-message::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #10b981, #059669);
        border-radius: 15px 15px 0 0;
    }
    
    .role-badge {
        background-color: #1f77b4;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .namespace-badge {
        background-color: #4caf50;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 3px solid #e2e8f0;
        padding: 1rem;
        transition: all 0.3s ease;
        background: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
        background: rgba(255, 255, 255, 1);
        transform: translateY(-1px);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #9ca3af;
        font-style: italic;
    }
    
    /* Chat Interface Styling */
    .chat-container {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 2px solid rgba(59, 130, 246, 0.2);
        position: relative;
    }
    
    .chat-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #10b981, #8b5cf6, #3b82f6);
        border-radius: 20px 20px 0 0;
        background-size: 200% 100%;
        animation: gradientShift 3s ease-in-out infinite;
    }
    
    .chat-header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: rgba(255,255,255,0.8);
        border-radius: 15px;
        border: 2px solid rgba(59, 130, 246, 0.1);
    }
    
    .chat-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .thinking-indicator {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        border: 2px solid #f59e0b;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
        color: #92400e;
        font-weight: 500;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .chat-input-container {
        background: rgba(255,255,255,0.95);
        padding: 2rem;
        border-radius: 18px;
        border: 3px solid rgba(59, 130, 246, 0.2);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin-top: 2rem;
        position: relative;
    }
    
    .chat-input-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #10b981, #3b82f6, #10b981);
        border-radius: 18px 18px 0 0;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 3px solid #e2e8f0;
        padding: 1rem;
        transition: all 0.3s ease;
        background: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        resize: none;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
        background: rgba(255, 255, 255, 1);
        transform: translateY(-1px);
    }
    
    .send-button {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .send-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "demo_credentials" not in st.session_state:
    st.session_state.demo_credentials = None

def make_api_request(endpoint: str, method: str = "GET", data: Dict = None, auth_required: bool = True) -> Dict:
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if auth_required and st.session_state.access_token:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    
    try:
        if method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.get(url, headers=headers)
        
        if response.status_code == 401:
            st.session_state.authenticated = False
            st.session_state.access_token = None
            st.session_state.user_info = None
            st.error("Session expired. Please login again.")
            st.rerun()
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to FinGuard API. Please ensure the backend server is running on http://localhost:8000")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API Error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None

def login_user(username: str, password: str) -> bool:
    data = {"username": username, "password": password}
    response = make_api_request("/auth/login", "POST", data, auth_required=False)
    
    if response:
        st.session_state.access_token = response["access_token"]
        st.session_state.authenticated = True
        
        user_info = make_api_request("/auth/me")
        if user_info:
            st.session_state.user_info = user_info
            return True
    
    return False

def logout_user():
    st.session_state.authenticated = False
    st.session_state.access_token = None
    st.session_state.user_info = None
    st.session_state.chat_history = []
    st.rerun()

def get_demo_credentials():
    if not st.session_state.demo_credentials:
        response = make_api_request("/auth/demo-credentials", auth_required=False)
        if response and isinstance(response, dict):
            credentials = response.get("credentials", [])
            if isinstance(credentials, list):
                st.session_state.demo_credentials = credentials
            else:
                st.session_state.demo_credentials = []
        else:
            st.session_state.demo_credentials = []
    
    if not isinstance(st.session_state.demo_credentials, list):
        st.session_state.demo_credentials = []
    
    return st.session_state.demo_credentials

def send_chat_message(query: str, namespace: str) -> Dict:
    data = {"query": query, "namespace": namespace}
    return make_api_request("/chat/query", "POST", data)

def check_api_health() -> bool:
    if not st.session_state.authenticated:
        return False
    
    response = make_api_request("/chat/health")
    return response is not None and response.get("status") == "healthy"

def render_chat_message(message: Dict, is_user: bool = False):
    if is_user:
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 You:</strong><br>
            {message['content']}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 FinGuard AI:</strong><br>
            {message['answer']}
        </div>
        """, unsafe_allow_html=True)
        

def main():
    st.markdown('<h1 class="main-header">🏦 FinGuard AI Assistant</h1>', unsafe_allow_html=True)
    
    if not st.session_state.authenticated:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="login-header">
            <div class="login-title">🔐 Welcome to FinGuard</div>
            <div class="login-subtitle">Enterprise Role-Based AI-Assistant</div>
        </div>
        """, unsafe_allow_html=True)
        
        demo_creds = get_demo_credentials()
        if demo_creds and isinstance(demo_creds, list):
            st.markdown('<div class="demo-credentials">', unsafe_allow_html=True)
            st.markdown('<div class="demo-title">🎯 Available Demo Accounts</div>', unsafe_allow_html=True)
            
            num_creds = len(demo_creds)
            if num_creds <= 3:
                cols = st.columns(num_creds)
            else:
                cols = st.columns(3)
                
            for i, cred in enumerate(demo_creds):
                col_index = i % len(cols)
                with cols[col_index]:
                    if isinstance(cred, dict):
                        role = cred.get('role', 'Unknown')
                        username = cred.get('username', 'N/A')
                        password = cred.get('password', 'N/A')
                    else:
                        role = str(cred)
                        username = 'N/A'
                        password = 'N/A'
                    
                    st.markdown(f"""
                    <div class="credential-card">
                        <div class="credential-role">{role.replace('_', ' ').title()}</div>
                        <div class="credential-info">
                            <strong>Username:</strong> {username}<br>
                            <strong>Password:</strong> {password}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        
        with st.form("login_form"):
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.markdown("#### 📝 Enter Your Credentials")
                username = st.text_input(
                    "Username", 
                    placeholder="Enter your username",
                    help="Use one of the demo accounts above"
                )
                password = st.text_input(
                    "Password", 
                    type="password", 
                    placeholder="Enter your password",
                    help="Password for the selected demo account"
                )
            
            with col2:
                st.markdown('<div class="quick-login-section">', unsafe_allow_html=True)
                
                st.markdown("""
                <div style="text-align: center; margin-bottom: 1.5rem;">
                    <h4 style="color: #2c3e50; margin-bottom: 0.5rem;">🏦 About FinGuard</h4>
                    <p style="color: #7f8c8d; font-size: 0.9rem; line-height: 1.4; margin-bottom: 1rem;">
                        FinGuard is an AI-powered financial intelligence platform that provides 
                        secure, role-based access to financial data and insights. Experience 
                        advanced analytics with enterprise-grade security.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="quick-login-title">⚡ Quick Login</div>', unsafe_allow_html=True)
                st.markdown('<p style="text-align: center; color: #7f8c8d; font-size: 0.85rem; margin-bottom: 1rem;">Click to instantly login with demo accounts</p>', unsafe_allow_html=True)
                
                if demo_creds and isinstance(demo_creds, list):
                    creds_to_show = demo_creds[:4] if len(demo_creds) > 4 else demo_creds
                    for cred in creds_to_show:
                        if isinstance(cred, dict):
                            role = cred.get('role', 'Unknown')
                            cred_username = cred.get('username', '')
                            cred_password = cred.get('password', '')
                            
                            role_emojis = {
                                'c_level': '👑',
                                'finance': '💰',
                                'marketing': '📈',
                                'hr': '👥',
                                'engineering': '⚙️',
                                'employee': '👤'
                            }
                            emoji = role_emojis.get(role, '👤')
                            
                            if st.form_submit_button(
                                f"{emoji} {role.replace('_', ' ').title()}", 
                                use_container_width=True
                            ):
                                username = cred_username
                                password = cred_password
                else:
                    st.markdown('<p style="text-align: center; color: #e74c3c; font-size: 0.9rem;">Demo accounts loading...</p>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            col_center = st.columns([1, 2, 1])
            with col_center[1]:
                submitted = st.form_submit_button(
                    "🚀 Sign In to FinGuard", 
                    use_container_width=True,
                    help="Click to authenticate and access the platform"
                )
            
            if submitted and username and password:
                with st.spinner("🔐 Authenticating your credentials..."):
                    if login_user(username, password):
                        st.success("✅ Authentication successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Please check your username and password.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-top: 2rem; color: #7f8c8d;">
            <small>
                🔒 This is a secure demo environment. All data is simulated for demonstration purposes.<br>
                💡 Try different user roles to see how access controls work across departments.
            </small>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        user_info = st.session_state.user_info
        
        with st.sidebar:
            st.markdown("### 👤 User Information")
            st.markdown(f"""
            **Name:** {user_info.get('full_name', user_info['username'])}  
            **Username:** {user_info['username']}  
            **Role:** <span class="role-badge">{USER_ROLES.get(user_info['role'], user_info['role'])}</span>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("### 🎯 Query Namespace")
            selected_namespace = st.selectbox(
                "Select data source:",
                options=list(NAMESPACES.keys()),
                format_func=lambda x: NAMESPACES[x],
                index=0
            )
            
            st.markdown("---")
            
            st.markdown("### 📊 System Status")
            if check_api_health():
                st.success("🟢 System Healthy")
            else:
                st.error("🔴 System Issues")
            
            st.markdown("---")
            
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
            
            if st.button("🚪 Logout", use_container_width=True):
                logout_user()
        
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="chat-header">
            <div class="chat-title">💬 Chat with FinGuard AI</div>
            <span class="namespace-badge">Current Namespace: {NAMESPACES[selected_namespace]}</span>
        </div>
        """, unsafe_allow_html=True)
        
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message['type'] == 'user':
                    render_chat_message(message, is_user=True)
                else:
                    render_chat_message(message, is_user=False)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if "is_thinking" not in st.session_state:
            st.session_state.is_thinking = False
        
        if st.session_state.is_thinking:
            st.markdown("""
            <div class="thinking-indicator">
                🤖 FinGuard AI is analyzing your request and searching through relevant data...
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
        
        with st.form("chat_form", clear_on_submit=True):
            st.markdown("### 💭 Ask FinGuard AI")
            
            user_query = st.text_area(
                "Type your question here...",
                placeholder="e.g., What is our current quarterly budget allocation for marketing expenses?",
                height=120,
                key="chat_input",
                help="Ask anything about your company's data based on your role permissions"
            )
            
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                send_button = st.form_submit_button(
                    "🚀 Send Message", 
                    use_container_width=True,
                    help="Send your question to FinGuard AI"
                )
            
            if send_button and user_query.strip():
                st.session_state.is_thinking = True
                
                user_message = {
                    'type': 'user',
                    'content': user_query,
                    'timestamp': datetime.now().isoformat(),
                    'namespace': selected_namespace
                }
                st.session_state.chat_history.append(user_message)
                
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.is_thinking and len(st.session_state.chat_history) > 0:
            last_message = st.session_state.chat_history[-1]
            if last_message['type'] == 'user':
                response = send_chat_message(last_message['content'], selected_namespace)
                
                if response:
                    assistant_message = {
                        'type': 'assistant',
                        'answer': response['answer'],
                        'timestamp': datetime.now().isoformat()
                    }
                    st.session_state.chat_history.append(assistant_message)
                else:
                    error_message = {
                        'type': 'assistant',
                        'answer': "❌ Sorry, I encountered an error processing your request. Please try again.",
                        'timestamp': datetime.now().isoformat()
                    }
                    st.session_state.chat_history.append(error_message)
                
                st.session_state.is_thinking = False
                st.rerun()
        
        st.markdown("---")
        st.markdown("""
        <div class="info-box">
            <strong>🔒 Role-Based Access:</strong> Your queries are processed based on your role permissions. 
            The AI will only access data you're authorized to view.<br>
            <strong>🛠️ Agentic AI:</strong> This system uses advanced agentic tools to intelligently search and analyze data.
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()