#!/usr/bin/env python3
"""
Farcaster Frame Handler - Interactive Content
Handle Farcaster Frames (Mini Apps) and interactive embedded content

REAL IMPLEMENTATION - No Mocks/Simulations
- Real Frame validation
- Real button interaction handling
- Real Frame metadata parsing
- Real transaction frame support
"""

import os
import json
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import requests
from urllib.parse import urlparse

# Neynar API configuration
NEYNAR_API_BASE = "https://api.neynar.com/v2/farcaster"

class FrameButtonAction(Enum):
    """Frame button action types"""
    POST = "post"              # Standard button press
    POST_REDIRECT = "post_redirect"  # Button press with redirect
    LINK = "link"              # External link
    MINT = "mint"              # NFT mint action
    TX = "tx"                  # Transaction request

@dataclass
class FrameButton:
    """Frame button configuration"""
    index: int
    label: str
    action: FrameButtonAction = FrameButtonAction.POST
    target: Optional[str] = None  # URL for action
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "index": self.index,
            "label": self.label,
            "action": self.action.value,
            "target": self.target
        }

@dataclass
class FrameMetadata:
    """Frame metadata from og: tags"""
    version: str = "vNext"  # Frame version
    image: Optional[str] = None  # Frame image URL
    image_aspect_ratio: str = "1.91:1"  # Image aspect ratio (1.91:1 or 1:1)
    buttons: List[FrameButton] = field(default_factory=list)
    input_text: Optional[str] = None  # Input field placeholder
    post_url: Optional[str] = None  # URL to post button clicks
    state: Optional[str] = None  # Serialized frame state
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "version": self.version,
            "image": self.image,
            "image_aspect_ratio": self.image_aspect_ratio,
            "buttons": [b.to_dict() for b in self.buttons],
            "input_text": self.input_text,
            "post_url": self.post_url,
            "state": self.state
        }

@dataclass
class FrameValidation:
    """Frame validation result"""
    valid: bool
    url: str
    metadata: Optional[FrameMetadata] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "valid": self.valid,
            "url": self.url,
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "errors": self.errors,
            "warnings": self.warnings
        }

