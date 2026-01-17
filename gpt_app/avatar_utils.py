"""
Avatar generation utility for creating user-specific avatars
"""
import hashlib
from django.utils.text import slugify


def get_user_initials(full_name, username):
    """Get user initials from full name or username"""
    if full_name and full_name.strip():
        names = full_name.strip().split()
        initials = ''.join([name[0].upper() for name in names])[:2]
    else:
        initials = username[:2].upper()
    return initials


def get_user_color(username):
    """Generate a consistent color based on username using MD5 hash"""
    hash_object = hashlib.md5(username.encode())
    hash_hex = hash_object.hexdigest()
    
    # Color palette - vibrant colors
    colors = [
        '#FF6B6B',  # Red
        '#4ECDC4',  # Teal
        '#45B7D1',  # Blue
        '#FFA07A',  # Light Salmon
        '#98D8C8',  # Mint
        '#F7DC6F',  # Yellow
        '#BB8FCE',  # Purple
        '#85C1E2',  # Light Blue
        '#F8B88B',  # Peach
        '#52C9A6',  # Green
    ]
    
    # Use hash to pick a color consistently
    color_index = int(hash_hex[:2], 16) % len(colors)
    return colors[color_index]


def generate_avatar_svg(full_name, username, size=200):
    """Generate an SVG avatar with initials"""
    initials = get_user_initials(full_name, username)
    bg_color = get_user_color(username)
    
    svg = f'''<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <style>
          .avatar-bg {{ fill: {bg_color}; }}
          .avatar-text {{ font-size: {int(size * 0.4)}px; font-weight: bold; fill: white; text-anchor: middle; vertical-align: middle; font-family: Arial, sans-serif; }}
        </style>
      </defs>
      <rect class="avatar-bg" width="{size}" height="{size}" rx="10"/>
      <text class="avatar-text" x="{size/2}" y="{size/2 + int(size * 0.15)}">{initials}</text>
    </svg>'''
    
    return svg


def generate_bot_logo_svg(size=200):
    """Generate a bot logo SVG"""
    svg = f'''<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
      <defs>
        <linearGradient id="botGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#00f5c9;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#00c3ff;stop-opacity:1" />
        </linearGradient>
      </defs>
      <!-- Head -->
      <rect x="50" y="40" width="100" height="90" rx="10" fill="url(#botGradient)"/>
      <!-- Eyes -->
      <circle cx="75" cy="65" r="6" fill="white"/>
      <circle cx="125" cy="65" r="6" fill="white"/>
      <!-- Mouth -->
      <path d="M 80 85 Q 100 95 120 85" stroke="white" stroke-width="3" fill="none" stroke-linecap="round"/>
      <!-- Body -->
      <rect x="60" y="130" width="80" height="50" rx="5" fill="url(#botGradient)"/>
      <!-- Arms -->
      <rect x="30" y="145" width="30" height="15" rx="7" fill="url(#botGradient)"/>
      <rect x="140" y="145" width="30" height="15" rx="7" fill="url(#botGradient)"/>
      <!-- Antenna -->
      <line x1="100" y1="40" x2="100" y2="10" stroke="url(#botGradient)" stroke-width="4" stroke-linecap="round"/>
      <circle cx="100" cy="8" r="5" fill="url(#botGradient)"/>
    </svg>'''
    
    return svg
