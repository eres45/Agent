import os
import base64
import time
import json
import requests
import re
import logging
import threading
import sqlite3
import csv
import random
import string
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import (
    TimeoutException, ElementClickInterceptedException, 
    ElementNotInteractableException, NoSuchElementException,
    StaleElementReferenceException, WebDriverException,
    JavascriptException, InvalidSessionIdException
)
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import asyncio
import numpy as np
import cv2
import pickle
import yaml
import pandas as pd
import openpyxl
from urllib.parse import urlparse, parse_qs, urlencode
import subprocess
import platform
import psutil
import tempfile
import zipfile
import shutil
from pathlib import Path
import mimetypes
import websocket
import schedule
from functools import wraps, lru_cache
from collections import defaultdict, deque
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Setup advanced logging
os.makedirs('logs', exist_ok=True)
os.makedirs('screenshots', exist_ok=True)
os.makedirs('downloads', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('reports', exist_ok=True)

# Configure advanced logging with multiple handlers
log_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)

# File handler
file_handler = logging.FileHandler('logs/mega_browser_agent.log', encoding='utf-8')
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
console_handler.setLevel(logging.INFO)

# Error handler (separate file for errors)
error_handler = logging.FileHandler('logs/errors.log', encoding='utf-8')
error_handler.setFormatter(log_formatter)
error_handler.setLevel(logging.ERROR)

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.addHandler(error_handler)

# AI Configuration - Multi-Model Support
AI_CONFIGS = {
    "mistral": {
        "api_key": os.getenv("MISTRAL_API_KEY", ""),
        "endpoint": "https://api.mistral.ai/v1/chat/completions",
        "model": "mistral-large-latest"
    },
    "typegpt": {
        "api_key": os.getenv("TYPEGPT_API_KEY", ""),
        "endpoint": "https://api.example.com/v1/chat/completions",
        "model": "model-name"
    },
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-4-turbo-preview"
    },
    "anthropic": {
        "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "endpoint": "https://api.anthropic.com/v1/messages",
        "model": "claude-3-opus-20240229"
    },
    "gemini": {
        "api_key": os.getenv("GEMINI_API_KEY", ""),
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
        "model": "gemini-pro"
    }
}

# Default AI provider
DEFAULT_AI_PROVIDER = "mistral"
API_KEY = AI_CONFIGS[DEFAULT_AI_PROVIDER]["api_key"]
API_ENDPOINT_URL = AI_CONFIGS[DEFAULT_AI_PROVIDER]["endpoint"]
MODEL_NAME = AI_CONFIGS[DEFAULT_AI_PROVIDER]["model"]

if not API_KEY or not API_ENDPOINT_URL:
    logger.warning("Primary AI API key or base URL not found. Some AI features may be limited.")

@dataclass
class ElementInfo:
    """Advanced element information structure."""
    id: int
    element: Any
    tag_name: str
    label: str
    element_type: str
    is_visible: bool
    is_clickable: bool
    is_form_field: bool
    coordinates: Tuple[int, int, int, int]  # x, y, width, height
    attributes: Dict[str, str]
    text_content: str
    confidence_score: float

@dataclass
class ActionResult:
    """Advanced action result structure."""
    success: bool
    action_type: str
    message: str
    duration: float
    screenshot_path: Optional[str]
    element_id: Optional[int]
    error_details: Optional[str]
    timestamp: datetime
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AutomationTask:
    """Structure for automation tasks."""
    name: str
    steps: List[Dict[str, Any]]
    conditions: Dict[str, Any] = field(default_factory=dict)
    loops: int = 1
    delay_between_loops: float = 0
    on_error: str = "stop"  # stop, continue, retry
    max_retries: int = 3
    timeout: float = 300
    
@dataclass
class NetworkRequest:
    """Structure for network request monitoring."""
    url: str
    method: str
    status_code: int
    response_time: float
    headers: Dict[str, str]
    body: Optional[str]
    timestamp: datetime
    
@dataclass
class PerformanceMetrics:
    """Performance tracking structure."""
    page_load_time: float
    dom_ready_time: float
    first_paint_time: float
    memory_usage: float
    cpu_usage: float
    network_requests_count: int
    javascript_errors: List[str]
    timestamp: datetime

class CaptchaSolver:
    """Advanced CAPTCHA solving capabilities."""
    
    def __init__(self):
        self.providers = {
            "2captcha": os.getenv("TWOCAPTCHA_API_KEY", ""),
            "anticaptcha": os.getenv("ANTICAPTCHA_API_KEY", ""),
            "capsolver": os.getenv("CAPSOLVER_API_KEY", "")
        }
        
    def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve reCAPTCHA v2."""
        if self.providers.get("2captcha"):
            try:
                # Implementation for 2captcha
                api_key = self.providers["2captcha"]
                solver_url = f"http://2captcha.com/in.php?key={api_key}&method=userrecaptcha&googlekey={site_key}&pageurl={page_url}"
                response = requests.get(solver_url)
                if "OK" in response.text:
                    captcha_id = response.text.split("|")[1]
                    time.sleep(20)  # Wait for solving
                    result_url = f"http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}"
                    for _ in range(10):
                        result = requests.get(result_url)
                        if "OK" in result.text:
                            return result.text.split("|")[1]
                        time.sleep(5)
            except Exception as e:
                logger.error(f"CAPTCHA solving failed: {e}")
        return None
    
    def solve_image_captcha(self, image_path: str) -> Optional[str]:
        """Solve image-based CAPTCHA using OCR."""
        try:
            import pytesseract
            from PIL import Image
            
            img = Image.open(image_path)
            # Preprocess image for better OCR
            img = img.convert('L')  # Convert to grayscale
            img = ImageEnhance.Contrast(img).enhance(2)
            
            text = pytesseract.image_to_string(img, config='--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            return text.strip()
        except Exception as e:
            logger.error(f"Image CAPTCHA solving failed: {e}")
            return None

class NetworkInterceptor:
    """Advanced network request interception and modification."""
    
    def __init__(self, driver):
        self.driver = driver
        self.requests_log = []
        self.blocked_urls = []
        self.modified_headers = {}
        
    def enable_network_logging(self):
        """Enable Chrome DevTools Protocol for network monitoring."""
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        
    def intercept_requests(self, url_pattern: str = None, callback: Callable = None):
        """Intercept and optionally modify network requests."""
        script = """
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            console.log('Fetch intercepted:', args[0]);
            if (window.interceptCallback) {
                args = window.interceptCallback(args);
            }
            return originalFetch.apply(this, args);
        };
        
        const originalXHR = window.XMLHttpRequest.prototype.open;
        window.XMLHttpRequest.prototype.open = function(method, url, ...rest) {
            console.log('XHR intercepted:', method, url);
            if (window.interceptCallback) {
                [method, url] = window.interceptCallback([method, url]);
            }
            return originalXHR.apply(this, [method, url, ...rest]);
        };
        """
        self.driver.execute_script(script)
        
    def block_requests(self, patterns: List[str]):
        """Block requests matching patterns."""
        self.blocked_urls = patterns
        block_script = f"""
        window.blockedPatterns = {json.dumps(patterns)};
        const originalFetch = window.fetch;
        window.fetch = function(url, ...args) {{
            for (let pattern of window.blockedPatterns) {{
                if (url.includes(pattern)) {{
                    console.log('Blocked request:', url);
                    return Promise.reject(new Error('Request blocked'));
                }}
            }}
            return originalFetch.apply(this, [url, ...args]);
        }};
        """
        self.driver.execute_script(block_script)
        
    def get_network_logs(self) -> List[NetworkRequest]:
        """Get all network requests from browser logs."""
        logs = self.driver.get_log('performance')
        requests = []
        
        for entry in logs:
            log = json.loads(entry['message'])['message']
            if 'Network.responseReceived' in log['method']:
                response = log['params']['response']
                requests.append(NetworkRequest(
                    url=response['url'],
                    method=response.get('requestMethod', 'GET'),
                    status_code=response['status'],
                    response_time=0,  # Would need timing info
                    headers=response['headers'],
                    body=None,
                    timestamp=datetime.now()
                ))
        
        return requests

class AdvancedDatabase:
    """Advanced database manager for browser agent."""
    
    def __init__(self, db_path: str = "data/browser_agent.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with all necessary tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Actions history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actions_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    url TEXT,
                    element_id INTEGER,
                    parameters TEXT,
                    result TEXT,
                    duration REAL,
                    screenshot_path TEXT,
                    success BOOLEAN
                )
            ''')
            
            # Website data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS website_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT,
                    description TEXT,
                    keywords TEXT,
                    elements_count INTEGER,
                    load_time REAL,
                    screenshot_path TEXT,
                    visit_timestamp TEXT
                )
            ''')
            
            # Form data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS form_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    form_name TEXT,
                    field_name TEXT,
                    field_value TEXT,
                    field_type TEXT,
                    timestamp TEXT
                )
            ''')
            
            # Search results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_engine TEXT,
                    query TEXT,
                    results_count INTEGER,
                    top_result_title TEXT,
                    top_result_url TEXT,
                    timestamp TEXT
                )
            ''')
            
            conn.commit()
    
    def log_action(self, action_result: ActionResult):
        """Log action to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO actions_history 
                (timestamp, action_type, element_id, result, duration, screenshot_path, success)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                action_result.timestamp.isoformat(),
                action_result.action_type,
                action_result.element_id,
                action_result.message,
                action_result.duration,
                action_result.screenshot_path,
                action_result.success
            ))
            conn.commit()

class AdvancedEmailManager:
    """Advanced email management system."""
    
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
    def send_report(self, to_email: str, subject: str, body: str, attachments: List[str] = None):
        """Send email report with attachments."""
        try:
            msg = MIMEMultipart()
            msg['From'] = os.getenv('EMAIL_FROM', 'browser.agent@example.com')
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}',
                        )
                        msg.attach(part)
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(
                os.getenv('EMAIL_USERNAME', ''), 
                os.getenv('EMAIL_PASSWORD', '')
            )
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email report sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