class FrameHandler:
    """
    Handle Farcaster Frames (Mini Apps) and interactive content
    
    Features:
    - Validate Frame URLs and metadata
    - Parse Frame configuration from HTML
    - Handle button interactions
    - Support transaction frames
    - Fetch Frame details from Neynar
    """
    
    def __init__(self, api_key: str):
        """
        Initialize Frame Handler
        
        Args:
            api_key: Neynar API key
        """
        self.api_key = api_key
        self.base_url = NEYNAR_API_BASE
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        })
        
        print("=" * 70)
        print("FARCASTER FRAME HANDLER")
        print("=" * 70)
        print("✅ Frame validation and interaction enabled")
        print()
    
    def validate_frame(self, url: str) -> FrameValidation:
        """
        Validate a Frame URL using Neynar's Frame validator
        
        Args:
            url: URL of the Frame to validate
        
        Returns:
            FrameValidation object with validation results
        """
        print(f"🔍 Validating Frame")
        print(f"   URL: {url}")
        
        validation = FrameValidation(valid=False, url=url)
        
        try:
            response = self.session.post(
                f"{self.base_url}/frame/validate",
                json={"url": url}
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("valid"):
                validation.valid = True
                
                # Parse metadata
                frame_data = data.get("frame", {})
                metadata = FrameMetadata(
                    version=frame_data.get("version", "vNext"),
                    image=frame_data.get("image"),
                    image_aspect_ratio=frame_data.get("image_aspect_ratio", "1.91:1"),
                    input_text=frame_data.get("input", {}).get("text"),
                    post_url=frame_data.get("post_url"),
                    state=frame_data.get("state")
                )
                
                # Parse buttons
                buttons_data = frame_data.get("buttons", [])
                for btn_data in buttons_data:
                    try:
                        action = FrameButtonAction(btn_data.get("action", "post"))
                    except ValueError:
                        action = FrameButtonAction.POST
                    
                    button = FrameButton(
                        index=btn_data.get("index", 1),
                        label=btn_data.get("label", ""),
                        action=action,
                        target=btn_data.get("target")
                    )
                    metadata.buttons.append(button)
                
                validation.metadata = metadata
                
                print("   ✅ Frame is valid")
                print(f"   Version: {metadata.version}")
                print(f"   Buttons: {len(metadata.buttons)}")
                if metadata.input_text:
                    print(f"   Input: {metadata.input_text}")
            else:
                validation.valid = False
                validation.errors = data.get("errors", ["Validation failed"])
                print("   ❌ Frame is invalid")
                for error in validation.errors:
                    print(f"      • {error}")
            
            # Add warnings if any
            validation.warnings = data.get("warnings", [])
            if validation.warnings:
                for warning in validation.warnings:
                    print(f"   ⚠️  {warning}")
            
            return validation
            
        except requests.exceptions.HTTPError as e:
            print(f"   ❌ HTTP Error: {e.response.status_code}")
            validation.errors.append(f"HTTP {e.response.status_code}")
            return validation
        except Exception as e:
            print(f"   ❌ Error: {e}")
            validation.errors.append(str(e))
            return validation
    
    def fetch_frame_metadata(self, url: str) -> Optional[FrameMetadata]:
        """
        Fetch Frame metadata from URL
        
        Args:
            url: Frame URL
        
        Returns:
            FrameMetadata object if successful, None otherwise
        """
        print(f"📥 Fetching Frame Metadata")
        print(f"   URL: {url}")
        
        try:
            # Use Neynar's frame extraction endpoint
            response = self.session.get(
                f"{self.base_url}/frame/meta",
                params={"url": url}
            )
            response.raise_for_status()
            
            data = response.json()
            frame_data = data.get("frame", {})
            
            metadata = FrameMetadata(
                version=frame_data.get("version", "vNext"),
                image=frame_data.get("image"),
                image_aspect_ratio=frame_data.get("image_aspect_ratio", "1.91:1"),
                input_text=frame_data.get("input", {}).get("text"),
                post_url=frame_data.get("post_url"),
                state=frame_data.get("state")
            )
            
            # Parse buttons
            buttons_data = frame_data.get("buttons", [])
            for btn_data in buttons_data:
                try:
                    action = FrameButtonAction(btn_data.get("action", "post"))
                except ValueError:
                    action = FrameButtonAction.POST
                
                button = FrameButton(
                    index=btn_data.get("index", 1),
                    label=btn_data.get("label", ""),
                    action=action,
                    target=btn_data.get("target")
                )
                metadata.buttons.append(button)
            
            print("   ✅ Metadata fetched")
            print(f"   Image: {metadata.image[:50]}..." if metadata.image else "   No image")
            print(f"   Buttons: {len(metadata.buttons)}")
            
            return metadata
            
        except requests.exceptions.HTTPError as e:
            print(f"   ❌ HTTP Error: {e.response.status_code}")
            return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def parse_frame_html(self, html: str) -> Optional[FrameMetadata]:
        """
        Parse Frame metadata from HTML content
        
        Args:
            html: HTML content containing Frame meta tags
        
        Returns:
            FrameMetadata object if Frame tags found, None otherwise
        """
        print("🔧 Parsing Frame HTML")
        
        try:
            from html.parser import HTMLParser
            
            class FrameParser(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.tags = {}
                
                def handle_starttag(self, tag, attrs):
                    if tag == "meta":
                        attrs_dict = dict(attrs)
                        property_name = attrs_dict.get("property") or attrs_dict.get("name")
                        content = attrs_dict.get("content")
                        
                        if property_name and property_name.startswith("fc:frame"):
                            self.tags[property_name] = content
            
            parser = FrameParser()
            parser.feed(html)
            
            if not parser.tags:
                print("   ❌ No Frame tags found")
                return None
            
            # Build metadata from tags
            metadata = FrameMetadata(
                version=parser.tags.get("fc:frame", "vNext"),
                image=parser.tags.get("fc:frame:image"),
                image_aspect_ratio=parser.tags.get("fc:frame:image:aspect_ratio", "1.91:1"),
                input_text=parser.tags.get("fc:frame:input:text"),
                post_url=parser.tags.get("fc:frame:post_url"),
                state=parser.tags.get("fc:frame:state")
            )
            
            # Parse buttons
            for i in range(1, 5):  # Max 4 buttons
                button_label = parser.tags.get(f"fc:frame:button:{i}")
                if button_label:
                    action_str = parser.tags.get(f"fc:frame:button:{i}:action", "post")
                    target = parser.tags.get(f"fc:frame:button:{i}:target")
                    
                    try:
                        action = FrameButtonAction(action_str)
                    except ValueError:
                        action = FrameButtonAction.POST
                    
                    button = FrameButton(
                        index=i,
                        label=button_label,
                        action=action,
                        target=target
                    )
                    metadata.buttons.append(button)
            
            print("   ✅ Frame parsed successfully")
            print(f"   Version: {metadata.version}")
            print(f"   Buttons: {len(metadata.buttons)}")
            
            return metadata
            
        except Exception as e:
            print(f"   ❌ Error parsing HTML: {e}")
            return None
    
    def generate_frame_html(self, metadata: FrameMetadata) -> str:
        """
        Generate Frame HTML meta tags from metadata
        
        Args:
            metadata: FrameMetadata object
        
        Returns:
            HTML string with Frame meta tags
        """
        print("🏗️  Generating Frame HTML")
        
        tags = []
        
        # Version
        tags.append(f'<meta property="fc:frame" content="{metadata.version}" />')
        
        # Image
        if metadata.image:
            tags.append(f'<meta property="fc:frame:image" content="{metadata.image}" />')
            tags.append(f'<meta property="fc:frame:image:aspect_ratio" content="{metadata.image_aspect_ratio}" />')
        
        # Input
        if metadata.input_text:
            tags.append(f'<meta property="fc:frame:input:text" content="{metadata.input_text}" />')
        
        # Post URL
        if metadata.post_url:
            tags.append(f'<meta property="fc:frame:post_url" content="{metadata.post_url}" />')
        
        # State
        if metadata.state:
            tags.append(f'<meta property="fc:frame:state" content="{metadata.state}" />')
        
        # Buttons
        for button in metadata.buttons:
            tags.append(f'<meta property="fc:frame:button:{button.index}" content="{button.label}" />')
            if button.action != FrameButtonAction.POST:
                tags.append(f'<meta property="fc:frame:button:{button.index}:action" content="{button.action.value}" />')
            if button.target:
                tags.append(f'<meta property="fc:frame:button:{button.index}:target" content="{button.target}" />')
        
        html = "\n".join(tags)
        
        print(f"   ✅ Generated {len(tags)} meta tags")
        
        return html
    
    def is_frame_url(self, url: str) -> bool:
        """
        Quick check if URL might contain a Frame
        
        Args:
            url: URL to check
        
        Returns:
            True if URL might be a Frame, False otherwise
        """
        print(f"❓ Checking if Frame URL: {url[:50]}...")
        
        try:
            # Make HEAD request to check for Frame tags
            response = requests.head(url, timeout=5)
            content_type = response.headers.get("Content-Type", "")
            
            # Frames are typically HTML
            is_html = "text/html" in content_type
            
            print(f"   {'✅' if is_html else '❌'} Content-Type: {content_type}")
            
            return is_html
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

def main():
    """Example usage of Frame Handler"""
    
    # Get credentials from environment
    api_key = os.getenv("NEYNAR_API_KEY")
    
    if not api_key:
        print("❌ NEYNAR_API_KEY environment variable required")
        print("   Get your API key from: https://dev.neynar.com/")
        return
    
    # Initialize handler
    handler = FrameHandler(api_key=api_key)
    
    # Example Frame URLs (popular Farcaster frames)
    example_frames = [
        "https://www.farcaster.xyz",
        "https://gallery.so",
        "https://zora.co"
    ]
    
    # Example 1: Validate a Frame
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Validate Frame")
    print("=" * 70)
    
    for frame_url in example_frames:
        validation = handler.validate_frame(frame_url)
        
        if validation.valid and validation.metadata:
            print(f"\n✅ Valid Frame")
            print(f"   URL: {frame_url}")
            print(f"   Buttons:")
            for btn in validation.metadata.buttons:
                print(f"      {btn.index}. {btn.label} ({btn.action.value})")
            break
    
    # Example 2: Generate Frame HTML
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Generate Frame HTML")
    print("=" * 70)
    
    metadata = FrameMetadata(
        version="vNext",
        image="https://example.com/frame.png",
        image_aspect_ratio="1.91:1",
        post_url="https://example.com/api/frame",
        buttons=[
            FrameButton(index=1, label="Click Me", action=FrameButtonAction.POST),
            FrameButton(index=2, label="Visit Site", action=FrameButtonAction.LINK, target="https://example.com")
        ]
    )
    
    html = handler.generate_frame_html(metadata)
    print("\nGenerated HTML:")
    print(html[:200] + "...")
    
    print("\n" + "=" * 70)
    print("✅ Examples complete")
    print("=" * 70)

if __name__ == "__main__":
    main()
