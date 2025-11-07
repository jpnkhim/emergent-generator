#!/usr/bin/env python3
"""
Emergent.sh Account Generator
Adapted for web service usage
"""

import requests
import json
import random
import string
import re
import time
import logging
from typing import Dict, Optional
from datetime import datetime
from urllib.parse import urljoin, urlencode
from mailpytm import MailTMApi

logger = logging.getLogger(__name__)


class EmergentAccountGenerator:
    """Generate Emergent.sh accounts with email verification"""
    
    BASE_URL = "https://app.emergent.sh"
    FALLBACK_SUPABASE_URL = "https://snksxwkyumhdykyrhhch.supabase.co"
    FALLBACK_SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNua3N4d2t5dW1oZHlreXJoaGNoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjQ3NzI2NDYsImV4cCI6MjA0MDM0ODY0Nn0.3unO6zdz2NilPL2xdxt7OjvZA19copj3Q7ulIjPVDLQ"
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        if debug:
            logger.setLevel(logging.DEBUG)
        
        self.session = requests.Session()
        self._configure_session()
        
        self.supabase_url = None
        self.supabase_anon_key = None
        self.supabase_api_version = "2024-01-01"
        self.email_account = None
    
    def _configure_session(self):
        """Configure session with realistic headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'DNT': '1',
            'Sec-GPC': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
        })
    
    @staticmethod
    def generate_random_password() -> str:
        """Generate strong password"""
        lowercase = random.choices(string.ascii_lowercase, k=4)
        uppercase = random.choices(string.ascii_uppercase, k=3)
        digits = random.choices(string.digits, k=3)
        special = random.choices('!@#$%^&*', k=2)
        
        all_chars = lowercase + uppercase + digits + special
        random.shuffle(all_chars)
        return ''.join(all_chars)
    
    def create_temporary_email(self, max_retries: int = 3) -> Optional[str]:
        """Create temporary email using mail.tm"""
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Creating temporary email (attempt {attempt}/{max_retries})...")
                self.email_account = MailTMApi.create_email()
                logger.info(f"Temporary email created: {self.email_account.address}")
                return self.email_account.address
            except Exception as e:
                logger.warning(f"Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    wait_time = 2 * attempt
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to create temporary email after {max_retries} attempts")
                    return None
        return None
    
    def extract_supabase_credentials(self) -> bool:
        """Extract Supabase credentials from website or use fallback"""
        try:
            logger.info("Extracting Supabase credentials...")
            response = self.session.get(self.BASE_URL, timeout=10)
            
            if response.status_code != 200:
                return self._fallback_credentials()
            
            script_patterns = [
                r'src="([^"]*app-[a-f0-9]+\.js)"',
                r'src="([^"]*framework-[a-f0-9]+\.js)"',
                r'src="([^"]*main-[a-f0-9]+\.js)"',
                r'<script[^>]*src="([^"]*\.js)"'
            ]
            
            js_bundle_urls = []
            for pattern in script_patterns:
                matches = re.findall(pattern, response.text)
                for match in matches:
                    full_url = urljoin(self.BASE_URL, match)
                    if full_url not in js_bundle_urls:
                        js_bundle_urls.append(full_url)
            
            if not js_bundle_urls:
                return self._fallback_credentials()
            
            for js_bundle_url in js_bundle_urls:
                try:
                    js_response = self.session.get(
                        js_bundle_url, 
                        timeout=15,
                        headers={'Accept-Encoding': 'gzip, deflate'}
                    )
                    
                    if js_response.status_code != 200:
                        continue
                    
                    js_content = js_response.text
                    url_pattern = r'https://([a-z0-9]+)\.supabase\.co'
                    url_matches = re.findall(url_pattern, js_content)
                    jwt_pattern = r'eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}'
                    jwt_matches = re.findall(jwt_pattern, js_content)
                    
                    if url_matches and jwt_matches:
                        self.supabase_url = f"https://{url_matches[0]}.supabase.co"
                        
                        best_jwt = None
                        for jwt in jwt_matches:
                            try:
                                import base64
                                payload = jwt.split('.')[1]
                                payload += '=' * (4 - len(payload) % 4)
                                decoded = base64.b64decode(payload).decode('utf-8', errors='ignore')
                                
                                if '"role":"anon"' in decoded or 'role":"anon' in decoded:
                                    best_jwt = jwt
                                    break
                                elif 'supabase' in decoded.lower():
                                    best_jwt = jwt
                            except:
                                continue
                        
                        self.supabase_anon_key = best_jwt if best_jwt else jwt_matches[0]
                        
                        if len(self.supabase_anon_key) > 100:
                            logger.info("Credentials extracted successfully")
                            return True
                        
                except Exception as e:
                    if self.debug:
                        logger.debug(f"Error processing bundle: {e}")
                    continue
            
            return self._fallback_credentials()
            
        except Exception as e:
            logger.error(f"Error extracting credentials: {e}")
            return self._fallback_credentials()
    
    def _fallback_credentials(self) -> bool:
        """Use fallback credentials"""
        logger.info("Using fallback credentials...")
        self.supabase_url = self.FALLBACK_SUPABASE_URL
        self.supabase_anon_key = self.FALLBACK_SUPABASE_KEY
        return True
    
    def build_payload(self, email: str, password: str) -> Dict:
        """Build registration payload"""
        username = email.split('@')[0]
        
        payload = {
            "email": email,
            "password": password,
            "data": {
                "name": username
            },
            "gotrue_meta_security": {},
            "code_challenge": None,
            "code_challenge_method": None
        }
        
        return payload
    
    def register(self, email: str, password: str) -> Dict:
        """Register new account"""
        if not self.extract_supabase_credentials():
            return {
                'success': False,
                'error': 'Failed to get Supabase credentials'
            }
        
        redirect_to = f"{self.BASE_URL}/home"
        signup_url = f"{self.supabase_url}/auth/v1/signup"
        params = {'redirect_to': redirect_to}
        signup_url_with_params = f"{signup_url}?{urlencode(params)}"
        
        payload = self.build_payload(email, password)
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.supabase_anon_key}',
            'apikey': self.supabase_anon_key,
            'X-Client-Info': 'supabase-js-web/2.78.0',
            'X-Supabase-Api-Version': self.supabase_api_version,
            'Origin': self.BASE_URL,
            'Referer': f'{self.BASE_URL}/',
        }
        
        try:
            logger.info("Sending registration request...")
            
            response = self.session.post(
                signup_url_with_params,
                json=payload,
                headers=headers,
                timeout=15,
                allow_redirects=False
            )
            
            logger.info(f"Status Code: {response.status_code}")
            
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {'raw_text': response.text[:500]}
            
            if response.status_code in [200, 201]:
                logger.info("Registration successful")
                
                return {
                    'success': True,
                    'email': email,
                    'password': password,
                    'status_code': response.status_code,
                    'response_data': response_data,
                }
            else:
                error_msg = 'Registration failed'
                if isinstance(response_data, dict):
                    error_msg = response_data.get('error_description', 
                                response_data.get('message', 
                                response_data.get('msg', error_msg)))
                
                logger.error(f"Registration failed: {error_msg}")
                
                return {
                    'success': False,
                    'email': email,
                    'error': error_msg,
                    'status_code': response.status_code,
                    'response_data': response_data
                }
        
        except Exception as e:
            logger.exception("Error during registration")
            return {
                'success': False,
                'email': email,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def wait_for_verification_email(self, timeout: int = 60, check_interval: int = 3) -> Optional[Dict]:
        """Wait for verification email"""
        try:
            logger.info(f"Waiting for verification email (timeout: {timeout}s)...")
            end_time = time.time() + timeout
            
            while time.time() < end_time:
                try:
                    messages = self.email_account.messages
                    
                    for msg in messages:
                        subject = msg.get('subject', '').lower()
                        if 'confirm' in subject or 'verify' in subject or 'emergent' in subject:
                            logger.info("Verification email received")
                            message_id = msg.get('id')
                            full_message = self.email_account.get_message_by_id(message_id)
                            return full_message
                    
                    remaining = int(end_time - time.time())
                    if remaining > 0:
                        time.sleep(check_interval)
                    
                except Exception as e:
                    logger.warning(f"Error checking messages: {e}")
                    time.sleep(check_interval)
            
            logger.warning(f"No verification email within {timeout}s")
            return None
            
        except Exception as e:
            logger.error(f"Error waiting for email: {e}")
            return None
    
    def extract_verification_url(self, message: Dict) -> Optional[str]:
        """Extract verification URL from email"""
        try:
            logger.info("Extracting verification URL...")
            
            html_content = message.get('html', [''])[0] if message.get('html') else ''
            text_content = message.get('text', '')
            content = html_content + '\n' + text_content
            
            direct_patterns = [
                r'https://app\.emergent\.sh/auth/confirm\?[^\s<>"\']+ ',
                r'https://app\.emergent\.sh/activate[^\s<>"\']* ',
                r'https://[^/]+\.supabase\.co/auth/v1/verify\?[^\s<>"\']+ ',
            ]
            
            for pattern in direct_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    url = matches[0]
                    url = re.sub(r'[,;.!?\]}>]+$', '', url)
                    url = url.replace('&amp;', '&')
                    logger.info("Found verification URL")
                    return url
            
            href_pattern = r'href="([^"]+)"'
            href_matches = re.findall(href_pattern, html_content)
            
            text_url_patterns = [r'\[?(https://[^\s\]<>"\']+ )\]?']
            for pattern in text_url_patterns:
                text_matches = re.findall(pattern, text_content)
                href_matches.extend(text_matches)
            
            potential_urls = []
            for url in href_matches:
                url_lower = url.lower()
                if 'tr/op/' in url or 'width=' in url or 'height=' in url:
                    continue
                if any(keyword in url_lower for keyword in ['tr/cl/', 'confirm', 'verify', 'activate', 'click']):
                    potential_urls.append(url)
            
            if potential_urls:
                url = potential_urls[0].replace('&amp;', '&')
                logger.info("Found redirect URL")
                return url
            
            logger.warning("Could not find verification URL")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting URL: {e}")
            return None
    
    def visit_verification_url(self, url: str) -> bool:
        """Visit verification URL"""
        try:
            logger.info("Visiting verification URL...")
            response = self.session.get(url, timeout=15, allow_redirects=True)
            
            if response.status_code == 200:
                logger.info("Verification successful")
                return True
            else:
                logger.warning(f"Verification returned status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error visiting verification URL: {e}")
            return False
    
    def generate_account(self) -> Dict:
        """Complete account generation with verification"""
        result = {
            'success': False,
            'steps_completed': []
        }
        
        try:
            # Create temporary email
            email = self.create_temporary_email(max_retries=3)
            if not email:
                result['error'] = 'Failed to create temporary email'
                return result
            
            result['email'] = email
            result['steps_completed'].append('temp_email_created')
            
            # Generate password
            password = self.generate_random_password()
            result['password'] = password
            result['steps_completed'].append('password_generated')
            
            # Register account
            reg_result = self.register(email, password)
            if not reg_result['success']:
                result['error'] = reg_result.get('error', 'Registration failed')
                result['registration_response'] = reg_result
                return result
            
            result['registration_response'] = reg_result
            result['steps_completed'].append('account_registered')
            
            # Wait for verification email
            message = self.wait_for_verification_email(timeout=60, check_interval=3)
            if not message:
                result['error'] = 'Verification email not received'
                result['warning'] = 'Account created but not verified'
                return result
            
            result['verification_email_received'] = True
            result['steps_completed'].append('verification_email_received')
            
            # Extract verification URL
            verification_url = self.extract_verification_url(message)
            if not verification_url:
                result['error'] = 'Could not extract verification URL'
                result['warning'] = 'Account created but not verified'
                return result
            
            result['verification_url'] = verification_url
            result['steps_completed'].append('verification_url_extracted')
            
            # Visit verification URL
            verified = self.visit_verification_url(verification_url)
            if not verified:
                result['error'] = 'Verification failed'
                result['warning'] = 'Could not complete verification'
                return result
            
            result['verified'] = True
            result['steps_completed'].append('account_verified')
            result['success'] = True
            result['message'] = 'Account fully registered and verified!'
            
            return result
            
        except Exception as e:
            logger.exception("Error in account generation")
            result['error'] = str(e)
            return result
        
        finally:
            # Cleanup temporary email
            if self.email_account:
                try:
                    self.email_account.delete_account()
                    logger.info("Temporary email deleted")
                except Exception as e:
                    logger.debug(f"Could not delete email: {e}")