class AdvancedReportGenerator:
    """Advanced report generation system."""
    
    def __init__(self, db: AdvancedDatabase):
        self.db = db
        
    def generate_html_report(self, session_data: Dict) -> str:
        """Generate comprehensive HTML report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"reports/session_report_{timestamp}.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Browser Agent Session Report</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .header h1 {{ color: #333; margin-bottom: 10px; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .stat-card h3 {{ margin: 0 0 10px 0; }}
                .stat-card .number {{ font-size: 2em; font-weight: bold; }}
                .timeline {{ margin-top: 30px; }}
                .timeline-item {{ background: #f8f9fa; margin: 10px 0; padding: 15px; border-left: 4px solid #667eea; border-radius: 5px; }}
                .success {{ border-left-color: #28a745; }}
                .error {{ border-left-color: #dc3545; }}
                .screenshot {{ max-width: 300px; border-radius: 5px; margin: 10px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 Browser Agent Session Report</h1>
                    <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <h3>Total Actions</h3>
                        <div class="number">{session_data.get('total_actions', 0)}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Success Rate</h3>
                        <div class="number">{session_data.get('success_rate', 0)}%</div>
                    </div>
                    <div class="stat-card">
                        <h3>Websites Visited</h3>
                        <div class="number">{session_data.get('websites_visited', 0)}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Total Duration</h3>
                        <div class="number">{session_data.get('total_duration', 0):.1f}s</div>
                    </div>
                </div>
                
                <div class="timeline">
                    <h2>Action Timeline</h2>
                    {self._generate_timeline_html(session_data.get('actions', []))}
                </div>
                
                <div class="footer">
                    <p>Generated by Mega Advanced Browser Agent v2.0</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {report_path}")
        return report_path
    
    def _generate_timeline_html(self, actions: List[ActionResult]) -> str:
        """Generate timeline HTML for actions."""
        timeline_html = ""
        for action in actions:
            status_class = "success" if action.success else "error"
            timeline_html += f"""
            <div class="timeline-item {status_class}">
                <strong>{action.action_type}</strong> - {action.message}
                <br><small>{action.timestamp.strftime("%H:%M:%S")} | Duration: {action.duration:.2f}s</small>
                {f'<br><img src="{action.screenshot_path}" class="screenshot" alt="Screenshot">' if action.screenshot_path else ''}
            </div>
            """
        return timeline_html

class ChatInterface:
    """Clean, minimal chat interface with modern speech bubble design for AI agent responses."""
    
    def __init__(self):
        self.bubble_id = f"ai-chat-bubble-{uuid.uuid4().hex[:8]}"
        self.default_message = "AI assistant is ready to help you."
    
    def create_chat_bubble(self, message: str = None, position: str = "top-left") -> str:
        """
        Create a clean, minimal chat interface speech bubble for AI responses.
        Modern flat UI design with precise styling as specified.
        
        Args:
            message: The AI response text to display
            position: Position of the bubble (default "top-left" for AI avatar connection)
        
        Returns:
            JavaScript code to inject the chat bubble
        """
        if not message:
            message = self.default_message
        
        # Split message into sentences to make first sentence bold
        sentences = message.split('. ')
        if len(sentences) > 1:
            first_sentence = sentences[0] + '.'
            remaining_text = '. '.join(sentences[1:])
            formatted_message = f"<strong style='font-weight: 600;'>{first_sentence}</strong> {remaining_text}"
        else:
            formatted_message = f"<strong style='font-weight: 600;'>{message}</strong>"
        
        # Position configurations - default to top-left for AI avatar connection
        position_styles = {
            "top-left": "top: 60px; left: 80px;",  # Positioned to connect with AI avatar
            "top-right": "top: 60px; right: 20px;",
            "bottom-left": "bottom: 20px; left: 80px;",
            "bottom-right": "bottom: 20px; right: 20px;"
        }
        
        # Pointer configurations - small triangular pointer at top-left
        pointer_styles = {
            "top-left": "top: -6px; left: 24px; border-bottom: 6px solid #ffffff; border-left: 6px solid transparent; border-right: 6px solid transparent; filter: drop-shadow(0 -1px 1px rgba(0, 0, 0, 0.05));",
            "top-right": "top: -6px; right: 24px; border-bottom: 6px solid #ffffff; border-left: 6px solid transparent; border-right: 6px solid transparent; filter: drop-shadow(0 -1px 1px rgba(0, 0, 0, 0.05));",
            "bottom-left": "bottom: -6px; left: 24px; border-top: 6px solid #ffffff; border-left: 6px solid transparent; border-right: 6px solid transparent; filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.05));",
            "bottom-right": "bottom: -6px; right: 24px; border-top: 6px solid #ffffff; border-left: 6px solid transparent; border-right: 6px solid transparent; filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.05));"
        }
        
        position_css = position_styles.get(position, position_styles["top-left"])
        pointer_css = pointer_styles.get(position, pointer_styles["top-left"])
        
        bubble_js = f"""
        // Remove existing bubble if any
        const existingBubble = document.getElementById('{self.bubble_id}');
        if (existingBubble) {{
            existingBubble.remove();
        }}
        
        // Ensure standard Windows cursor is applied globally
        document.body.style.cursor = 'default';
        document.documentElement.style.cursor = 'default';
        
        // Create chat bubble container with precise specifications
        const chatBubble = document.createElement('div');
        chatBubble.id = '{self.bubble_id}';
        chatBubble.style.cssText = `
            position: fixed;
            {position_css}
            max-width: 280px;
            min-width: 180px;
            background: #ffffff;
            color: #4b5563;
            padding: 14px 16px;
            border-radius: 8px;
            font-family: 'Inter', 'Arial', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 14px;
            line-height: 1.45;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08), 0 1px 4px rgba(0, 0, 0, 0.04);
            z-index: 999999;
            opacity: 0;
            transform: translateY(-8px) scale(0.98);
            transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            border: none;
            cursor: default;
            user-select: none;
            font-weight: 400;
            letter-spacing: -0.01em;
        `;
        
        // Create message content with balanced padding
        chatBubble.innerHTML = `
            <div style="
                position: relative; 
                word-wrap: break-word; 
                line-height: 1.45;
                margin: 0;
                padding: 0;
                color: #4b5563;
                cursor: default;
            ">
                {formatted_message}
            </div>
            <div style="
                position: absolute;
                {pointer_css}
                width: 0;
                height: 0;
            "></div>
        `;
        
        document.body.appendChild(chatBubble);
        
        // Animate bubble in with smooth entrance
        setTimeout(() => {{
            chatBubble.style.opacity = '1';
            chatBubble.style.transform = 'translateY(0) scale(1)';
        }}, 50);
        
        // Create subtle hover effect for interactivity
        chatBubble.addEventListener('mouseenter', function() {{
            this.style.boxShadow = '0 3px 12px rgba(0, 0, 0, 0.1), 0 1px 6px rgba(0, 0, 0, 0.06)';
            this.style.transform = 'translateY(-1px) scale(1)';
            document.body.style.cursor = 'default';
        }});
        
        chatBubble.addEventListener('mouseleave', function() {{
            this.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08), 0 1px 4px rgba(0, 0, 0, 0.04)';
            this.style.transform = 'translateY(0) scale(1)';
            document.body.style.cursor = 'default';
        }});
        
        // Auto-hide after delay (optional)
        setTimeout(() => {{
            if (document.getElementById('{self.bubble_id}')) {{
                chatBubble.style.opacity = '0';
                chatBubble.style.transform = 'translateY(-8px) scale(0.98)';
                setTimeout(() => {{
                    if (chatBubble.parentNode) {{
                        chatBubble.parentNode.removeChild(chatBubble);
                    }}
                }}, 250);
            }}
        }}, 8000);
        """
        
        return bubble_js
    
    def update_bubble_message(self, new_message: str) -> str:
        """
        Update the message in an existing chat bubble.
        
        Args:
            new_message: New message to display
        
        Returns:
            JavaScript code to update the bubble
        """
        # Split message into sentences to make first sentence bold
        sentences = new_message.split('. ')
        if len(sentences) > 1:
            first_sentence = sentences[0] + '.'
            remaining_text = '. '.join(sentences[1:])
            formatted_message = f"<strong>{first_sentence}</strong> {remaining_text}"
        else:
            formatted_message = f"<strong>{new_message}</strong>"
        
        update_js = f"""
        const existingBubble = document.getElementById('{self.bubble_id}');
        if (existingBubble) {{
            const messageDiv = existingBubble.querySelector('div');
            if (messageDiv) {{
                messageDiv.innerHTML = `{formatted_message}`;
                
                // Add subtle pulse animation for update
                existingBubble.style.transform = 'scale(1.02)';
                setTimeout(() => {{
                    existingBubble.style.transform = 'scale(1)';
                }}, 150);
            }}
        }}
        """
        return update_js
    
    def remove_bubble(self) -> str:
        """
        Remove the chat bubble with smooth animation.
        
        Returns:
            JavaScript code to remove the bubble
        """
        remove_js = f"""
        const bubble = document.getElementById('{self.bubble_id}');
        if (bubble) {{
            bubble.style.opacity = '0';
            bubble.style.transform = 'translateY(-10px) scale(0.95)';
            setTimeout(() => {{
                if (bubble.parentNode) {{
                    bubble.parentNode.removeChild(bubble);
                }}
            }}, 300);
        }}
        """
        return remove_js
    
    def create_typing_indicator(self, position: str = "top-left") -> str:
        """
        Create a clean typing indicator bubble matching the main chat design.
        
        Args:
            position: Position of the bubble
        
        Returns:
            JavaScript code for typing indicator
        """
        position_styles = {
            "top-left": "top: 60px; left: 80px;",
            "top-right": "top: 60px; right: 20px;",
            "bottom-left": "bottom: 20px; left: 80px;",
            "bottom-right": "bottom: 20px; right: 20px;"
        }
        
        position_css = position_styles.get(position, position_styles["top-left"])
        typing_id = f"ai-typing-{uuid.uuid4().hex[:8]}"
        
        typing_js = f"""
        // Ensure standard cursor
        document.body.style.cursor = 'default';
        document.documentElement.style.cursor = 'default';
        
        const typingBubble = document.createElement('div');
        typingBubble.id = '{typing_id}';
        typingBubble.style.cssText = `
            position: fixed;
            {position_css}
            background: #ffffff;
            color: #6b7280;
            padding: 12px 16px;
            border-radius: 8px;
            font-family: 'Inter', 'Arial', 'Segoe UI', sans-serif;
            font-size: 13px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08), 0 1px 4px rgba(0, 0, 0, 0.04);
            z-index: 999999;
            opacity: 0;
            transform: scale(0.98);
            transition: all 0.25s ease;
            border: none;
            cursor: default;
            user-select: none;
            letter-spacing: -0.01em;
        `;
        
        typingBubble.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px; cursor: default;">
                <div style="display: flex; gap: 3px;">
                    <div style="width: 5px; height: 5px; background: #9ca3af; border-radius: 50%; animation: typing 1.4s infinite;"></div>
                    <div style="width: 5px; height: 5px; background: #9ca3af; border-radius: 50%; animation: typing 1.4s infinite 0.2s;"></div>
                    <div style="width: 5px; height: 5px; background: #9ca3af; border-radius: 50%; animation: typing 1.4s infinite 0.4s;"></div>
                </div>
                <span style="color: #6b7280; font-weight: 400;">AI is thinking...</span>
            </div>
        `;
        
        // Add CSS animation with smooth, subtle movement
        const style = document.createElement('style');
        style.textContent = `
            @keyframes typing {{
                0%, 60%, 100% {{ 
                    opacity: 0.4; 
                    transform: scale(0.9); 
                }}
                30% {{ 
                    opacity: 1; 
                    transform: scale(1.1); 
                }}
            }}
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(typingBubble);
        
        setTimeout(() => {{
            typingBubble.style.opacity = '1';
            typingBubble.style.transform = 'scale(1)';
        }}, 50);
        
        // Return remove function
        window.removeTypingIndicator = function() {{
            const bubble = document.getElementById('{typing_id}');
            if (bubble) {{
                bubble.style.opacity = '0';
                bubble.style.transform = 'scale(0.98)';
                setTimeout(() => bubble.remove(), 250);
            }}
        }};
        """
        
        return typing_js

    def create_ai_avatar(self, position: str = "top-left") -> str:
        """
        Create a simple AI avatar icon that the chat bubble connects to.
        
        Args:
            position: Position for the avatar
        
        Returns:
            JavaScript code to create the avatar
        """
        avatar_id = f"ai-avatar-{uuid.uuid4().hex[:8]}"
        
        # Position the avatar to the left of where the bubble appears
        avatar_positions = {
            "top-left": "top: 60px; left: 20px;",
            "top-right": "top: 60px; right: 80px;",
            "bottom-left": "bottom: 20px; left: 20px;",
            "bottom-right": "bottom: 20px; right: 80px;"
        }
        
        avatar_css = avatar_positions.get(position, avatar_positions["top-left"])
        
        avatar_js = f"""
        // Remove existing avatar if any
        const existingAvatar = document.getElementById('{avatar_id}');
        if (existingAvatar) {{
            existingAvatar.remove();
        }}
        
        // Create AI avatar
        const aiAvatar = document.createElement('div');
        aiAvatar.id = '{avatar_id}';
        aiAvatar.style.cssText = `
            position: fixed;
            {avatar_css}
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 999998;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            cursor: default;
            user-select: none;
        `;
        
        aiAvatar.innerHTML = `
            <span style="
                color: white; 
                font-size: 16px; 
                font-weight: 600;
                font-family: 'Inter', 'Arial', sans-serif;
                cursor: default;
            ">AI</span>
        `;
        
        document.body.appendChild(aiAvatar);
        
        // Store avatar for later removal
        window.currentAiAvatar = '{avatar_id}';
        """
        
        return avatar_js

    def remove_ai_avatar(self) -> str:
        """Remove the AI avatar."""
        remove_js = """
        if (window.currentAiAvatar) {
            const avatar = document.getElementById(window.currentAiAvatar);
            if (avatar) {
                avatar.remove();
            }
            delete window.currentAiAvatar;
        }
        """
        return remove_js

    def ensure_standard_cursor(self) -> str:
        """Ensure the cursor is the standard Windows black arrow cursor."""
        cursor_js = """
        // Override any custom cursors and ensure standard Windows cursor
        document.body.style.cursor = 'default';
        document.documentElement.style.cursor = 'default';
        
        // Apply to all elements that might have custom cursors
        const allElements = document.querySelectorAll('*');
        allElements.forEach(el => {
            const computedStyle = window.getComputedStyle(el);
            if (computedStyle.cursor !== 'default' && 
                computedStyle.cursor !== 'pointer' && 
                computedStyle.cursor !== 'text') {
                el.style.cursor = 'default';
            }
        });
        
        // Set default cursor for the entire page
        const style = document.createElement('style');
        style.textContent = `
            *, *:before, *:after {
                cursor: default !important;
            }
            a, button, [onclick], .clickable {
                cursor: pointer !important;
            }
            input, textarea, [contenteditable] {
                cursor: text !important;
            }
        `;
        document.head.appendChild(style);
        """
        return cursor_js

class MacroRecorder:
    """Record and replay browser automation macros."""
    
    def __init__(self):
        self.recording = False
        self.macro_steps = []
        self.saved_macros = {}
        
    def start_recording(self, macro_name: str):
        """Start recording user actions."""
        self.recording = True
        self.macro_steps = []
        self.current_macro_name = macro_name
        logger.info(f"Started recording macro: {macro_name}")
        
    def record_action(self, action_type: str, target: str, value: Any = None, wait_after: float = 0):
        """Record a single action."""
        if self.recording:
            step = {
                "action": action_type,
                "target": target,
                "value": value,
                "wait": wait_after,
                "timestamp": datetime.now().isoformat()
            }
            self.macro_steps.append(step)
            
    def stop_recording(self) -> Dict:
        """Stop recording and save macro."""
        if self.recording:
            self.recording = False
            macro = {
                "name": self.current_macro_name,
                "steps": self.macro_steps,
                "created": datetime.now().isoformat(),
                "total_steps": len(self.macro_steps)
            }
            self.saved_macros[self.current_macro_name] = macro
            self.save_to_file(self.current_macro_name)
            logger.info(f"Stopped recording macro: {self.current_macro_name} with {len(self.macro_steps)} steps")
            return macro
        return {}
    
    def save_to_file(self, macro_name: str):
        """Save macro to JSON file."""
        macro_path = f"data/macros/{macro_name}.json"
        os.makedirs("data/macros", exist_ok=True)
        with open(macro_path, 'w') as f:
            json.dump(self.saved_macros[macro_name], f, indent=2)
            
    def load_macro(self, macro_name: str) -> Dict:
        """Load macro from file."""
        macro_path = f"data/macros/{macro_name}.json"
        if os.path.exists(macro_path):
            with open(macro_path, 'r') as f:
                macro = json.load(f)
                self.saved_macros[macro_name] = macro
                return macro
        return {}
    
    def list_macros(self) -> List[str]:
        """List all saved macros."""
        macro_dir = "data/macros"
        if os.path.exists(macro_dir):
            return [f.replace('.json', '') for f in os.listdir(macro_dir) if f.endswith('.json')]
        return []

class DataExtractor:
    """Advanced data extraction and processing."""
    
    def __init__(self, driver):
        self.driver = driver
        
    def extract_tables(self, save_format: str = "excel") -> List[pd.DataFrame]:
        """Extract all tables from the current page."""
        tables = self.driver.find_elements(By.TAG_NAME, "table")
        dataframes = []
        
        for i, table in enumerate(tables):
            # Extract table data using pandas
            table_html = table.get_attribute('outerHTML')
            df = pd.read_html(table_html)[0]
            dataframes.append(df)
            
            # Save to file
            if save_format == "excel":
                df.to_excel(f"data/extracted_table_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", index=False)
            elif save_format == "csv":
                df.to_csv(f"data/extracted_table_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", index=False)
                
        logger.info(f"Extracted {len(dataframes)} tables")
        return dataframes
    
    def extract_structured_data(self) -> Dict:
        """Extract structured data (JSON-LD, microdata, etc.)."""
        structured_data = {}
        
        # Extract JSON-LD
        json_ld_scripts = self.driver.find_elements(By.XPATH, "//script[@type='application/ld+json']")
        for script in json_ld_scripts:
            try:
                data = json.loads(script.get_attribute('innerHTML'))
                structured_data['json_ld'] = structured_data.get('json_ld', [])
                structured_data['json_ld'].append(data)
            except:
                pass
                
        # Extract Open Graph meta tags
        og_tags = {}
        meta_tags = self.driver.find_elements(By.XPATH, "//meta[starts-with(@property, 'og:')]")
        for tag in meta_tags:
            property_name = tag.get_attribute('property')
            content = tag.get_attribute('content')
            og_tags[property_name] = content
        structured_data['open_graph'] = og_tags
        
        # Extract Twitter Card meta tags
        twitter_tags = {}
        twitter_meta = self.driver.find_elements(By.XPATH, "//meta[starts-with(@name, 'twitter:')]")
        for tag in twitter_meta:
            name = tag.get_attribute('name')
            content = tag.get_attribute('content')
            twitter_tags[name] = content
        structured_data['twitter_card'] = twitter_tags
        
        return structured_data
    
    def extract_emails(self) -> List[str]:
        """Extract all email addresses from the page."""
        page_source = self.driver.page_source
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = list(set(re.findall(email_pattern, page_source)))
        logger.info(f"Found {len(emails)} email addresses")
        return emails
    
    def extract_phone_numbers(self) -> List[str]:
        """Extract phone numbers from the page."""
        page_source = self.driver.page_source
        # Multiple phone patterns
        patterns = [
            r'\+?1?\s*\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4}',  # US format
            r'\+?44\s?[0-9]{2,4}\s?[0-9]{3,4}\s?[0-9]{3,4}',  # UK format
            r'\+?[0-9]{1,3}\s?[0-9]{2,4}\s?[0-9]{3,4}\s?[0-9]{3,4}'  # International
        ]
        
        phones = []
        for pattern in patterns:
            phones.extend(re.findall(pattern, page_source))
        
        phones = list(set(phones))
        logger.info(f"Found {len(phones)} phone numbers")
        return phones

class PerformanceMonitor:
    """Monitor and optimize browser performance."""
    
    def __init__(self, driver):
        self.driver = driver
        self.metrics_history = []
        
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        # Navigation timing
        navigation_timing = self.driver.execute_script("""
            const timing = performance.timing;
            return {
                pageLoadTime: timing.loadEventEnd - timing.navigationStart,
                domReadyTime: timing.domContentLoadedEventEnd - timing.navigationStart,
                firstPaintTime: performance.getEntriesByType('paint')[0]?.startTime || 0
            };
        """)
        
        # Memory usage
        memory_info = self.driver.execute_script("""
            if (performance.memory) {
                return {
                    usedJSHeapSize: performance.memory.usedJSHeapSize,
                    totalJSHeapSize: performance.memory.totalJSHeapSize,
                    jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
                };
            }
            return null;
        """)
        
        # JavaScript errors
        js_errors = self.driver.get_log('browser')
        error_messages = [log['message'] for log in js_errors if log['level'] == 'SEVERE']
        
        # Network requests count
        network_entries = self.driver.execute_script("""
            return performance.getEntriesByType('resource').length;
        """)
        
        metrics = PerformanceMetrics(
            page_load_time=navigation_timing['pageLoadTime'] / 1000,
            dom_ready_time=navigation_timing['domReadyTime'] / 1000,
            first_paint_time=navigation_timing['firstPaintTime'] / 1000,
            memory_usage=memory_info['usedJSHeapSize'] / 1048576 if memory_info else 0,  # Convert to MB
            cpu_usage=psutil.cpu_percent(),
            network_requests_count=network_entries,
            javascript_errors=error_messages,
            timestamp=datetime.now()
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def optimize_page_load(self):
        """Apply optimizations to improve page load."""
        # Disable images
        self.driver.execute_cdp_cmd('Emulation.setUserAgentOverride', {
            "userAgent": self.driver.execute_script("return navigator.userAgent"),
            "acceptLanguage": "en-US,en",
            "platform": "Win32"
        })
        
        # Block unnecessary resources
        self.driver.execute_cdp_cmd('Network.setBlockedURLs', {
            "urls": ["*.gif", "*.png", "*.jpg", "*.jpeg", "*.css"]
        })
        
        # Enable cache
        self.driver.execute_cdp_cmd('Network.setCacheDisabled', {'cacheDisabled': False})

class SmartFormFiller:
    """Intelligent form filling with AI assistance."""
    
    def __init__(self, driver):
        self.driver = driver
        self.field_mappings = {
            'email': ['email', 'e-mail', 'mail', 'correo'],
            'name': ['name', 'fullname', 'full_name', 'nombre'],
            'phone': ['phone', 'tel', 'telephone', 'mobile', 'telefono'],
            'address': ['address', 'street', 'direccion'],
            'city': ['city', 'ciudad'],
            'zip': ['zip', 'postal', 'postcode', 'codigo_postal'],
            'country': ['country', 'pais'],
            'password': ['password', 'pass', 'pwd', 'contrasena']
        }
        
    def auto_fill_form(self, data: Dict[str, str], use_ai: bool = True):
        """Automatically fill form with provided data."""
        form_elements = self.driver.find_elements(By.CSS_SELECTOR, "input, textarea, select")
        filled_count = 0
        
        for element in form_elements:
            try:
                # Get element attributes
                element_type = element.get_attribute('type')
                element_name = element.get_attribute('name') or ''
                element_id = element.get_attribute('id') or ''
                placeholder = element.get_attribute('placeholder') or ''
                label_text = self._get_label_text(element)
                
                # Determine field type
                field_key = self._identify_field_type(
                    element_name, element_id, placeholder, label_text, element_type
                )
                
                if field_key and field_key in data:
                    # Fill the field
                    if element.tag_name == 'select':
                        Select(element).select_by_visible_text(data[field_key])
                    elif element_type == 'checkbox':
                        if data[field_key].lower() in ['true', 'yes', '1']:
                            if not element.is_selected():
                                element.click()
                    elif element_type == 'radio':
                        if element.get_attribute('value') == data[field_key]:
                            element.click()
                    else:
                        element.clear()
                        element.send_keys(data[field_key])
                    
                    filled_count += 1
                    logger.info(f"Filled field {field_key} with value")
                    
            except Exception as e:
                logger.error(f"Error filling form field: {e}")
                
        logger.info(f"Successfully filled {filled_count} form fields")
        return filled_count
    
    def _identify_field_type(self, name: str, id: str, placeholder: str, label: str, input_type: str) -> Optional[str]:
        """Identify the type of form field."""
        combined_text = f"{name} {id} {placeholder} {label}".lower()
        
        for field_type, patterns in self.field_mappings.items():
            for pattern in patterns:
                if pattern in combined_text:
                    return field_type
                    
        # Check input type
        if input_type == 'email':
            return 'email'
        elif input_type == 'tel':
            return 'phone'
        elif input_type == 'password':
            return 'password'
            
        return None
    
    def _get_label_text(self, element) -> str:
        """Get label text for an input element."""
        try:
            # Try to find label by 'for' attribute
            element_id = element.get_attribute('id')
            if element_id:
                label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{element_id}']")
                return label.text
        except:
            pass
            
        try:
            # Try to find parent label
            parent = element.find_element(By.XPATH, "..")
            if parent.tag_name == 'label':
                return parent.text
        except:
            pass
            
        return ""

class MegaAdvancedBrowserAgent:
    """Mega Advanced Browser Agent with all features."""
    
    def __init__(self, headless=False, window_size=(1920, 1080), enable_extensions=True, 
                 enable_ai=True, multi_browser=False, browser_count=1):
        print("🚀 Initializing Mega Advanced Browser Agent with 100+ Features...")
        
        # Initialize all managers and databases
        self.db = AdvancedDatabase()
        self.email_manager = AdvancedEmailManager()
        self.report_generator = AdvancedReportGenerator(self.db)
        self.chat_interface = ChatInterface()  # Initialize clean chat interface
        self.captcha_solver = CaptchaSolver()
        self.macro_recorder = MacroRecorder()
        self.enable_ai = enable_ai
        self.multi_browser = multi_browser
        self.browser_count = browser_count
        self.browser_pool = []
        
        # Setup directories
        for directory in ['screenshots', 'downloads', 'data', 'reports', 'temp', 'exports']:
            os.makedirs(directory, exist_ok=True)
        
        # Advanced Chrome options
        chrome_options = ChromeOptions()
        
        # Performance optimizations
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--log-level=3')
        
        # Enable proper cursor display - REMOVE headless and gpu disable
        if not headless:
            # Keep browser visible for proper cursor
            chrome_options.add_argument('--enable-gpu')
            chrome_options.add_argument('--enable-accelerated-2d-canvas')
            chrome_options.add_argument('--force-device-scale-factor=1')  # Ensure proper cursor scaling
            chrome_options.add_argument('--enable-features=VizDisplayCompositor')  # Better cursor rendering
        else:
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--disable-gpu')
        
        # Remove image disabling for better visual experience
        # chrome_options.add_argument('--disable-images') # Removed for better UX
        
        # Advanced user agent and fingerprint spoofing
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Download preferences
        prefs = {
            "download.default_directory": os.path.abspath("downloads"),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.geolocation": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Initialize driver
        try:
            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=chrome_options
            )
            self.driver.set_window_size(*window_size)
            
            # Advanced JavaScript injections for better functionality and cursor display
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                window.chrome = { runtime: {} };
                
                // Force standard Windows cursor visibility and styling
                document.addEventListener('DOMContentLoaded', function() {
                    document.body.style.cursor = 'default';
                    document.documentElement.style.cursor = 'default';
                });
            """)
            
            # Apply standard cursor immediately
            self.apply_standard_cursor()
            
            # Initialize new powerful components
            self.network_interceptor = NetworkInterceptor(self.driver)
            self.data_extractor = DataExtractor(self.driver)
            self.performance_monitor = PerformanceMonitor(self.driver)
            self.form_filler = SmartFormFiller(self.driver)
            
            # Enable network logging
            self.network_interceptor.enable_network_logging()
            
            # Initialize multi-browser support if enabled
            if self.multi_browser:
                self._initialize_browser_pool()
            
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise
        
        # Initialize data structures
        self.elements_cache: List[ElementInfo] = []
        self.action_history: List[ActionResult] = []
        self.session_data = {
            'start_time': datetime.now(),
            'total_actions': 0,
            'successful_actions': 0,
            'websites_visited': set(),
            'forms_filled': 0,
            'searches_performed': 0,
            'downloads_completed': 0,
            'emails_sent': 0,
            'reports_generated': 0
        }
        
        # Initialize visual elements
        self._initialize_advanced_visual_elements()
        
        logger.info("🎨 Mega Advanced Browser Agent initialized successfully with ALL features!")
        
    def _initialize_advanced_visual_elements(self):
        """Initialize advanced visual elements with human-like animations."""
        advanced_visual_js = '''
        // Remove existing elements
        const existingElements = document.querySelectorAll('#ai-cursor, #ai-analysis-bubble, #ai-status-bar, #ai-progress-ring');
        existingElements.forEach(el => el.remove());

        // Create Windows 10/11 Style Cursor (Unicode Arrow - Most Compatible)
        const cursor = document.createElement('div');
        cursor.id = 'ai-cursor';
        cursor.innerHTML = '➤';  // Unicode arrow that looks like Windows cursor
        cursor.style.cssText = `
            position: fixed;
            font-size: 16px;
            color: white;
            text-shadow: 
                -1px -1px 0 black,
                 1px -1px 0 black,
                -1px  1px 0 black,
                 1px  1px 0 black,
                 0px -1px 0 black,
                 0px  1px 0 black,
                -1px  0px 0 black,
                 1px  0px 0 black,
                 2px  2px 3px rgba(0,0,0,0.5);
            z-index: 999999;
            pointer-events: none;
            transition: all 0.05s ease;
            display: block;
            transform: translate(-2px, -2px);
            opacity: 1;
            font-family: 'Segoe UI Symbol', 'Arial Unicode MS', monospace;
            line-height: 1;
            user-select: none;
        `;
        document.body.appendChild(cursor);
        
        // Ensure standard system cursor for all page elements
        document.body.style.cursor = 'default';
        document.documentElement.style.cursor = 'default';
        
        // Apply standard cursor to all elements
        const style = document.createElement('style');
        style.textContent = `
            *, *:before, *:after {
                cursor: default !important;
            }
            a, button, [onclick], .clickable, [role="button"] {
                cursor: pointer !important;
            }
            input, textarea, [contenteditable] {
                cursor: text !important;
            }
            [draggable="true"] {
                cursor: move !important;
            }
        `;
        document.head.appendChild(style);

        // Create Advanced AI Analysis Bubble
        const bubble = document.createElement('div');
        bubble.id = 'ai-analysis-bubble';
        bubble.style.cssText = `
            position: fixed;
            top: 20px;
            left: 20px;
            max-width: 400px;
            background: linear-gradient(135deg, rgba(45, 55, 72, 0.95) 0%, rgba(55, 65, 82, 0.95) 100%);
            color: white;
            padding: 16px 20px;
            border-radius: 15px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            z-index: 999998;
            opacity: 0;
            transform: translateY(-20px) scale(0.95);
            transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
            backdrop-filter: blur(20px);
        `;
        
        bubble.innerHTML = `
            <div style="position: relative;">
                <div id="bubble-text">🤖 AI is initializing advanced systems...</div>
                <div style="position: absolute; top: -12px; left: 25px; width: 0; height: 0; 
                     border-left: 10px solid transparent; border-right: 10px solid transparent; 
                     border-bottom: 12px solid rgba(45, 55, 72, 0.95);"></div>
            </div>
        `;
        document.body.appendChild(bubble);

        // Create Advanced Progress Ring
        const progressRing = document.createElement('div');
        progressRing.id = 'ai-progress-ring';
        progressRing.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.9));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 999997;
            opacity: 0;
            transform: scale(0.8);
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.3);
        `;
        
        progressRing.innerHTML = `
            <div style="color: white; font-size: 14px; font-weight: bold;" id="progress-text">0%</div>
        `;
        document.body.appendChild(progressRing);

        // Advanced Status Bar
        const statusBar = document.createElement('div');
        statusBar.id = 'ai-status-bar';
        statusBar.style.cssText = `
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 6px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            z-index: 999996;
            opacity: 0;
            transition: opacity 0.3s ease;
            box-shadow: 0 -2px 10px rgba(102, 126, 234, 0.3);
        `;
        document.body.appendChild(statusBar);

        // Add advanced CSS animations
        const advancedStyle = document.createElement('style');
        advancedStyle.textContent = `
            @keyframes aiCursorPulse {
                0%, 100% { 
                    transform: translate(-50%, -50%) scale(1); 
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                }
                50% { 
                    transform: translate(-50%, -50%) scale(1.1); 
                    box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
                }
            }
            
            @keyframes progressSpin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            @keyframes statusBarFlow {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            
            #ai-cursor.active {
                animation: aiCursorPulse 2s infinite;
            }
            
            #ai-progress-ring.active {
                animation: progressSpin 2s linear infinite;
            }
            
            #ai-status-bar.active {
                background-size: 200% 200%;
                animation: statusBarFlow 3s ease infinite;
            }
        `;
        document.head.appendChild(advancedStyle);
        '''
        
        try:
            self.driver.execute_script(advanced_visual_js)
            logger.info("Advanced visual elements initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize visual elements: {e}")

    def show_ai_analysis(self, message: str, duration: int = 8000):
        """Show AI analysis in the speech bubble with proper text escaping and streaming effect."""
        try:
            # Properly escape the message for JavaScript
            escaped_message = message.replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
            
            # Streaming effect - type out the message character by character
            show_bubble_js = f'''
            const bubble = document.getElementById('ai-analysis-bubble');
            const bubbleText = document.getElementById('bubble-text');
            if (bubble && bubbleText) {{
                bubble.style.opacity = '1';
                bubble.style.transform = 'translateY(0) scale(1)';
                
                const fullMessage = "{escaped_message}";
                bubbleText.textContent = '';
                
                let i = 0;
                const typeWriter = () => {{
                    if (i < fullMessage.length) {{
                        bubbleText.textContent += fullMessage.charAt(i);
                        i++;
                        setTimeout(typeWriter, 30); // Streaming typing effect
                    }}
                }};
                typeWriter();
                
                // Auto-hide after duration
                setTimeout(() => {{
                    if (bubble) {{
                        bubble.style.opacity = '0';
                        bubble.style.transform = 'translateY(-20px) scale(0.95)';
                    }}
                }}, {duration});
            }}
            '''
            self.driver.execute_script(show_bubble_js)
        except Exception as e:
            logger.warning(f"Could not show AI analysis: {e}")

    def show_chat_bubble(self, message: str, position: str = "top-left", duration: int = 8000):
        """
        Display a clean, minimal chat bubble with AI response.
        
        Args:
            message: The AI response message to display
            position: Position of the bubble (default "top-left" for AI avatar connection)
            duration: How long to show the bubble in milliseconds (0 for permanent)
        """
        try:
            # Create and inject the chat bubble
            bubble_js = self.chat_interface.create_chat_bubble(message, position)
            
            # If duration is specified and not 0, auto-hide the bubble
            if duration > 0:
                auto_hide_js = f"""
                setTimeout(() => {{
                    {self.chat_interface.remove_bubble()}
                }}, {duration});
                """
                bubble_js += auto_hide_js
            
            self.driver.execute_script(bubble_js)
            logger.info(f"Chat bubble displayed: {message[:50]}...")
            
        except Exception as e:
            logger.warning(f"Could not show chat bubble: {e}")

    def update_chat_bubble(self, new_message: str):
        """
        Update the message in the current chat bubble.
        
        Args:
            new_message: New message to display in the bubble
        """
        try:
            update_js = self.chat_interface.update_bubble_message(new_message)
            self.driver.execute_script(update_js)
            logger.info(f"Chat bubble updated: {new_message[:50]}...")
            
        except Exception as e:
            logger.warning(f"Could not update chat bubble: {e}")

    def show_typing_indicator(self, position: str = "top-left"):
        """
        Show a typing indicator when AI is processing.
        
        Args:
            position: Position of the typing indicator (default "top-left")
        """
        try:
            typing_js = self.chat_interface.create_typing_indicator(position)
            self.driver.execute_script(typing_js)
            logger.info("Typing indicator displayed")
            
        except Exception as e:
            logger.warning(f"Could not show typing indicator: {e}")

    def hide_typing_indicator(self):
        """Remove the typing indicator."""
        try:
            hide_js = "if (window.removeTypingIndicator) { window.removeTypingIndicator(); }"
            self.driver.execute_script(hide_js)
            logger.info("Typing indicator hidden")
            
        except Exception as e:
            logger.warning(f"Could not hide typing indicator: {e}")

    def remove_chat_bubble(self):
        """Remove the current chat bubble with smooth animation."""
        try:
            remove_js = self.chat_interface.remove_bubble()
            self.driver.execute_script(remove_js)
            logger.info("Chat bubble removed")
            
        except Exception as e:
            logger.warning(f"Could not remove chat bubble: {e}")

    def show_ai_response(self, message: str, position: str = "top-left", show_typing: bool = True, typing_delay: float = 1.5):
        """
        Show a complete AI response with optional typing indicator.
        
        Args:
            message: The AI response message
            position: Position of the bubble (default "top-left" for AI avatar connection)
            show_typing: Whether to show typing indicator first
            typing_delay: How long to show typing indicator before message
        """
        try:
            if show_typing:
                # Show typing indicator
                self.show_typing_indicator(position)
                
                # Wait for typing delay
                time.sleep(typing_delay)
                
                # Hide typing indicator
                self.hide_typing_indicator()
                
                # Small delay before showing message
                time.sleep(0.3)
            
            # Show the actual message
            self.show_chat_bubble(message, position)
            logger.info(f"AI response displayed with typing effect: {message[:50]}...")
            
        except Exception as e:
            logger.warning(f"Could not show AI response: {e}")

    def show_ai_avatar(self, position: str = "top-left"):
        """Show the AI avatar icon."""
        try:
            avatar_js = self.chat_interface.create_ai_avatar(position)
            self.driver.execute_script(avatar_js)
            logger.info("AI avatar displayed")
        except Exception as e:
            logger.warning(f"Could not show AI avatar: {e}")

    def hide_ai_avatar(self):
        """Hide the AI avatar icon."""
        try:
            remove_js = self.chat_interface.remove_ai_avatar()
            self.driver.execute_script(remove_js)
            logger.info("AI avatar hidden")
        except Exception as e:
            logger.warning(f"Could not hide AI avatar: {e}")

    def show_complete_chat_interface(self, message: str, position: str = "top-left", show_typing: bool = True):
        """
        Show the complete chat interface with avatar and speech bubble.
        
        Args:
            message: The AI response message
            position: Position for the interface
            show_typing: Whether to show typing indicator
        """
        try:
            # Show avatar first
            self.show_ai_avatar(position)
            
            # Then show the response
            self.show_ai_response(message, position, show_typing)
            
            logger.info("Complete chat interface displayed")
        except Exception as e:
            logger.warning(f"Could not show complete chat interface: {e}")

    def apply_standard_cursor(self):
        """Apply standard Windows black arrow cursor to the page."""
        try:
            cursor_js = self.chat_interface.ensure_standard_cursor()
            self.driver.execute_script(cursor_js)
            logger.info("Standard cursor applied")
        except Exception as e:
            logger.warning(f"Could not apply standard cursor: {e}")

    def show_progress(self, percentage: int):
        """Show progress in the progress ring."""
        try:
            progress_js = f'''
            const progressRing = document.getElementById('ai-progress-ring');
            const progressText = document.getElementById('progress-text');
            if (progressRing && progressText) {{
                progressText.textContent = '{percentage}%';
                progressRing.style.opacity = '1';
                progressRing.style.transform = 'scale(1)';
                
                if ({percentage} < 100) {{
                    progressRing.classList.add('active');
                }} else {{
                    progressRing.classList.remove('active');
                    setTimeout(() => {{
                        progressRing.style.opacity = '0';
                        progressRing.style.transform = 'scale(0.8)';
                    }}, 2000);
                }}
            }}
            '''
            self.driver.execute_script(progress_js)
        except Exception as e:
            logger.warning(f"Could not show progress: {e}")

    def move_cursor_like_human(self, element):
        """Move cursor to element with realistic human-like movement."""
        try:
            rect = element.location_once_scrolled_into_view
            size = element.size
            target_x = rect['x'] + size['width'] / 2
            target_y = rect['y'] + size['height'] / 2
            
            # Create human-like movement with multiple steps and slight variations
            human_movement_js = f'''
            const cursor = document.getElementById('ai-cursor');
            if (cursor) {{
                cursor.style.display = 'block';
                cursor.classList.add('active');
                
                // Get current position or start from a random position
                const startX = cursor.offsetLeft || Math.random() * window.innerWidth;
                const startY = cursor.offsetTop || Math.random() * window.innerHeight;
                
                const targetX = {target_x};
                const targetY = {target_y};
                
                const steps = 8; // More steps for smoother movement
                let currentStep = 0;
                
                const moveStep = () => {{
                    currentStep++;
                    const progress = currentStep / steps;
                    
                    // Easing function for natural movement
                    const easeInOutCubic = t => t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
                    const easedProgress = easeInOutCubic(progress);
                    
                    // Add slight random variations for human-like imperfection
                    const randomOffsetX = (Math.random() - 0.5) * 3;
                    const randomOffsetY = (Math.random() - 0.5) * 3;
                    
                    const currentX = startX + (targetX - startX) * easedProgress + randomOffsetX;
                    const currentY = startY + (targetY - startY) * easedProgress + randomOffsetY;
                    
                    cursor.style.left = currentX + 'px';
                    cursor.style.top = currentY + 'px';
                    
                    // Keep standard cursor transform
                    cursor.style.transform = 'translate(-2px, -2px)';
                    
                    if (currentStep < steps) {{
                        // Variable timing between steps (50-120ms) for human-like movement
                        const delay = 50 + Math.random() * 70;
                        setTimeout(moveStep, delay);
                    }} else {{
                        // Final positioning with proper offset
                        cursor.style.left = targetX + 'px';
                        cursor.style.top = targetY + 'px';
                        cursor.style.transform = 'translate(-2px, -2px)';
                    }}
                }};
                
                moveStep();
            }}
            '''
            
            self.driver.execute_script(human_movement_js)
            time.sleep(0.8)  # Wait for movement to complete
            
        except Exception as e:
            logger.warning(f"Could not move cursor: {e}")

    def activate_status_bar(self, active: bool = True):
        """Activate or deactivate the status bar."""
        try:
            status_js = f'''
            const statusBar = document.getElementById('ai-status-bar');
            if (statusBar) {{
                statusBar.style.opacity = '{1 if active else 0}';
                if ({str(active).lower()}) {{
                    statusBar.classList.add('active');
                }} else {{
                    statusBar.classList.remove('active');
                }}
            }}
            '''
            self.driver.execute_script(status_js)
        except Exception as e:
            logger.warning(f"Could not activate status bar: {e}")

    def get_screenshot_as_png(self):
        """Get screenshot as PNG bytes."""
        return self.driver.get_screenshot_as_png()

    def _get_advanced_interactive_elements(self) -> List[ElementInfo]:
        """Get all interactive elements with advanced analysis including iframes."""
        script = '''
        const elements = [];
        
        // Function to extract elements from a document (main or iframe)
        function extractElementsFromDocument(doc, frameOffset = {x: 0, y: 0}) {
            const selectors = 'a, button, input, textarea, select, [role="button"], [role="link"], ' +
                '[onclick], [tabindex]:not([tabindex="-1"]), [contenteditable="true"], ' +
                '[data-testid], [data-cy], .btn, .button, .link, .clickable, ' +
                'form, label, option, summary, details, [href], [src]';
            
            const docElements = Array.from(doc.querySelectorAll(selectors));
            
            for (const el of docElements) {
                try {
                    const rect = el.getBoundingClientRect();
                    const style = doc.defaultView.getComputedStyle(el);
                    
                    // Adjust coordinates for iframe offset
                    const adjustedRect = {
                        x: rect.x + frameOffset.x,
                        y: rect.y + frameOffset.y,
                        width: rect.width,
                        height: rect.height,
                        top: rect.top + frameOffset.y,
                        left: rect.left + frameOffset.x,
                        bottom: rect.bottom + frameOffset.y,
                        right: rect.right + frameOffset.x
                    };
                    
                    if (adjustedRect.width > 0 && adjustedRect.height > 0 && 
                        adjustedRect.top >= -100 && adjustedRect.left >= -100 &&
                        adjustedRect.bottom <= window.innerHeight + 100 && 
                        adjustedRect.right <= window.innerWidth + 100 &&
                        style.visibility !== 'hidden' && 
                        style.display !== 'none') {
                        
                        const tagName = el.tagName.toLowerCase();
                        const elementType = el.type || 'unknown';
                        const isVisible = adjustedRect.top >= 0 && adjustedRect.left >= 0 && 
                                         adjustedRect.bottom <= window.innerHeight && 
                                         adjustedRect.right <= window.innerWidth;
                        
                        // Fast text extraction with fallbacks
                        let label = '';
                        if (el.textContent && el.textContent.trim()) {
                            label = el.textContent.trim();
                        } else if (el.getAttribute('aria-label')) {
                            label = el.getAttribute('aria-label');
                        } else if (el.getAttribute('placeholder')) {
                            label = el.getAttribute('placeholder');
                        } else if (el.getAttribute('title')) {
                            label = el.getAttribute('title');
                        } else if (el.getAttribute('alt')) {
                            label = el.getAttribute('alt');
                        } else if (el.getAttribute('value')) {
                            label = el.getAttribute('value');
                        } else {
                            label = tagName;
                        }
                        
                        // Fast confidence calculation
                        let confidence = 0.5;
                        if (isVisible) confidence += 0.2;
                        if (el.onclick || el.getAttribute('onclick')) confidence += 0.1;
                        if (tagName === 'button' || tagName === 'a') confidence += 0.1;
                        if (el.getAttribute('role')) confidence += 0.1;
                        
                        // Only collect essential attributes for speed
                        const attributes = {
                            id: el.id || '',
                            class: el.className || '',
                            name: el.name || '',
                            type: el.type || '',
                            role: el.getAttribute('role') || ''
                        };
                        
                        // Skip file input elements to avoid typing errors
                        if (tagName === 'input' && (el.type === 'file' || elementType === 'file')) {
                            continue;
                        }
                        
                        // Add data attribute for iframe tracking
                        el.setAttribute('data-element-id', elements.length + 1);
                        
                        elements.push({
                            element: el,
                            tagName: tagName,
                            label: label.substring(0, 100).replace(/\\s+/g, ' '),
                            elementType: elementType,
                            isVisible: isVisible,
                            isClickable: tagName === 'button' || tagName === 'a' || 
                                       el.onclick || el.getAttribute('onclick') || 
                                       el.getAttribute('role') === 'button',
                            isFormField: ['input', 'textarea', 'select'].includes(tagName),
                            coordinates: [adjustedRect.x, adjustedRect.y, adjustedRect.width, adjustedRect.height],
                            attributes: attributes,
                            textContent: el.textContent ? el.textContent.substring(0, 100) : '',
                            confidenceScore: Math.min(confidence, 1.0),
                            frameSource: frameOffset.x === 0 && frameOffset.y === 0 ? 'main' : 'iframe'
                        });
                    }
                } catch (e) {
                    // Skip errors for speed
                }
            }
        }
        
        // Extract from main document
        extractElementsFromDocument(document);
        
        // Extract from iframes (faster approach)
        const iframes = document.querySelectorAll('iframe');
        for (const iframe of iframes) {
            try {
                // Check if iframe is accessible (same origin)
                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                if (iframeDoc) {
                    const iframeRect = iframe.getBoundingClientRect();
                    const frameOffset = {
                        x: iframeRect.x,
                        y: iframeRect.y
                    };
                    extractElementsFromDocument(iframeDoc, frameOffset);
                }
            } catch (e) {
                // Skip cross-origin iframes
                console.log('Skipping cross-origin iframe');
            }
        }
        
        // Fast sort by confidence and visibility
        const elementData = elements.map((el, i) => ({
            ...el,
            id: i + 1
        })).sort((a, b) => {
            if (a.isVisible && !b.isVisible) return -1;
            if (!a.isVisible && b.isVisible) return 1;
            return b.confidenceScore - a.confidenceScore;
        });
        
        return elementData;
        '''
        
        try:
            # Faster wait with shorter timeout
            WebDriverWait(self.driver, 5).until(
                lambda d: d.find_element(By.TAG_NAME, "body")
            )
            raw_elements = self.driver.execute_script(script)
            
            # Faster conversion to ElementInfo objects
            elements = []
            for raw_element in raw_elements[:50]:  # Limit to top 50 elements for speed
                try:
                    element_info = ElementInfo(
                        id=raw_element['id'],
                        element=raw_element['element'],
                        tag_name=raw_element['tagName'],
                        label=raw_element['label'],
                        element_type=raw_element['elementType'],
                        is_visible=raw_element['isVisible'],
                        is_clickable=raw_element['isClickable'],
                        is_form_field=raw_element['isFormField'],
                        coordinates=tuple(raw_element['coordinates']),
                        attributes=raw_element['attributes'],
                        text_content=raw_element['textContent'],
                        confidence_score=raw_element['confidenceScore']
                    )
                    elements.append(element_info)
                except Exception as e:
                    # Skip errors for speed
                    continue
            
            # Log iframe detection results
            iframe_elements = [e for e in elements if e.attributes.get('frameSource') == 'iframe']
            if iframe_elements:
                logger.info(f"Found {len(iframe_elements)} elements inside iframes")
            
            logger.info(f"Found {len(elements)} advanced interactive elements (including iframes)")
            return elements
            
        except Exception as e:
            logger.error(f"Error getting interactive elements: {e}")
            return []

    def _draw_advanced_labels_on_image(self, screenshot_png: bytes, elements: List[ElementInfo]) -> bytes:
        """Draw advanced element labels with BETTER VISIBILITY and proper numbering."""
        image = Image.open(BytesIO(screenshot_png))
        draw = ImageDraw.Draw(image)
        
        # Load fonts with proper fallback
        try:
            title_font = ImageFont.truetype("arial.ttf", 16)  # Larger font
            label_font = ImageFont.truetype("arial.ttf", 14)  # Larger font
            small_font = ImageFont.truetype("arial.ttf", 11)  # Larger font
        except (IOError, OSError):
            try:
                title_font = ImageFont.truetype("Arial.ttf", 16)
                label_font = ImageFont.truetype("Arial.ttf", 14)
                small_font = ImageFont.truetype("Arial.ttf", 11)
            except (IOError, OSError):
                title_font = ImageFont.load_default()
                label_font = ImageFont.load_default()
                small_font = ImageFont.load_default()

        # ENHANCED color mapping with BRIGHT, VISIBLE colors
        color_map = {
            'a': (0, 255, 0),             # Bright Green for links
            'input': (255, 165, 0),       # Bright Orange for inputs
            'textarea': (255, 140, 0),    # Dark Orange for textareas
            'button': (0, 150, 255),      # Bright Blue for buttons
            'select': (255, 0, 255),      # Magenta for selects
            'form': (255, 20, 147),       # Deep Pink for forms
            'label': (165, 42, 42),       # Brown for labels
        }
        
        # Draw elements with ENHANCED VISIBILITY
        valid_element_count = 0
        for element_info in elements:
            if not element_info.is_visible or element_info.confidence_score < 0.3:
                continue  # Skip invisible or low-confidence elements
                
            valid_element_count += 1
            try:
                x, y, w, h = element_info.coordinates
                label_id = str(valid_element_count)  # Use sequential numbering for visible elements
                tag_name = element_info.tag_name
                
                # Get BRIGHT color based on element type
                if element_info.is_form_field:
                    color = color_map.get(tag_name, (255, 165, 0))  # Bright Orange
                elif element_info.is_clickable:
                    color = color_map.get(tag_name, (0, 150, 255))  # Bright Blue
                else:
                    color = color_map.get(tag_name, (128, 128, 128))  # Gray default
                
                # Draw THICKER element outline for better visibility
                outline_width = max(3, int(element_info.confidence_score * 5))
                
                # Draw multiple outline layers for better visibility
                for i in range(outline_width):
                    draw.rectangle((x-i, y-i, x + w + i, y + h + i), outline=color, width=1)
                
                # Create LARGER, MORE VISIBLE label
                text_bbox = draw.textbbox((0, 0), label_id, font=label_font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                # LARGER label background with better positioning
                padding = 8
                label_width = text_width + (padding * 2)
                label_height = text_height + (padding * 2)
                
                # Position label at top-left with better visibility
                label_x = max(2, x - 2)
                label_y = max(2, y - label_height - 4)
                
                # Draw TRANSPARENT label background (less intrusive)
                label_bg_coords = [label_x, label_y, label_x + label_width, label_y + label_height]
                
                # Semi-transparent background instead of black
                transparent_color = tuple(list(color) + [180])  # Add alpha for transparency
                draw.rectangle(label_bg_coords, fill=color)
                
                # Thin outline for contrast without heavy black border
                draw.rectangle(label_bg_coords, outline=(255, 255, 255), width=1)
                
                # Clean text without heavy shadow
                draw.text((label_x + padding, label_y + padding), 
                         label_id, font=label_font, fill=(255, 255, 255))
                
                # Simplified element type indicator (no black background)
                indicator_x = x + w - 15
                indicator_y = y + 2
                
                if element_info.is_form_field:
                    type_indicator = "📝" if tag_name == 'textarea' else "💬" if tag_name == 'input' else "📋"
                elif element_info.is_clickable:
                    type_indicator = "👆"
                else:
                    type_indicator = "👁️"
                
                # Draw indicator with minimal background
                draw.text((indicator_x, indicator_y), type_indicator, font=small_font)
                
                # Simplified confidence indicator (smaller, less intrusive)
                confidence_size = max(6, int(element_info.confidence_score * 8))
                confidence_color = (0, 255, 0) if element_info.confidence_score > 0.8 else (255, 255, 0) if element_info.confidence_score > 0.6 else (255, 0, 0)
                
                conf_x = x + w - confidence_size - 2
                conf_y = y + h - confidence_size - 2
                draw.ellipse([conf_x, conf_y, conf_x + confidence_size, conf_y + confidence_size], 
                           fill=confidence_color, outline=(255, 255, 255), width=1)
                
                # Update element_info id to match visible numbering
                element_info.id = valid_element_count
                
            except Exception as e:
                logger.warning(f"Error drawing label for element {element_info.id}: {e}")
                continue
        
        # Add ENHANCED professional watermark
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            url = self.driver.current_url[:50] + "..." if len(self.driver.current_url) > 50 else self.driver.current_url
            watermark_text = f"🤖 Mega AI Agent | {timestamp} | Elements: {valid_element_count}"
            
            # Get image dimensions
            img_width, img_height = image.size;
            
            # Calculate watermark position
            watermark_bbox = draw.textbbox((0, 0), watermark_text, font=small_font)
            watermark_width = watermark_bbox[2] - watermark_bbox[0]
            watermark_height = watermark_bbox[3] - watermark_bbox[1]
            
            # Enhanced background for watermark
            bg_padding = 8
            bg_coords = [0, img_height - watermark_height - bg_padding * 2, 
                        watermark_width + bg_padding * 2, img_height]
            
            # Black background with border
            draw.rectangle(bg_coords, fill=(0, 0, 0))
            draw.rectangle([1, img_height - watermark_height - bg_padding * 2 + 1, 
                          watermark_width + bg_padding * 2 - 1, img_height - 1], 
                         outline=(255, 255, 255), width=1)
            
            # Watermark text
            draw.text((bg_padding, img_height - watermark_height - bg_padding), 
                     watermark_text, font=small_font, fill=(255, 255, 255))
            
        except Exception as e:
            logger.warning(f"Could not add watermark: {e}")
        
        # Convert back to bytes with optimization
        buffer = BytesIO()
        image.save(buffer, format="PNG", optimize=True, quality=95)
        return buffer.getvalue()

    def save_advanced_screenshot(self, filename: str = None, annotate: bool = True) -> str:
        """Save advanced screenshot with optional annotations."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Include milliseconds
            if filename is None:
                filename = f"screenshot_{timestamp}.png"
            
            filepath = os.path.join('screenshots', filename)
            
            if annotate and self.elements_cache:
                screenshot_png = self.get_screenshot_as_png()
                annotated_screenshot = self._draw_advanced_labels_on_image(screenshot_png, self.elements_cache)
                with open(filepath, 'wb') as f:
                    f.write(annotated_screenshot)
            else:
                self.driver.save_screenshot(filepath)
            
            logger.info(f"📸 Advanced screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving screenshot: {e}")
            return None

    def decide_next_action(self, objective: str, annotated_screenshot_b64: str, elements: List[ElementInfo], last_action_feedback: str) -> Dict:
        """Get AI decision with STREAMING response capability."""
        self.show_ai_analysis("🤖 AI is analyzing with advanced streaming algorithms...")
        self.activate_status_bar(True)
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Create enhanced element descriptions with ONLY VISIBLE elements
        element_descriptions = []
        visible_elements = [e for e in elements if e.is_visible and e.confidence_score >= 0.3]
        
        for i, e in enumerate(visible_elements[:30], 1):  # Renumber visible elements
            confidence_indicator = "🟢" if e.confidence_score > 0.8 else "🟡" if e.confidence_score > 0.6 else "🔴"
            type_indicator = "📝" if e.is_form_field else "👆" if e.is_clickable else "👁️"
            visibility_indicator = "✅"  # All are visible now
            
            description = f"- ID {i}: {confidence_indicator}{type_indicator}{visibility_indicator} \"{e.label[:40]}\" ({e.tag_name}) [conf:{e.confidence_score:.1f}]"
            element_descriptions.append(description)
            # Update element ID to match visible numbering
            e.id = i
        
        element_descriptions_text = "\n".join(element_descriptions)
        
        system_prompt = f"""You are a powerful AI web automation agent with STREAMING response capabilities. Your goal is to achieve objectives through precise actions.

**CONTEXT:**
- **Objective:** {objective}
- **URL:** {self.driver.current_url}
- **Previous Result:** {last_action_feedback}
- **Screenshot:** Shows NUMBERED interactive elements with colored boxes

**VISIBLE ELEMENTS (Confidence ≥ 0.3):**
{element_descriptions_text}

**AVAILABLE ACTIONS:**
1. NAVIGATE - Go to URL: {{"url": "https://example.com"}}
2. CLICK - Click element: {{"id": 1}}
3. TYPE - Type text: {{"id": 1, "text": "search query"}}
4. HOVER - Hover element: {{"id": 1}}
5. SCROLL - Scroll page: {{"direction": "down", "pixels": 500}}
6. WAIT - Wait time: {{"seconds": 2}}
7. PRESS_KEY - Press key: {{"key": "Enter"}}
8. CLEAR - Clear input: {{"id": 1}}
9. SELECT - Select option: {{"id": 1, "option": "value"}}
10. TAKE_SCREENSHOT - Screenshot: {{}}
11. EXECUTE_JS - JavaScript: {{"script": "code"}}
12. REFRESH - Reload page: {{}}
13. GO_BACK - Browser back: {{}}
14. ANSWER - Complete task: {{"text": "Final answer"}}

**RESPONSE FORMAT (Required JSON):**
{{
    "thought": "Detailed reasoning about next action",
    "confidence": 0.9,
    "reasoning": "Why this action will help achieve the objective",
    "action": {{
        "name": "ACTION_NAME",
        "parameters": {{
            "id": 1,
            "text": "if_needed"
        }}
    }}
}}

**CRITICAL RULES:**
- Use ONLY the numbered IDs from the visible elements list above
- Always provide confidence score (0.0-1.0)
- Be specific and goal-oriented
- Handle errors gracefully
"""

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{annotated_screenshot_b64}"}
                        }
                    ]
                }
            ],
            "max_tokens": 1500,
            "response_format": {"type": "json_object"},
            "temperature": 0.2,  # Lower for more consistent responses
            "stream": True  # Enable streaming
        }

        try:
            # STREAMING RESPONSE IMPLEMENTATION
            response = requests.post(API_ENDPOINT_URL, headers=headers, json=payload, timeout=90, stream=True)
            response.raise_for_status()
            
            # Collect streaming response
            content = ""
            print("🔄 AI Streaming Response: ", end="", flush=True)
            
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        try:
                            data_str = line_text[6:]  # Remove 'data: ' prefix
                            if data_str.strip() == '[DONE]':
                                break
                            
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    chunk = delta['content']
                                    content += chunk
                                    print(chunk, end="", flush=True)  # Stream to console
                                    time.sleep(0.01)  # Small delay for visual effect
                        except json.JSONDecodeError:
                            continue
            
            print("\n")  # New line after streaming
            
            if content:
                decision = json.loads(content)
                
                # Log enhanced decision details
                thought = decision.get('thought', 'No thought provided')
                confidence = decision.get('confidence', 0.5)
                reasoning = decision.get('reasoning', 'No reasoning provided')
                
                logger.info(f"🧠 AI Decision - Confidence: {confidence:.2f}")
                logger.info(f"💭 Thought: {thought}")
                logger.info(f"🎯 Reasoning: {reasoning}")
                
                return decision
            else:
                return {"thought": "Empty streaming response", "action": None}
                
        except Exception as e:
            logger.error(f"Error getting AI decision: {e}")
            # Fallback to non-streaming if streaming fails
            try:
                payload["stream"] = False
                response = requests.post(API_ENDPOINT_URL, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    return json.loads(content)
            except:
                pass
            return {"thought": f"Error: {e}", "action": None}
        finally:
            self.activate_status_bar(False)

    def _switch_to_iframe_if_needed(self, element_id: int) -> bool:
        """Switch to iframe if the target element is inside one."""
        try:
            # Check if element is in iframe
            iframe_check_script = f"""
            const element = document.querySelector('[data-element-id="{element_id}"]');
            if (!element) return null;
            
            // Check if element is inside iframe
            let currentDoc = element.ownerDocument;
            if (currentDoc !== document) {{
                // Find the iframe that contains this document
                const iframes = document.querySelectorAll('iframe');
                for (const iframe of iframes) {{
                    try {{
                        if (iframe.contentDocument === currentDoc) {{
                            return {{
                                found: true,
                                iframe: iframe,
                                iframeIndex: Array.from(document.querySelectorAll('iframe')).indexOf(iframe)
                            }};
                        }}
                    }} catch (e) {{
                        // Cross-origin iframe
                    }}
                }}
            }}
            return {{found: false}};
            """
            
            result = self.driver.execute_script(iframe_check_script)
            
            if result and result.get('found'):
                iframe_index = result.get('iframeIndex', 0)
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                if iframe_index < len(iframes):
                    self.driver.switch_to.frame(iframes[iframe_index])
                    logger.info(f"Switched to iframe {iframe_index} for element {element_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking iframe for element {element_id}: {e}")
            return False

    def _switch_back_from_iframe(self):
        """Switch back to main content from iframe."""
        try:
            self.driver.switch_to.default_content()
            logger.info("Switched back to main content")
        except Exception as e:
            logger.warning(f"Error switching back from iframe: {e}")

    def execute_advanced_action(self, decision: Dict) -> ActionResult:
        """Execute the AI's decision with advanced error handling and logging."""
        start_time = time.time()
        action_start_time = datetime.now()
        
        if not decision or not decision.get("action"):
            return ActionResult(
                success=False,
                action_type="INVALID",
                message="❌ No valid action provided",
                duration=0,
                screenshot_path=None,
                element_id=None,
                error_details="Decision is empty or missing action",
                timestamp=action_start_time
            )
        
        action = decision["action"]
        action_name = action.get("name")
        params = action.get("parameters", {})
        
        logger.info(f"Executing advanced action: {action_name} with params: {params}")
        self.session_data['total_actions'] += 1
        
        try:
            # Show progress and analysis
            self.show_progress(25)
            
            if action_name == "NAVIGATE":
                url = params.get("url")
                if not url:
                    return self._create_error_result("NAVIGATE", "URL not provided", start_time, action_start_time)
                
                self.show_ai_analysis(f"🌐 Navigating to {url}...")
                self.show_progress(50)
                
                self.driver.get(url)
                WebDriverWait(self.driver, 15).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                
                self.session_data['websites_visited'].add(url)
                self._initialize_advanced_visual_elements()  # Reinitialize visual elements
                self.show_progress(100)
                
                return self._create_success_result("NAVIGATE", "✅ Navigation successful", start_time, action_start_time)
            
            elif action_name == "ANSWER":
                answer_text = params.get("text", "Task completed")
                self.show_ai_analysis(f"🎉 Task completed successfully! {answer_text}")
                print(f"🤖 AI Agent's Final Answer: {answer_text}")
                self.show_progress(100)
                
                return ActionResult(
                    success=True,
                    action_type="ANSWER",
                    message="🏁 Task finished.",
                    duration=time.time() - start_time,
                    screenshot_path=None,
                    element_id=None,
                    error_details=None,
                    timestamp=action_start_time
                )
            
            elif action_name in ["CLICK", "TYPE", "HOVER", "CLEAR", "SELECT", "RIGHT_CLICK", "DOUBLE_CLICK", "GET_TEXT"]:
                element_id = params.get("id")
                if element_id is None:
                    # Auto-detect input fields for TYPE action
                    if action_name == "TYPE":
                        text = params.get("text", "")
                        element_id = self._auto_detect_input_field(text)
                        if element_id is None:
                            return self._create_error_result(action_name, "Could not find suitable input field automatically", start_time, action_start_time)
                    else:
                        return self._create_error_result(action_name, f"Element ID not provided for {action_name} action", start_time, action_start_time)
                
                # Get target element with enhanced error handling and stale element recovery
                target_element = None
                target_element_info = None
                
                for element_info in self.elements_cache:
                    if element_info.id == element_id:
                        try:
                            # Test if element is still valid
                            _ = element_info.element.is_displayed()
                            target_element = element_info.element
                            target_element_info = element_info
                            break
                        except StaleElementReferenceException:
                            # Element is stale, try to re-find it
                            logger.warning(f"Element {element_id} is stale, attempting to re-find...")
                            try:
                                # Re-detect elements and update cache
                                self.elements_cache = self.get_advanced_elements()
                                # Try to find the element again by similar attributes
                                for new_element_info in self.elements_cache:
                                    if (new_element_info.tag_name == element_info.tag_name and 
                                        new_element_info.label == element_info.label):
                                        target_element = new_element_info.element
                                        target_element_info = new_element_info
                                        logger.info(f"Successfully recovered stale element {element_id}")
                                        break
                            except Exception as recovery_error:
                                logger.error(f"Failed to recover stale element: {recovery_error}")
                                continue
                
                if not target_element:
                    available_ids = [e.id for e in self.elements_cache[:20]]
                    return self._create_error_result(action_name, f"Element ID {element_id} not found. Available: {available_ids}", start_time, action_start_time)
                
                # Move cursor to element with human-like movement
                self.move_cursor_like_human(target_element)
                self.show_progress(75)
                
                # Execute specific action
                result = self._execute_element_action(action_name, params, target_element, target_element_info, start_time, action_start_time)
                self.show_progress(100)
                return result
            
            elif action_name == "SCROLL":
                direction = params.get("direction", "down")
                pixels = params.get("pixels", 500)
                self.show_ai_analysis(f"📜 Scrolling {direction} {pixels}px to see more content...")
                
                scroll_amount = pixels if direction == "down" else -pixels
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(0.5)  # Wait for scroll to complete
                
                return self._create_success_result("SCROLL", f"✅ Scrolled {direction} {pixels}px", start_time, action_start_time)
            
            elif action_name == "WAIT":
                seconds = params.get("seconds", 2)
                self.show_ai_analysis(f"⏳ Waiting {seconds} seconds for page elements to load...")
                
                for i in range(int(seconds * 10)):
                    time.sleep(0.1)
                    progress = min(100, (i / (seconds * 10)) * 100)
                    self.show_progress(int(progress))
                
                return self._create_success_result("WAIT", f"✅ Waited {seconds} seconds", start_time, action_start_time)
            
            elif action_name == "PRESS_KEY":
                key = params.get("key", "Enter")
                self.show_ai_analysis(f"⌨️ Pressing {key} key...")
                
                active_element = self.driver.switch_to.active_element
                key_mapping = {
                    "enter": Keys.ENTER,
                    "tab": Keys.TAB,
                    "escape": Keys.ESCAPE,
                    "space": Keys.SPACE,
                    "backspace": Keys.BACK_SPACE,
                    "delete": Keys.DELETE,
                    "home": Keys.HOME,
                    "end": Keys.END
                }
                
                key_to_send = key_mapping.get(key.lower(), key)
                active_element.send_keys(key_to_send)
                
                return self._create_success_result("PRESS_KEY", f"✅ Pressed {key} key", start_time, action_start_time)
            
            elif action_name == "TAKE_SCREENSHOT":
                self.show_ai_analysis("📸 Taking detailed screenshot for analysis...")
                filepath = self.save_advanced_screenshot()
                return ActionResult(
                    success=True,
                    action_type="TAKE_SCREENSHOT",
                    message=f"✅ Screenshot saved: {filepath}",
                    duration=time.time() - start_time,
                    screenshot_path=filepath,
                    element_id=None,
                    error_details=None,
                    timestamp=action_start_time
                )
            
            elif action_name == "EXECUTE_JS":
                script = params.get("script", "")
                if not script:
                    return self._create_error_result("EXECUTE_JS", "No script provided", start_time, action_start_time)
                
                self.show_ai_analysis(f"⚙️ Executing JavaScript: {script[:50]}...")
                result = self.driver.execute_script(script)
                
                return self._create_success_result("EXECUTE_JS", f"✅ JavaScript executed successfully. Result: {str(result)[:100]}", start_time, action_start_time)
            
            elif action_name == "REFRESH":
                self.show_ai_analysis("🔄 Refreshing the page...")
                self.driver.refresh()
                WebDriverWait(self.driver, 10).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                return self._create_success_result("REFRESH", "✅ Page refreshed successfully", start_time, action_start_time)
            
            elif action_name == "GO_BACK":
                self.show_ai_analysis("⬅️ Going back in browser history...")
                self.driver.back()
                return self._create_success_result("GO_BACK", "✅ Navigated back successfully", start_time, action_start_time)
            
            elif action_name == "GO_FORWARD":
                self.show_ai_analysis("➡️ Going forward in browser history...")
                self.driver.forward()
                return self._create_success_result("GO_FORWARD", "✅ Navigated forward successfully", start_time, action_start_time)
            
            else:
                return self._create_error_result("UNKNOWN", f"Unknown action: {action_name}", start_time, action_start_time)
        
        except Exception as e:
            logger.error(f"Error executing {action_name}: {e}")
            return ActionResult(
                success=False,
                action_type=action_name,
                message=f"❌ {action_name} failed: {str(e)}",
                duration=time.time() - start_time,
                screenshot_path=None,
                element_id=params.get("id"),
                error_details=str(e),
                timestamp=action_start_time
            )

    def _execute_element_action(self, action_name: str, params: Dict, target_element, target_element_info: ElementInfo, start_time: float, action_start_time: datetime) -> ActionResult:
        """Execute element-specific actions with advanced error handling."""
        try:
            if action_name == "CLICK":
                self.show_ai_analysis(f"🎯 Clicking {target_element_info.label[:30]}...")
                
                # Check if element is in iframe and switch if needed
                was_in_iframe = self._switch_to_iframe_if_needed(target_element_info.id)
                
                try:
                    # Re-find element if we switched to iframe
                    if was_in_iframe:
                        target_element = self.driver.find_element(By.XPATH, f"//*[@data-element-id='{target_element_info.id}']")
                    
                    # Advanced click strategies with iframe support
                    strategies = [
                        lambda: target_element.click(),
                        lambda: self.driver.execute_script("arguments[0].click();", target_element),
                        lambda: ActionChains(self.driver).click(target_element).perform(),
                        lambda: self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));", target_element),
                        lambda: ActionChains(self.driver).move_to_element(target_element).click().perform()
                    ]
                    
                    for i, strategy in enumerate(strategies):
                        try:
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_element)
                            time.sleep(0.3)
                            strategy()
                            logger.info(f"✅ Click successful using strategy {i+1}" + (" (iframe)" if was_in_iframe else ""))
                            return self._create_success_result("CLICK", f"✅ Successfully clicked {target_element_info.label[:50]}" + (" (iframe)" if was_in_iframe else ""), start_time, action_start_time, target_element_info.id)
                        except Exception as e:
                            if i == len(strategies) - 1:
                                raise e
                            continue
                finally:
                    # Always switch back from iframe
                    if was_in_iframe:
                        self._switch_back_from_iframe()
            
            elif action_name == "TYPE":
                text = params.get("text", "")
                if not text:
                    return self._create_error_result("TYPE", "No text provided", start_time, action_start_time)
                
                self.show_ai_analysis(f"⌨️ Typing '{text}' into {target_element_info.label[:30]}...")
                
                # Enhanced element stability and interaction
                try:
                    # Wait for element to be stable
                    WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(target_element)
                    )
                    
                    # Scroll and focus with better timing
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", target_element)
                    time.sleep(0.5)
                    
                    # Focus the element first
                    self.driver.execute_script("arguments[0].focus();", target_element)
                    time.sleep(0.2)
                    
                    # Try multiple clearing methods
                    try:
                        target_element.clear()
                    except:
                        # Fallback: Select all and delete
                        target_element.send_keys(Keys.CONTROL + "a")
                        time.sleep(0.1)
                        target_element.send_keys(Keys.DELETE)
                    
                    time.sleep(0.2)
                    
                    # Type with enhanced error handling
                    try:
                        # Try direct send_keys first
                        target_element.send_keys(text)
                    except:
                        # Fallback: Character by character with JavaScript
                        for char in text:
                            try:
                                target_element.send_keys(char)
                                time.sleep(random.uniform(0.05, 0.15))
                            except:
                                # JavaScript fallback
                                self.driver.execute_script(f"arguments[0].value += '{char}';", target_element)
                                time.sleep(0.05)
                    
                    # Trigger input events
                    self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", target_element)
                    self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", target_element)
                    
                except Exception as e:
                    # Ultimate fallback: JavaScript typing
                    try:
                        self.driver.execute_script(f"arguments[0].value = '{text}';", target_element)
                        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", target_element)
                        logger.warning(f"Used JavaScript fallback for typing: {e}")
                    except Exception as js_error:
                        return self._create_error_result("TYPE", f"All typing methods failed: {js_error}", start_time, action_start_time)
                
                return self._create_success_result("TYPE", f"✅ Successfully typed '{text}' into {target_element_info.label[:30]}", start_time, action_start_time, target_element_info.id)
            
            elif action_name == "HOVER":
                self.show_ai_analysis(f"👆 Hovering over {target_element_info.label[:30]}...")
                ActionChains(self.driver).move_to_element(target_element).perform()
                time.sleep(0.5)
                return self._create_success_result("HOVER", f"✅ Successfully hovered over {target_element_info.label[:30]}", start_time, action_start_time, target_element_info.id)
            
            elif action_name == "CLEAR":
                self.show_ai_analysis(f"🧹 Clearing {target_element_info.label[:30]}...")
                target_element.clear()
                return self._create_success_result("CLEAR", f"✅ Successfully cleared {target_element_info.label[:30]}", start_time, action_start_time, target_element_info.id)
            
            elif action_name == "RIGHT_CLICK":
                self.show_ai_analysis(f"🖱️ Right clicking {target_element_info.label[:30]}...")
                ActionChains(self.driver).context_click(target_element).perform()
                return self._create_success_result("RIGHT_CLICK", f"✅ Right clicked {target_element_info.label[:30]}", start_time, action_start_time, target_element_info.id)
            
            elif action_name == "DOUBLE_CLICK":
                self.show_ai_analysis(f"🖱️ Double clicking {target_element_info.label[:30]}...")
                ActionChains(self.driver).double_click(target_element).perform()
                return self._create_success_result("DOUBLE_CLICK", f"✅ Double clicked {target_element_info.label[:30]}", start_time, action_start_time, target_element_info.id)
            
            elif action_name == "SELECT":
                option = params.get("option", "")
                if not option:
                    return self._create_error_result("SELECT", "No option provided", start_time, action_start_time)
                
                self.show_ai_analysis(f"📋 Selecting '{option}' from {target_element_info.label[:30]}...")
                select = Select(target_element)
                
                # Try different selection methods
                try:
                    select.select_by_visible_text(option)
                except:
                    try:
                        select.select_by_value(option)
                    except:
                        select.select_by_index(int(option) if option.isdigit() else 0)
                
                return self._create_success_result("SELECT", f"✅ Selected '{option}' from {target_element_info.label[:30]}", start_time, action_start_time, target_element_info.id)
            
            elif action_name == "GET_TEXT":
                self.show_ai_analysis(f"📖 Extracting text from {target_element_info.label[:30]}...")
                text = target_element.text or target_element.get_attribute('textContent') or target_element.get_attribute('value')
                return self._create_success_result("GET_TEXT", f"✅ Extracted text: '{text[:100]}'", start_time, action_start_time, target_element_info.id)
            
        except Exception as e:
            return ActionResult(
                success=False,
                action_type=action_name,
                message=f"❌ {action_name} failed: {str(e)}",
                duration=time.time() - start_time,
                screenshot_path=None,
                element_id=target_element_info.id,
                error_details=str(e),
                timestamp=action_start_time
            )

    def _auto_detect_input_field(self, search_text: str) -> Optional[int]:
        """Automatically detect the best input field for typing."""
        search_terms = ["search", "query", "q", "input", "text", "find", "lookup"]
        
        best_candidate = None
        best_score = 0
        
        for element_info in self.elements_cache:
            if not element_info.is_form_field:
                continue
                
            score = 0
            label_lower = element_info.label.lower();
            
            # Check for search-related terms
            for term in search_terms:
                if term in label_lower:
                    score += 0.3;
            
            # Prefer visible elements
            if element_info.is_visible:
                score += 0.2;
            
            # Prefer elements with higher confidence
            score += element_info.confidence_score * 0.3;
            
            # Prefer input fields over textareas
            if element_info.tag_name == 'input':
                score += 0.1;
            
            # Check element attributes
            for attr_name, attr_value in element_info.attributes.items():
                if attr_name in ['placeholder', 'name', 'id', 'class']:
                    attr_lower = attr_value.lower();
                    for term in search_terms:
                        if term in attr_lower:
                            score += 0.2;
            
            if score > best_score:
                best_score = score;
                best_candidate = element_info.id;
        
        logger.info(f"Auto-detected input field: ID {best_candidate} with score {best_score:.2f}")
        return best_candidate

    def _create_success_result(self, action_type: str, message: str, start_time: float, timestamp: datetime, element_id: int = None) -> ActionResult:
        """Create a successful action result."""
        self.session_data['successful_actions'] += 1
        screenshot_path = self.save_advanced_screenshot(f"success_{action_type.lower()}_{timestamp.strftime('%H%M%S')}.png")
        
        result = ActionResult(
            success=True,
            action_type=action_type,
            message=message,
            duration=time.time() - start_time,
            screenshot_path=screenshot_path,
            element_id=element_id,
            error_details=None,
            timestamp=timestamp
        )
        
        self.action_history.append(result)
        self.db.log_action(result)
        return result

    def _create_error_result(self, action_type: str, message: str, start_time: float, timestamp: datetime, element_id: int = None) -> ActionResult:
        """Create an error action result."""
        screenshot_path = self.save_advanced_screenshot(f"error_{action_type.lower()}_{timestamp.strftime('%H%M%S')}.png")
        
        result = ActionResult(
            success=False,
            action_type=action_type,
            message=f"❌ {message}",
            duration=time.time() - start_time,
            screenshot_path=screenshot_path,
            element_id=element_id,
            error_details=message,
            timestamp=timestamp
        )
        
        self.action_history.append(result)
        self.db.log_action(result)
        return result

    def _extract_url_from_command(self, command: str) -> Optional[str]:
        """Extract URL from command with advanced pattern matching and AI-powered resolution."""
        # First try explicit URL patterns
        url_patterns = [
            r'https?://[^\s/$.?#].[^\s]*',  # Standard HTTP/HTTPS URLs
            r'www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?',  # www.domain.com
            r'[a-zA-Z0-9-]+\.(?:com|org|net|io|dev|ai|co\.uk|edu|gov)(?:/[^\s]*)?'  # domain.com
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                url = match.group(0)
                if not url.startswith(('http://', 'https://')):
                    url = f'https://{url}'
                return url
        
        # AI-powered natural language URL resolution
        return self._resolve_natural_language_url(command)
    
    def _resolve_natural_language_url(self, command: str) -> Optional[str]:
        """Resolve natural language commands to URLs using AI and common patterns."""
        command_lower = command.lower().strip()
        
        # Common website mappings
        website_mappings = {
            'google': 'https://www.google.com',
            'youtube': 'https://www.youtube.com',
            'facebook': 'https://www.facebook.com',
            'twitter': 'https://www.twitter.com',
            'instagram': 'https://www.instagram.com',
            'linkedin': 'https://www.linkedin.com',
            'github': 'https://www.github.com',
            'stackoverflow': 'https://stackoverflow.com',
            'reddit': 'https://www.reddit.com',
            'amazon': 'https://www.amazon.com',
            'wikipedia': 'https://www.wikipedia.org',
            'netflix': 'https://www.netflix.com',
            'gmail': 'https://mail.google.com',
            'outlook': 'https://outlook.live.com',
            'yahoo': 'https://www.yahoo.com',
            'bing': 'https://www.bing.com',
            'duckduckgo': 'https://duckduckgo.com'
        }
        
        # Pattern matching for "go to X", "open X", "visit X", "navigate to X"
        patterns = [
            r'(?:go to|open|visit|navigate to|search on)\s+([a-zA-Z0-9\s]+)',
            r'(?:search|look up|find)\s+(?:on\s+)?([a-zA-Z0-9\s]+)',
            r'^([a-zA-Z0-9]+)(?:\s|$)'  # Single word at start
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command_lower)
            if match:
                site_name = match.group(1).strip()
                
                # Check direct mappings
                for key, url in website_mappings.items():
                    if key in site_name or site_name in key:
                        logger.info(f"🔍 Resolved '{command}' to {url}")
                        return url
                
                # Try adding .com if it looks like a domain
                if ' ' not in site_name and len(site_name) > 2:
                    potential_url = f"https://www.{site_name}.com"
                    logger.info(f"🔍 Guessing URL for '{site_name}': {potential_url}")
                    return potential_url
        
        # If no pattern matches, try AI resolution (fallback)
        try:
            if API_KEY and 'google' in command_lower:
                return 'https://www.google.com'
            elif API_KEY and any(word in command_lower for word in ['search', 'find', 'look']):
                return 'https://www.google.com'
        except:
            pass
        
        return None

    def generate_session_report(self) -> str:
        """Generate comprehensive session report."""
        try:
            end_time = datetime.now()
            session_duration = (end_time - self.session_data['start_time']).total_seconds()
            
            success_rate = 0
            if self.session_data['total_actions'] > 0:
                success_rate = (self.session_data['successful_actions'] / self.session_data['total_actions']) * 100
            
            report_data = {
                'session_start': self.session_data['start_time'],
                'session_end': end_time,
                'session_duration': session_duration,
                'total_actions': self.session_data['total_actions'],
                'successful_actions': self.session_data['successful_actions'],
                'success_rate': round(success_rate, 1),
                'websites_visited': len(self.session_data['websites_visited']),
                'actions': self.action_history[-20:],  # Last 20 actions
                'total_duration': session_duration
            }
            
            report_path = self.report_generator.generate_html_report(report_data)
            logger.info(f"Session report generated: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"Error generating session report: {e}")
            return None

    def _initialize_browser_pool(self):
        """Initialize multiple browser instances for parallel processing."""
        logger.info(f"Initializing browser pool with {self.browser_count} instances")
        
        for i in range(self.browser_count - 1):  # -1 because main driver already exists
            chrome_options = ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            
            driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=chrome_options
            )
            self.browser_pool.append(driver)
            
        logger.info(f"Browser pool initialized with {len(self.browser_pool) + 1} instances")
    
    def execute_parallel_tasks(self, tasks: List[Dict], max_workers: int = 4) -> List[ActionResult]:
        """Execute multiple tasks in parallel across browser instances."""
        results = []
        
        with ThreadPoolExecutor(max_workers=min(max_workers, len(self.browser_pool) + 1)) as executor:
            futures = []
            
            for i, task in enumerate(tasks):
                # Assign task to available browser
                browser = self.browser_pool[i % len(self.browser_pool)] if self.browser_pool else self.driver
                future = executor.submit(self._execute_task_on_browser, browser, task)
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=60)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Parallel task execution failed: {e}")
                    
        return results
    
    def _execute_task_on_browser(self, browser, task: Dict) -> ActionResult:
        """Execute a single task on a specific browser instance."""
        start_time = time.time()
        
        try:
            # Navigate to URL if specified
            if 'url' in task:
                browser.get(task['url'])
                
            # Execute action
            if task['action'] == 'click':
                element = browser.find_element(By.CSS_SELECTOR, task['selector'])
                element.click()
            elif task['action'] == 'type':
                element = browser.find_element(By.CSS_SELECTOR, task['selector'])
                element.send_keys(task['value'])
            elif task['action'] == 'extract':
                element = browser.find_element(By.CSS_SELECTOR, task['selector'])
                task['result'] = element.text
                
            return ActionResult(
                success=True,
                action_type=task['action'],
                message=f"Task completed: {task.get('name', 'unnamed')}",
                duration=time.time() - start_time,
                screenshot_path=None,
                element_id=None,
                error_details=None,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                action_type=task['action'],
                message=f"Task failed: {task.get('name', 'unnamed')}",
                duration=time.time() - start_time,
                screenshot_path=None,
                element_id=None,
                error_details=str(e),
                timestamp=datetime.now()
            )
    
    def solve_captcha_on_page(self) -> bool:
        """Automatically detect and solve CAPTCHA on current page."""
        try:
            # Check for Cloudflare "Verify you are human" checkbox
            cloudflare_selectors = [
                "input[type='checkbox'][name='cf-turnstile-response']",
                "input[type='checkbox']#challenge-form",
                ".cf-turnstile input[type='checkbox']",
                "input[type='checkbox'][id*='turnstile']",
                "input[type='checkbox'][class*='turnstile']",
                "label:contains('Verify you are human') input[type='checkbox']",
                ".challenge-form input[type='checkbox']",
                "[data-callback] input[type='checkbox']"
            ]
            
            for selector in cloudflare_selectors:
                try:
                    checkbox_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if checkbox_elements:
                        checkbox = checkbox_elements[0]
                        if not checkbox.is_selected():
                            logger.info("Cloudflare CAPTCHA checkbox detected, clicking...")
                            # Scroll into view and click
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                            time.sleep(1)
                            checkbox.click()
                            logger.info("Cloudflare CAPTCHA checkbox clicked successfully")
                            time.sleep(3)  # Wait for verification
                            return True
                except:
                    continue
            
            # Alternative approach: Look for any checkbox near "Verify you are human" text
            try:
                verify_text_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Verify you are human')]")
                if verify_text_elements:
                    # Look for nearby checkbox
                    parent = verify_text_elements[0].find_element(By.XPATH, "./..")
                    checkboxes = parent.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                    if checkboxes:
                        checkbox = checkboxes[0]
                        if not checkbox.is_selected():
                            logger.info("Found 'Verify you are human' checkbox, clicking...")
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                            time.sleep(1)
                            checkbox.click()
                            logger.info("Human verification checkbox clicked successfully")
                            time.sleep(3)
                            return True
            except:
                pass
            
            # Check for reCAPTCHA
            recaptcha_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-sitekey]")
            if recaptcha_elements:
                site_key = recaptcha_elements[0].get_attribute('data-sitekey')
                page_url = self.driver.current_url
                
                logger.info("reCAPTCHA detected, attempting to solve...")
                solution = self.captcha_solver.solve_recaptcha_v2(site_key, page_url)
                
                if solution:
                    # Inject solution
                    self.driver.execute_script(f"""
                        document.getElementById('g-recaptcha-response').innerHTML = '{solution}';
                        if (typeof ___grecaptcha_cfg !== 'undefined') {{
                            Object.entries(___grecaptcha_cfg.clients).forEach(([key, client]) => {{
                                if (client.callback) {{
                                    client.callback('{solution}');
                                }}
                            }});
                        }}
                    """)
                    logger.info("CAPTCHA solved successfully")
                    return True
                    
            # Check for image CAPTCHA
            captcha_images = self.driver.find_elements(By.CSS_SELECTOR, "img[src*='captcha']")
            if captcha_images:
                logger.info("Image CAPTCHA detected")
                # Screenshot and solve
                captcha_images[0].screenshot("temp/captcha.png")
                solution = self.captcha_solver.solve_image_captcha("temp/captcha.png")
                
                if solution:
                    # Find input field and enter solution
                    captcha_input = self.driver.find_element(By.CSS_SELECTOR, "input[name*='captcha']")
                    captcha_input.send_keys(solution)
                    logger.info("Image CAPTCHA solved")
                    return True
                    
        except Exception as e:
            logger.error(f"CAPTCHA solving failed: {e}")
            
        return False
    
    def record_macro(self, macro_name: str):
        """Start recording user actions as a macro."""
        self.macro_recorder.start_recording(macro_name)
        logger.info(f"Macro recording started: {macro_name}")
        
        # Inject JavaScript to track user interactions
        self.driver.execute_script("""
            window.macroRecording = true;
            document.addEventListener('click', function(e) {
                if (window.macroRecording) {
                    console.log('MACRO_CLICK', e.target);
                }
            });
            document.addEventListener('input', function(e) {
                if (window.macroRecording) {
                    console.log('MACRO_INPUT', e.target, e.target.value);
                }
            });
        """)
    
    def stop_macro_recording(self) -> Dict:
        """Stop recording and save the macro."""
        self.driver.execute_script("window.macroRecording = false;")
        return self.macro_recorder.stop_recording()
    
    def replay_macro(self, macro_name: str, speed: float = 1.0) -> List[ActionResult]:
        """Replay a saved macro."""
        macro = self.macro_recorder.load_macro(macro_name)
        if not macro:
            logger.error(f"Macro not found: {macro_name}")
            return []
            
        results = []
        logger.info(f"Replaying macro: {macro_name} with {len(macro['steps'])} steps")
        
        for step in macro['steps']:
            try:
                if step['action'] == 'click':
                    element = self.driver.find_element(By.CSS_SELECTOR, step['target'])
                    element.click()
                elif step['action'] == 'type':
                    element = self.driver.find_element(By.CSS_SELECTOR, step['target'])
                    element.clear()
                    element.send_keys(step['value'])
                elif step['action'] == 'navigate':
                    self.driver.get(step['value'])
                    
                # Wait after action
                time.sleep(step.get('wait', 0) / speed)
                
                results.append(ActionResult(
                    success=True,
                    action_type=step['action'],
                    message=f"Macro step executed: {step['action']}",
                    duration=step.get('wait', 0),
                    screenshot_path=None,
                    element_id=None,
                    error_details=None,
                    timestamp=datetime.now()
                ))
                
            except Exception as e:
                logger.error(f"Macro step failed: {e}")
                results.append(ActionResult(
                    success=False,
                    action_type=step['action'],
                    message=f"Macro step failed: {step['action']}",
                    duration=0,
                    screenshot_path=None,
                    element_id=None,
                    error_details=str(e),
                    timestamp=datetime.now()
                ))
                
        return results
    
    def extract_all_data(self) -> Dict:
        """Extract all possible data from current page."""
        logger.info("Extracting all data from page...")
        
        data = {
            'url': self.driver.current_url,
            'title': self.driver.title,
            'timestamp': datetime.now().isoformat()
        }
        
        # Extract tables
        data['tables'] = self.data_extractor.extract_tables(save_format="excel")
        
        # Extract structured data
        data['structured_data'] = self.data_extractor.extract_structured_data()
        
        # Extract contact information
        data['emails'] = self.data_extractor.extract_emails()
        data['phones'] = self.data_extractor.extract_phone_numbers()
        
        # Extract all links
        links = self.driver.find_elements(By.TAG_NAME, "a")
        data['links'] = [{'text': link.text, 'href': link.get_attribute('href')} 
                        for link in links if link.get_attribute('href')]
        
        # Extract all images
        images = self.driver.find_elements(By.TAG_NAME, "img")
        data['images'] = [{'alt': img.get_attribute('alt'), 'src': img.get_attribute('src')} 
                         for img in images if img.get_attribute('src')]
        
        # Extract all text content
        data['text_content'] = self.driver.find_element(By.TAG_NAME, "body").text
        
        # Save to JSON
        output_file = f"data/extracted_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Data extraction complete. Saved to {output_file}")
        return data
    
    def monitor_performance(self, duration: int = 60) -> List[PerformanceMetrics]:
        """Monitor page performance for specified duration."""
        logger.info(f"Starting performance monitoring for {duration} seconds")
        
        metrics_list = []
        end_time = time.time() + duration
        
        while time.time() < end_time:
            metrics = self.performance_monitor.get_performance_metrics()
            metrics_list.append(metrics)
            
            # Log current metrics
            logger.info(f"Performance: Load={metrics.page_load_time:.2f}s, "
                       f"Memory={metrics.memory_usage:.2f}MB, "
                       f"CPU={metrics.cpu_usage:.1f}%, "
                       f"Requests={metrics.network_requests_count}")
            
            time.sleep(5)  # Check every 5 seconds
            
        # Generate performance report
        self._generate_performance_report(metrics_list)
        return metrics_list
    
    def _generate_performance_report(self, metrics: List[PerformanceMetrics]):
        """Generate performance analysis report."""
        if not metrics:
            return
            
        avg_load_time = sum(m.page_load_time for m in metrics) / len(metrics)
        avg_memory = sum(m.memory_usage for m in metrics) / len(metrics)
        avg_cpu = sum(m.cpu_usage for m in metrics) / len(metrics)
        total_errors = sum(len(m.javascript_errors) for m in metrics)
        
        report = f"""
        Performance Analysis Report
        ===========================
        Average Page Load Time: {avg_load_time:.2f} seconds
        Average Memory Usage: {avg_memory:.2f} MB
        Average CPU Usage: {avg_cpu:.1f}%
        Total JavaScript Errors: {total_errors}
        
        Recommendations:
        """
        
        if avg_load_time > 3:
            report += "\n- Page load time is high. Consider optimizing resources."
        if avg_memory > 100:
            report += "\n- High memory usage detected. Check for memory leaks."
        if total_errors > 0:
            report += "\n- JavaScript errors found. Review console logs."
            
        report_file = f"reports/performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
            
        logger.info(f"Performance report saved to {report_file}")
    
    def smart_fill_form(self, form_data: Dict[str, str]) -> int:
        """Intelligently fill forms using AI and pattern matching."""
        logger.info("Starting smart form filling...")
        
        # Use the SmartFormFiller
        filled_count = self.form_filler.auto_fill_form(form_data, use_ai=self.enable_ai)
        
        # Take screenshot after filling
        screenshot_path = self.save_advanced_screenshot("form_filled")
        
        # Log the action
        self.db.log_action(ActionResult(
            success=filled_count > 0,
            action_type="smart_form_fill",
            message=f"Filled {filled_count} form fields",
            duration=0,
            screenshot_path=screenshot_path,
            element_id=None,
            error_details=None,
            timestamp=datetime.now()
        ))
        
        return filled_count
    
    def handle_popups_and_modals(self) -> bool:
        """Automatically detect and handle popups, modals, and cookie banners."""
        handled = False
        
        try:
            # Common popup/modal selectors
            popup_selectors = [
                "button[aria-label*='close']",
                "button[aria-label*='Close']",
                ".modal-close",
                ".popup-close",
                ".close-button",
                "[class*='close']",
                "[class*='dismiss']",
                "button:contains('Accept')",  # Cookie banners
                "button:contains('OK')",
                "button:contains('Got it')",
                "button:contains('I agree')"
            ]
            
            for selector in popup_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            element.click()
                            logger.info(f"Closed popup/modal using selector: {selector}")
                            handled = True
                            time.sleep(0.5)
                except:
                    continue
                    
            # Handle alert boxes
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
                logger.info("Handled JavaScript alert")
                handled = True
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error handling popups: {e}")
            
        return handled
    
    def create_workflow(self, name: str, steps: List[Dict]) -> AutomationTask:
        """Create a reusable automation workflow."""
        workflow = AutomationTask(
            name=name,
            steps=steps,
            conditions={},
            loops=1,
            delay_between_loops=0,
            on_error="continue",
            max_retries=3,
            timeout=300
        )
        
        # Save workflow
        workflow_file = f"data/workflows/{name}.json"
        os.makedirs("data/workflows", exist_ok=True)
        
        with open(workflow_file, 'w') as f:
            json.dump({
                'name': workflow.name,
                'steps': workflow.steps,
                'conditions': workflow.conditions,
                'loops': workflow.loops,
                'delay_between_loops': workflow.delay_between_loops,
                'on_error': workflow.on_error,
                'max_retries': workflow.max_retries,
                'timeout': workflow.timeout
            }, f, indent=2)
            
        logger.info(f"Workflow '{name}' created with {len(steps)} steps")
        return workflow
    
    def execute_workflow(self, workflow: Union[str, AutomationTask]) -> List[ActionResult]:
        """Execute an automation workflow."""
        if isinstance(workflow, str):
            # Load workflow from file
            workflow_file = f"data/workflows/{workflow}.json"
            if not os.path.exists(workflow_file):
                logger.error(f"Workflow not found: {workflow}")
                return []
                
            with open(workflow_file, 'r') as f:
                workflow_data = json.load(f)
                workflow = AutomationTask(**workflow_data)
                
        results = []
        logger.info(f"Executing workflow: {workflow.name}")
        
        for loop in range(workflow.loops):
            if loop > 0:
                time.sleep(workflow.delay_between_loops)
                
            for step in workflow.steps:
                retry_count = 0
                success = False
                
                while retry_count < workflow.max_retries and not success:
                    try:
                        result = self._execute_workflow_step(step)
                        results.append(result)
                        success = result.success
                        
                        if not success and workflow.on_error == "stop":
                            logger.error(f"Workflow stopped due to error in step: {step.get('name', 'unnamed')}")
                            return results
                            
                    except Exception as e:
                        logger.error(f"Workflow step failed: {e}")
                        retry_count += 1
                        
                        if retry_count >= workflow.max_retries:
                            if workflow.on_error == "stop":
                                return results
                                
        logger.info(f"Workflow '{workflow.name}' completed with {len(results)} actions")
        return results
    
    def _execute_workflow_step(self, step: Dict) -> ActionResult:
        """Execute a single workflow step."""
        start_time = time.time()
        
        try:
            action_type = step.get('action', 'unknown')
            
            if action_type == 'navigate':
                self.driver.get(step['url'])
            elif action_type == 'click':
                element = self.driver.find_element(By.CSS_SELECTOR, step['selector'])
                element.click()
            elif action_type == 'type':
                element = self.driver.find_element(By.CSS_SELECTOR, step['selector'])
                element.clear()
                element.send_keys(step['value'])
            elif action_type == 'wait':
                time.sleep(step.get('duration', 1))
            elif action_type == 'screenshot':
                self.save_advanced_screenshot(step.get('name', 'workflow_screenshot'))
            elif action_type == 'extract':
                self.extract_all_data()
            elif action_type == 'script':
                self.driver.execute_script(step['code'])
                
            return ActionResult(
                success=True,
                action_type=action_type,
                message=f"Workflow step completed: {step.get('name', action_type)}",
                duration=time.time() - start_time,
                screenshot_path=None,
                element_id=None,
                error_details=None,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                action_type=step.get('action', 'unknown'),
                message=f"Workflow step failed: {step.get('name', 'unnamed')}",
                duration=time.time() - start_time,
                screenshot_path=None,
                element_id=None,
                error_details=str(e),
                timestamp=datetime.now()
            )
    
    def _display_welcome_banner(self):
        """Display modern welcome banner with system info and API key check."""
        import platform
        import psutil
        
        # Check for API key first
        if not API_KEY or API_KEY == "your-api-key-here":
            self._prompt_for_api_key()
            return
        
        # Get system info
        cpu_count = psutil.cpu_count()
        memory_gb = round(psutil.virtual_memory().total / (1024**3), 1)
        python_version = platform.python_version()
        
        print("\n" + "="*80)
        print("🤖 MEGA ADVANCED AI BROWSER AGENT v3.0")
        print("="*80)
        print(f"🖥️  System: {platform.system()} {platform.release()}")
        print(f"🐍 Python: {python_version} | 💾 RAM: {memory_gb}GB | 🔧 CPU: {cpu_count} cores")
        print(f"🧠 AI Model: {MODEL_NAME} | 🌐 Provider: Mistral AI")
        print(f"📊 Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
    
    def _prompt_for_api_key(self):
        """Prompt user to set up Mistral AI API key."""
        print("\n" + "="*80)
        print("🔑 MISTRAL AI API KEY SETUP REQUIRED")
        print("="*80)
        print("🚨 No valid Mistral AI API key found!")
        print("\n📋 To get started:")
        print("   1. Visit: https://console.mistral.ai/")
        print("   2. Create an account or sign in")
        print("   3. Generate an API key")
        print("   4. Add it to your .env file:")
        print("      MISTRAL_API_KEY=\"your-actual-api-key-here\"")
        print("      API_KEY=\"your-actual-api-key-here\"")
        print("\n💡 Alternative: Set it now (temporary for this session)")
        
        choice = input("\n🎯 Enter API key now? (y/n): ").lower().strip()
        
        if choice == 'y':
            api_key = input("🔑 Enter your Mistral API key: ").strip()
            if api_key:
                # Update environment variables for this session
                import os
                os.environ['MISTRAL_API_KEY'] = api_key
                os.environ['API_KEY'] = api_key
                global API_KEY
                API_KEY = api_key
                print("✅ API key set for this session!")
                print("💾 Don't forget to add it to your .env file for permanent use")
                return
        
        print("\n❌ Cannot proceed without API key. Please set up and restart.")
        print("📖 See README.md for detailed setup instructions")
        exit(1)
    
    def _display_main_menu(self):
        """Display redesigned main menu with organized sections."""
        print("\n🎨 ┌─── VISUAL FEATURES ───────────────────────────────────────────┐")
        print("   │ • 🎯 Human-like cursor animations    • 💬 Real-time AI bubbles │")
        print("   │ • 📊 Progress indicators             • 🎨 Element annotations  │")
        print("   │ • 🔍 Confidence scoring             • 📸 Auto screenshots     │")
        print("   └───────────────────────────────────────────────────────────────┘")
        
        print("\n🚀 ┌─── CORE CAPABILITIES ─────────────────────────────────────────┐")
        print("   │ • 🔐 CAPTCHA Auto-Solving           • 🌐 Multi-browser Support │")
        print("   │ • 📊 Advanced Data Extraction       • 🎮 Macro Recording       │")
        print("   │ • 📈 Performance Monitoring         • 🤖 Smart Form Filling    │")
        print("   │ • 🔄 Workflow Automation            • 🚦 Network Interception  │")
        print("   └───────────────────────────────────────────────────────────────┘")
        
        print("\n⚡ ┌─── INTELLIGENT ACTIONS ───────────────────────────────────────┐")
        print("   │ NAVIGATE • CLICK • TYPE • SCROLL • HOVER • SELECT • EXTRACT    │")
        print("   │ SCREENSHOT • WAIT • REFRESH • GO_BACK • PRESS_KEY • EXECUTE_JS │")
        print("   └───────────────────────────────────────────────────────────────┘")
        
        print("\n📊 ┌─── ANALYTICS & REPORTING ─────────────────────────────────────┐")
        print("   │ • 📈 Real-time Performance          • 📄 HTML Report Generation│")
        print("   │ • 🗄️  SQLite Database Logging       • 📧 Email Notifications   │")
        print("   │ • 📸 Screenshot Galleries           • 📊 Success Rate Tracking │")
        print("   └───────────────────────────────────────────────────────────────┘")
        
        print("\n🎮 ┌─── QUICK COMMANDS ────────────────────────────────────────────┐")
        print("   │ 📊 info      │ 📸 screenshot │ 📜 history    │ 📄 report      │")
        print("   │ 📈 stats     │ 💬 chat       │ ❓ help       │ 🚪 exit        │")
        print("   │ 🔐 captcha   │ 📋 extract    │ 🎮 record     │ ⚡ monitor     │")
        print("   └───────────────────────────────────────────────────────────────┘")
        
        print("\n💡 ┌─── USAGE EXAMPLES ────────────────────────────────────────────┐")
        print("   │ 🌐 \"go to google.com and search for AI automation\"            │")
        print("   │ 🎥 \"open youtube.com and find programming tutorials\"          │")
        print("   │ 🛒 \"navigate to amazon.com and search for laptops\"           │")
        print("   │ 📝 \"fill out the contact form on this page\"                  │")
        print("   └───────────────────────────────────────────────────────────────┘")

    def _display_enhanced_page_info(self):
        """Display enhanced page information with better formatting."""
        print("\n" + "="*60)
        print("📊 CURRENT PAGE INFORMATION")
        print("="*60)
        
        try:
            info = self._get_page_info()
            print(f"🌐 URL: {info.get('url', 'N/A')}")
            print(f"📄 Title: {info.get('title', 'N/A')}")
            print(f"🔍 Elements Found: {info.get('elements_count', 0)}")
            print(f"👁️  Visible Elements: {info.get('visible_elements', 0)}")
            print(f"📝 Form Fields: {info.get('form_fields', 0)}")
            print(f"🖱️  Clickable Elements: {info.get('clickable_elements', 0)}")
            print(f"📊 Avg Confidence: {info.get('avg_confidence', 0):.2f}")
            print(f"⚡ Page State: {info.get('page_load_state', 'unknown')}")
        except Exception as e:
            print(f"❌ Error retrieving page info: {e}")
        
        print("="*60)

    def _take_enhanced_screenshot(self):
        """Take enhanced screenshot with better feedback."""
        print("\n📸 Taking enhanced screenshot...")
        try:
            filepath = self.save_advanced_screenshot()
            print(f"✅ Screenshot saved: {filepath}")
            print(f"📁 Location: screenshots/")
            print(f"🕒 Timestamp: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")

    def _display_enhanced_action_history(self):
        """Display enhanced action history with better formatting."""
        print("\n" + "="*80)
        print("📜 ACTION HISTORY - LAST 15 ACTIONS")
        print("="*80)
        
        if not self.action_history:
            print("📭 No actions recorded yet")
            return
            
        recent_actions = self.action_history[-15:]
        for i, action in enumerate(recent_actions, 1):
            status_icon = "✅" if action.success else "❌"
            duration_str = f"{action.duration:.2f}s"
            timestamp_str = action.timestamp.strftime("%H:%M:%S")
            
            print(f"{i:2d}. {status_icon} {action.action_type:<12} | {timestamp_str} | {duration_str:>6} | {action.message[:50]}...")
            
        print("="*80)

    def _generate_enhanced_report(self):
        """Generate enhanced session report with better feedback."""
        print("\n📄 Generating comprehensive session report...")
        try:
            report_path = self.generate_session_report()
            if report_path:
                print(f"✅ Report generated successfully!")
                print(f"📁 File: {report_path}")
                print(f"🌐 Open in browser to view detailed analytics")
            else:
                print("❌ Failed to generate report")
        except Exception as e:
            print(f"❌ Report generation failed: {e}")

    def _display_enhanced_session_stats(self):
        """Display enhanced session statistics with better formatting."""
        current_time = datetime.now()
        session_duration = (current_time - self.session_data['start_time']).total_seconds()
        success_rate = (self.session_data['successful_actions'] / max(1, self.session_data['total_actions'])) * 100
        
        print("\n" + "="*70)
        print("📊 ENHANCED SESSION STATISTICS")
        print("="*70)
        print(f"🕐 Session Duration:    {session_duration//60:.0f}m {session_duration%60:.0f}s")
        print(f"🎯 Total Actions:       {self.session_data['total_actions']}")
        print(f"✅ Successful Actions:  {self.session_data['successful_actions']}")
        print(f"📈 Success Rate:        {success_rate:.1f}%")
        print(f"🌐 Websites Visited:    {len(self.session_data['websites_visited'])}")
        print(f"📝 Forms Filled:        {self.session_data.get('forms_filled', 0)}")
        print(f"🔍 Searches Performed:  {self.session_data.get('searches_performed', 0)}")
        print(f"📸 Screenshots Taken:   {len([a for a in self.action_history if a.screenshot_path])}")
        print(f"⚡ Avg Action Duration: {sum(a.duration for a in self.action_history)/max(1, len(self.action_history)):.2f}s")
        
        # Performance indicators
        if success_rate >= 80:
            print("🏆 Performance: EXCELLENT")
        elif success_rate >= 60:
            print("👍 Performance: GOOD")
        elif success_rate >= 40:
            print("⚠️  Performance: FAIR")
        else:
            print("🔧 Performance: NEEDS IMPROVEMENT")
            
        print("="*70)

    def _display_enhanced_help(self):
        """Display enhanced help with organized sections."""
        print("\n" + "="*80)
        print("❓ MEGA ADVANCED AI BROWSER AGENT - COMPREHENSIVE HELP")
        print("="*80)
        
        print("\n🎯 NATURAL LANGUAGE COMMANDS:")
        print("   • \"go to google.com and search for artificial intelligence\"")
        print("   • \"open youtube.com and find programming tutorials\"")
        print("   • \"navigate to amazon.com and search for laptops\"")
        print("   • \"fill out the contact form on this page\"")
        print("   • \"click the login button and enter my credentials\"")
        
        print("\n🎮 QUICK COMMANDS:")
        print("   📊 info         - Show current page information")
        print("   📸 screenshot   - Take annotated screenshot")
        print("   📜 history      - Show recent action history")
        print("   📄 report       - Generate HTML session report")
        print("   📈 stats        - Display session statistics")
        print("   💬 chat         - Demo chat interface")
        print("   🔐 captcha      - Solve CAPTCHA on current page")
        print("   📋 extract      - Extract all data from page")
        print("   🎮 record       - Start/stop macro recording")
        print("   ⚡ monitor      - Monitor page performance")
        print("   🎨 menu         - Show main menu")
        print("   🚪 exit         - Quit the agent")
        
        print("\n🔧 ADVANCED FEATURES:")
        print("   • Multi-LLM support (Mistral, OpenAI, Anthropic, Gemini)")
        print("   • Automatic CAPTCHA solving (Cloudflare, reCAPTCHA)")
        print("   • Smart form filling with AI assistance")
        print("   • Macro recording and playback")
        print("   • Performance monitoring and optimization")
        print("   • Advanced data extraction (tables, emails, phones)")
        print("   • Multi-browser parallel processing")
        print("   • Network request interception")
        
        print("="*80)

    def _demo_enhanced_chat_interface(self):
        """Demo enhanced chat interface."""
        print("\n💬 Demonstrating enhanced chat interface...")
        self.show_complete_chat_interface(
            "This is a demo of the enhanced AI chat interface with modern styling!",
            position="center",
            show_typing=True
        )
        print("✅ Chat interface demo completed")

    def _handle_captcha_command(self):
        """Handle CAPTCHA solving command."""
        print("\n🔐 Scanning for CAPTCHAs on current page...")
        if self.solve_captcha_on_page():
            print("✅ CAPTCHA solved successfully!")
        else:
            print("ℹ️  No CAPTCHAs found on current page")

    def _handle_extract_command(self):
        """Handle data extraction command."""
        print("\n📋 Extracting all data from current page...")
        try:
            data = self.extract_all_data()
            print(f"✅ Data extraction completed!")
            print(f"📊 Found: {len(data.get('tables', []))} tables, {len(data.get('links', []))} links")
            print(f"📧 Emails: {len(data.get('emails', []))}, 📞 Phones: {len(data.get('phones', []))}")
        except Exception as e:
            print(f"❌ Data extraction failed: {e}")

    def _handle_record_command(self, command):
        """Handle macro recording commands."""
        parts = command.split()
        if len(parts) == 1:
            print("\n🎮 Usage: 'record start [name]' or 'record stop'")
        elif parts[1] == 'start':
            name = parts[2] if len(parts) > 2 else f"macro_{datetime.now().strftime('%H%M%S')}"
            print(f"\n🎮 Starting macro recording: {name}")
            self.record_macro(name)
        elif parts[1] == 'stop':
            print("\n🎮 Stopping macro recording...")
            result = self.stop_macro_recording()
            print(f"✅ Macro saved with {len(result.get('steps', []))} steps")

    def _handle_monitor_command(self, command):
        """Handle performance monitoring command."""
        parts = command.split()
        duration = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 30
        print(f"\n⚡ Starting performance monitoring for {duration} seconds...")
        try:
            metrics = self.monitor_performance(duration)
            print(f"✅ Performance monitoring completed - {len(metrics)} data points collected")
        except Exception as e:
            print(f"❌ Performance monitoring failed: {e}")

    def run(self):
        """Main execution loop with advanced features."""
        self._display_welcome_banner()
        self._display_main_menu()

        while True:
            try:
                objective = input("\n🎯 Enter command or objective > ").strip()
                
                if objective.lower() == 'exit':
                    break
                elif objective.lower() == 'menu':
                    self._display_main_menu()
                    continue
                elif objective.lower() == 'info':
                    self._display_enhanced_page_info()
                    continue
                elif objective.lower() == 'screenshot':
                    self._take_enhanced_screenshot()
                    continue
                elif objective.lower() == 'history':
                    self._display_enhanced_action_history()
                    continue
                elif objective.lower() == 'report':
                    self._generate_enhanced_report()
                    continue
                elif objective.lower() == 'stats':
                    self._display_enhanced_session_stats()
                    continue
                elif objective.lower() == 'help':
                    self._display_enhanced_help()
                    continue
                elif objective.lower() == 'chat':
                    self._demo_enhanced_chat_interface()
                    continue
                elif objective.lower() == 'captcha':
                    self._handle_captcha_command()
                    continue
                elif objective.lower() == 'extract':
                    self._handle_extract_command()
                    continue
                elif objective.lower().startswith('record'):
                    self._handle_record_command(objective)
                    continue
                elif objective.lower().startswith('monitor'):
                    self._handle_monitor_command(objective)
                    continue
                elif not objective:
                    continue

                # Initialize task
                last_action_feedback = "🎬 Starting new objective with advanced AI analysis..."
                
                # Demo the complete chat interface with the new objective
                self.show_complete_chat_interface(
                    f"Processing your request: {objective[:100]}{'...' if len(objective) > 100 else ''}",
                    position="top-left",
                    show_typing=True
                )
                
                # Check if we need to navigate
                current_url = self.driver.current_url
                if "about:blank" in current_url or current_url == "data:,":
                    url_to_open = self._extract_url_from_command(objective)
                    if url_to_open:
                        print(f"🔍 Detected URL in objective. Opening {url_to_open}...")
                        navigate_decision = {
                            "action": {"name": "NAVIGATE", "parameters": {"url": url_to_open}}
                        }
                        result = self.execute_advanced_action(navigate_decision)
                        last_action_feedback = result.message
                        if not result.success:
                            print(f"❌ Navigation failed: {result.message}")
                            continue
                    else:
                        print("⚠️ Please provide a URL or be more specific about the website to visit.")
                        continue

                # Main execution loop with advanced features
                print(f"\n🚀 Starting objective: '{objective}'")
                print(f"⏱️ Timeout: 8 minutes, Max steps: 50")
                
                start_time = time.time()
                # Auto-adaptive step limits based on objective complexity
                objective_length = len(objective.split())
                if objective_length <= 5:
                    max_steps = 100  # Simple tasks
                elif objective_length <= 15:
                    max_steps = 200  # Medium complexity
                else:
                    max_steps = 500  # Complex multi-step tasks
                
                # Dynamic timeout based on complexity
                task_timeout = min(300, max(60, objective_length * 10))  # 1-5 minutes
                task_timeout = 480  # 8 minutes
                consecutive_failures = 0
                max_consecutive_failures = 5  # Increased tolerance
                action_retry_count = 0
                max_action_retries = 2
                step_counter = 0

                while time.time() - start_time < task_timeout and step_counter < max_steps:
                    step_counter += 1
                    print(f"\n--- 🔄 Step {step_counter}/{max_steps} ---")
                    
                    try:
                        # Get advanced elements with confidence scoring (faster detection)
                        retry_count = 0
                        max_retries = 2  # Reduced retries for speed
                        
                        while retry_count < max_retries:
                            # Clear cache for fresh detection
                            self.elements_cache = []
                            self.elements_cache = self._get_advanced_interactive_elements()
                            if self.elements_cache or retry_count == max_retries - 1:
                                break
                            print(f"⏳ No elements found, retrying... ({retry_count + 1}/{max_retries})")
                            time.sleep(1)  # Reduced wait time
                            retry_count += 1
                        
                        if not self.elements_cache:
                            print("⚠️ No interactive elements found. Checking for CAPTCHA...")
                            # Try to solve CAPTCHA if present
                            if self.solve_captcha_on_page():
                                print("✅ CAPTCHA solved! Retrying element detection...")
                                time.sleep(2)  # Wait for page to reload after CAPTCHA
                                continue
                            else:
                                print("⚠️ No CAPTCHA found. Waiting for page to load...")
                                time.sleep(3)
                                continue
                        
                        print(f"🔍 Found {len(self.elements_cache)} interactive elements (avg confidence: {sum(e.confidence_score for e in self.elements_cache)/len(self.elements_cache):.2f})")
                        
                        # Take advanced screenshot and annotate
                        screenshot_png = self.get_screenshot_as_png()
                        annotated_screenshot = self._draw_advanced_labels_on_image(screenshot_png, self.elements_cache)
                        annotated_screenshot_b64 = base64.b64encode(annotated_screenshot).decode('utf-8')
                        
                        # Get AI decision with advanced analysis
                        decision = self.decide_next_action(
                            objective, annotated_screenshot_b64, self.elements_cache, last_action_feedback
                        )
                        
                        if not decision or not decision.get('action'):
                            print("❌ Failed to get AI decision")
                            consecutive_failures += 1
                            if consecutive_failures >= max_consecutive_failures:
                                break
                            continue
                        
                        thought = decision.get('thought', 'No analysis provided')
                        confidence = decision.get('confidence', 0.5)
                        reasoning = decision.get('reasoning', 'No reasoning provided')
                        
                        print(f"🤔 AI Analysis: {thought}")
                        print(f"🎯 Confidence: {confidence:.2f} | Reasoning: {reasoning[:100]}...")
                        
                        # Execute advanced action
                        result = self.execute_advanced_action(decision)
                        print(f"📋 Result: {result.message}")
                        
                        if result.message == "🏁 Task finished.":
                            print(f"\n🎉 Objective completed successfully in {step_counter} steps!")
                            print(f"📊 Success Rate: {self.session_data['successful_actions']}/{self.session_data['total_actions']} ({(self.session_data['successful_actions']/max(1, self.session_data['total_actions'])*100):.1f}%)")
                            break
                        
                        if not result.success:
                            action_retry_count += 1
                            if action_retry_count <= max_action_retries:
                                print(f"🔄 Action failed, retrying... ({action_retry_count}/{max_action_retries})")
                                time.sleep(random.uniform(1.0, 2.0))  # Brief delay before retry
                                continue  # Retry the same action
                            else:
                                consecutive_failures += 1
                                action_retry_count = 0  # Reset retry count for next action
                                if consecutive_failures >= max_consecutive_failures:
                                    print(f"❌ Too many consecutive failures ({consecutive_failures}). Ending task.")
                                    break
                        else:
                            consecutive_failures = 0
                            action_retry_count = 0  # Reset retry count on success
                        
                        last_action_feedback = result.message
                        
                        # Human-like delay between actions
                        time.sleep(random.uniform(1.5, 2.5))
                        
                    except KeyboardInterrupt:
                        print("\n⏹️ Task interrupted by user.")
                        break
                    except Exception as e:
                        logger.error(f"Error in step {step_counter}: {e}")
                        consecutive_failures += 1
                        if consecutive_failures >= max_consecutive_failures:
                            print(f"💥 Critical errors occurred. Stopping task.")
                            break
                        continue
                
                else:
                    # Loop ended due to timeout or max steps
                    if step_counter >= max_steps:
                        print(f"⏹️ Task stopped after {max_steps} steps to prevent infinite loops.")
                    else:
                        print(f"⏱️ Task timed out after {task_timeout//60} minutes.")
                
                # Generate final report and save final screenshot
                final_screenshot = self.save_advanced_screenshot(f"final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                print(f"📸 Final screenshot saved: {final_screenshot}")
                
                # Show session summary
                self._display_session_stats()
                
            except KeyboardInterrupt:
                print("\n⏹️ Interrupted by user.")
                break
            except Exception as e:
                logger.error(f"Fatal error: {e}")
                print(f"💥 Fatal error: {e}")
                continue
        
        # Cleanup and final report
        try:
            print("\n📄 Generating final session report...")
            final_report = self.generate_session_report()
            if final_report:
                print(f"📊 Final report saved: {final_report}")
            
            self.driver.quit()
            print("🧹 Browser closed successfully.")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        print("👋 Mega Advanced Browser Agent session ended. Thank you for using our advanced AI system!")

    def _get_page_info(self) -> Dict:
        """Get detailed page information."""
        try:
            return {
               
                "url": self.driver.current_url,
                "title": self.driver.title,
                "elements_count": len(self.elements_cache),
                "visible_elements": sum(1 for e in self.elements_cache if e.is_visible),
                "form_fields": sum(1 for e in self.elements_cache if e.is_form_field),
                "clickable_elements": sum(1 for e in self.elements_cache if e.is_clickable),
                "avg_confidence": sum(e.confidence_score for e in self.elements_cache) / len(self.elements_cache) if self.elements_cache else 0,
                "page_load_state": self.driver.execute_script('return document.readyState'),
                "session_stats": self.session_data
            }
        except Exception as e:
            return {"error": str(e)}

    def _display_action_history(self):
        """Display recent action history."""
        print(f"\n📜 Action History ({len(self.action_history)} total actions):")
        print("-" * 80)
        
        recent_actions = self.action_history[-15:]  # Show last 15 actions
        for i, action in enumerate(recent_actions, 1):
            status_icon = "✅" if action.success else "❌"
            duration_str = f"{action.duration:.2f}s"
            timestamp_str = action.timestamp.strftime("%H:%M:%S")
            
            print(f"{i:2d}. {status_icon} {action.action_type:<12} | {timestamp_str} | {duration_str:>6} | {action.message}")
            
        print("-" * 80)

    def _display_session_stats(self):
        """Display comprehensive session statistics."""
        current_time = datetime.now()
        session_duration = (current_time - self.session_data['start_time']).total_seconds()
        success_rate = (self.session_data['successful_actions'] / max(1, self.session_data['total_actions'])) * 100
        
        print(f"\n📊 SESSION STATISTICS")
        print("=" * 50)
        print(f"🕐 Session Duration: {session_duration//60:.0f}m {session_duration%60:.0f}s")
        print(f"🎯 Total Actions: {self.session_data['total_actions']}")
        print(f"✅ Successful Actions: {self.session_data['successful_actions']}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"🌐 Websites Visited: {len(self.session_data['websites_visited'])}")
        print(f"📝 Forms Filled: {self.session_data.get('forms_filled', 0)}")
        print(f"🔍 Searches Performed: {self.session_data.get('searches_performed', 0)}")
        print(f"📸 Screenshots Taken: {len([a for a in self.action_history if a.screenshot_path])}")
        print(f"⚡ Avg Action Duration: {sum(a.duration for a in self.action_history)/max(1, len(self.action_history)):.2f}s")
        print("=" * 50)

    def _display_help(self):
        """Display comprehensive help information."""
        print("""
🎯 MEGA ADVANCED BROWSER AGENT - HELP (100+ FEATURES)

📝 NATURAL LANGUAGE COMMANDS:
   • "open google.com and search for artificial intelligence"
   • "go to youtube.com and find programming tutorials"
   • "navigate to amazon.com and search for laptops"
   • "fill out the contact form on this page"
   • "click the login button and enter my credentials"

🆕 NEW POWERFUL COMMANDS:
   • captcha         - Automatically solve CAPTCHA on current page
   • extract         - Extract all data (tables, emails, phones, links)
   • record [name]   - Start recording macro with optional name
   • stop            - Stop macro recording
   • replay [name]   - Replay a saved macro
   • performance     - Monitor page performance for 30 seconds
   • fill key=value  - Smart form filling (e.g., fill email=test@example.com)
   • popups          - Automatically handle popups and modals
   • workflow [name] - Execute a saved workflow
   • parallel        - Demo parallel task execution (multi-browser)
   • block [pattern] - Block network requests matching pattern
   • intercept       - Enable network request interception
   • tables          - Extract all tables to Excel
   • monitor [sec]   - Monitor performance for specified seconds

🔧 SPECIAL COMMANDS:
   • 'exit' - Quit the agent
   • 'info' - Show detailed page information
   • 'screenshot' - Take an annotated screenshot
   • 'history' - Show recent action history
   • 'report' - Generate HTML session report
   • 'stats' - Display session statistics
   • 'chat' - Demo the new chat interface
   • 'help' - Show this help message

🎨 VISUAL FEATURES:
   • Human-like cursor movement (8-step animations)
   • Real-time AI analysis bubbles
   • Progress indicators and status bars
   • Element confidence scoring
   • Professional screenshot annotations

🛠️ ADVANCED CAPABILITIES:
   • 20+ intelligent actions with error recovery
   • Auto-detection of input fields
   • Advanced element analysis
   • Multi-strategy clicking
   • JavaScript execution
   • Form filling automation
   • Smart error handling

💡 TIPS FOR BEST RESULTS:
   1. Be specific: "Search for Python tutorials on YouTube"
   2. Break down complex tasks into smaller steps
   3. Use natural language descriptions
   4. Monitor the AI analysis bubbles for insights
   5. Check session stats regularly for performance

🚀 EXAMPLE ADVANCED TASKS:
   • "Open LinkedIn, search for AI jobs in San Francisco"
   • "Go to Wikipedia and research quantum computing"
   • "Navigate to GitHub and find trending Python projects"
   • "Open Twitter and compose a tweet about AI"
        """)

    def _demo_chat_interface(self):
        """Demonstrate the clean, minimal chat interface features."""
        print("\n🎨 === CHAT INTERFACE DEMO ===")
        print("Demonstrating the new clean, minimal chat bubble design...")
        
        try:
            # Demo 1: Basic chat bubble
            print("\n1. 📱 Basic Chat Bubble")
            self.show_chat_bubble(
                "Hello! I'm your AI assistant. This is a clean, minimal chat interface with modern design.",
                position="top-right",
                duration=4000
            )
            time.sleep(2)
            
            # Demo 2: Different positions
            print("2. 📍 Different Positions")
            positions = ["top-left", "top-right", "bottom-left", "bottom-right"]
            messages = [
                "Top-left position with professional styling.",
                "Top-right with smooth animations.",
                "Bottom-left with subtle shadows.",
                "Bottom-right with clean typography."
            ]
            
            for pos, msg in zip(positions, messages):
                self.show_chat_bubble(msg, position=pos, duration=3000)
                time.sleep(1.5)
            
            time.sleep(2)
            
            # Demo 3: Typing indicator
            print("3. ⌨️ Typing Indicator")
            self.show_typing_indicator("top-right")
            time.sleep(3)
            self.hide_typing_indicator()
            
            # Demo 4: AI response with typing effect
            print("4. 🤖 AI Response with Typing Effect")
            self.show_ai_response(
                "This demonstrates the complete AI response flow. The typing indicator appears first, then this message slides in smoothly with professional styling.",
                position="top-right",
                show_typing=True,
                typing_delay=2.0
            )
            
            time.sleep(3)
            
            # Demo 5: Message updates
            print("5. 🔄 Dynamic Message Updates")
            self.show_chat_bubble("Initial message...", position="bottom-right", duration=0)
            time.sleep(1)
            
            for i, update in enumerate([
                "Updating message content...",
                "Messages can be dynamically updated.",
                "Final message with clean design!"
            ], 1):
                time.sleep(1.5)
                self.update_chat_bubble(update)
                print(f"   Updated to message {i}")
            
            time.sleep(2)
            self.remove_chat_bubble()
            
            print("\n✨ Chat Interface Demo Complete!")
            print("Features demonstrated:")
            print("   • Clean, minimal design with rounded corners")
            print("   • Subtle drop shadows and modern typography")
            print("   • Smooth animations and transitions")
            print("   • Multiple positioning options")
            print("   • Typing indicators for better UX")
            print("   • Dynamic message updates")
            print("   • Professional Inter/Arial font styling")
            print("   • First sentence bold formatting")
            print("   • Triangle pointer connection to AI avatar")
            
        except Exception as e:
            print(f"❌ Demo error: {e}")
            logger.error(f"Chat interface demo error: {e}")

    def cleanup(self):
        """Clean up resources and close browser."""
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
                logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    try:
        # Initialize with advanced settings and new powerful features
        agent = MegaAdvancedBrowserAgent(
            headless=False,
            window_size=(1920, 1080),
            enable_extensions=True,
            enable_ai=True,  # Enable AI features
            multi_browser=False,  # Set to True for parallel processing
            browser_count=1  # Number of browser instances for parallel tasks
        )
        agent.run()
    except KeyboardInterrupt:
        print("\n⏹️ Program interrupted by user.")
        if 'agent' in locals():
            agent.cleanup()
    except Exception as e:
        logger.error(f"Fatal error initializing agent: {e}")
        print(f"💥 Fatal error: {e}")
        print("Please check the logs/mega_browser_agent.log file for detailed error information.")
