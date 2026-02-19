#!/usr/bin/env python3
"""
Farcaster Cast Manager - Social Protocol Integration
Manage casts (posts) on the Farcaster decentralized social protocol

REAL IMPLEMENTATION - No Mocks/Simulations
- Real Neynar API integration
- Real cast publishing via HTTP API
- Real cast deletion and lookup
- Real channel and reply management
"""

import os
import json
import time
import uuid
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
import requests

# Neynar API configuration
NEYNAR_API_BASE = "https://api.neynar.com/v2/farcaster"

@dataclass
class CastEmbed:
    """Embed in a cast (URL, cast reference, or image)"""
    url: Optional[str] = None
    cast_id: Optional[Dict[str, Union[str, int]]] = None  # {"hash": str, "fid": int}
    
    def to_dict(self) -> Dict:
        """Convert to API format"""
        if self.url:
            return {"url": self.url}
        elif self.cast_id:
            return {"cast_id": self.cast_id}
        return {}

@dataclass
class Cast:
    """Farcaster cast (post) structure"""
    hash: str
    author_fid: int
    text: str
    timestamp: str
    embeds: List[Dict] = None
    mentions: List[int] = None
    channel_id: Optional[str] = None
    parent_hash: Optional[str] = None
    parent_author_fid: Optional[int] = None
    reactions: Optional[Dict] = None
    replies_count: int = 0
    recasts_count: int = 0
    likes_count: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

class CastManager:
    """
    Manage Farcaster casts (posts) via Neynar API
    
    Features:
    - Publish casts with text, embeds, and mentions
    - Post to channels or reply to other casts
    - Delete your own casts
    - Lookup casts by hash or URL
    - Search casts by keyword
    """
    
    def __init__(
        self,
        api_key: str,
        signer_uuid: Optional[str] = None
    ):
        """
        Initialize Cast Manager
        
        Args:
            api_key: Neynar API key
            signer_uuid: UUID of the signer (required for posting)
        """
        self.api_key = api_key
        self.signer_uuid = signer_uuid
        self.base_url = NEYNAR_API_BASE
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        })
        
        print("=" * 70)
        print("FARCASTER CAST MANAGER")
        print("=" * 70)
        if signer_uuid:
            print(f"✅ Write access enabled")
            print(f"   Signer UUID: {signer_uuid[:8]}...{signer_uuid[-8:]}")
        else:
            print("⚠️  Read-only mode (no signer UUID)")
        print()
    
    def publish_cast(
        self,
        text: str,
        embeds: Optional[List[Union[str, Dict]]] = None,
        channel_id: Optional[str] = None,
        parent: Optional[str] = None,
        parent_author_fid: Optional[int] = None
    ) -> Optional[Cast]:
        """
        Publish a cast (post) on Farcaster
        
        Args:
            text: Content of the cast (max 320 chars)
            embeds: List of URLs or cast references to embed
            channel_id: Channel to post in (e.g., "warpcast", "farcaster")
            parent: Parent cast hash (for replies) or channel URL
            parent_author_fid: FID of parent cast author
        
        Returns:
            Cast object if successful, None otherwise
        """
        if not self.signer_uuid:
            print("❌ Cannot publish: No signer UUID configured")
            return None
        
        print("📝 Publishing Cast")
        print(f"   Text: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        # Build request body
        body = {
            "signer_uuid": self.signer_uuid,
            "text": text,
            "idem": str(uuid.uuid4())[:16]  # Idempotency key
        }
        
        # Add embeds
        if embeds:
            formatted_embeds = []
            for embed in embeds:
                if isinstance(embed, str):
                    formatted_embeds.append({"url": embed})
                elif isinstance(embed, dict):
                    formatted_embeds.append(embed)
            body["embeds"] = formatted_embeds
            print(f"   Embeds: {len(formatted_embeds)}")
        
        # Add channel or parent
        if channel_id:
            body["channel_id"] = channel_id
            print(f"   Channel: {channel_id}")
        
        if parent:
            body["parent"] = parent
            print(f"   Reply to: {parent[:20]}...")
        
        if parent_author_fid:
            body["parent_author_fid"] = parent_author_fid
        
        try:
            response = self.session.post(
                f"{self.base_url}/cast",
                json=body
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("success"):
                cast_data = data["cast"]
                print(f"   ✅ Published successfully")
                print(f"   Hash: {cast_data['hash']}")
                print(f"   View: https://warpcast.com/{cast_data['author']['username']}/{cast_data['hash'][:10]}")
                
                return Cast(
                    hash=cast_data["hash"],
                    author_fid=cast_data["author"]["fid"],
                    text=cast_data["text"],
                    timestamp=cast_data.get("timestamp", ""),
                    embeds=cast_data.get("embeds", []),
                    mentions=cast_data.get("mentions", []),
                    channel_id=channel_id,
                    parent_hash=parent
                )
            else:
                print(f"   ❌ Failed: {data.get('message', 'Unknown error')}")
                return None
                
        except requests.exceptions.HTTPError as e:
            print(f"   ❌ HTTP Error: {e.response.status_code}")
            print(f"   Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def delete_cast(self, cast_hash: str) -> bool:
        """
        Delete a cast you authored
        
        Args:
            cast_hash: Hash of the cast to delete
        
        Returns:
            True if successful, False otherwise
        """
        if not self.signer_uuid:
            print("❌ Cannot delete: No signer UUID configured")
            return False
        
        print(f"🗑️  Deleting Cast")
        print(f"   Hash: {cast_hash}")
        
        try:
            response = self.session.delete(
                f"{self.base_url}/cast",
                json={
                    "signer_uuid": self.signer_uuid,
                    "target_hash": cast_hash
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("success"):
                print("   ✅ Deleted successfully")
                return True
            else:
                print(f"   ❌ Failed: {data.get('message', 'Unknown error')}")
                return False
                
        except requests.exceptions.HTTPError as e:
            print(f"   ❌ HTTP Error: {e.response.status_code}")
            print(f"   Response: {e.response.text}")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def lookup_cast(
        self,
        identifier: str,
        by_url: bool = False
    ) -> Optional[Cast]:
        """
        Lookup a cast by hash or URL
        
        Args:
            identifier: Cast hash (0x...) or Warpcast URL
            by_url: If True, identifier is a URL
        
        Returns:
            Cast object if found, None otherwise
        """
        print(f"🔍 Looking up Cast")
        print(f"   Identifier: {identifier[:50]}...")
        
        try:
            params = {}
            if by_url:
                params["type"] = "url"
                params["identifier"] = identifier
            else:
                params["type"] = "hash"
                params["identifier"] = identifier
            
            response = self.session.get(
                f"{self.base_url}/cast",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            cast_data = data.get("cast")
            
            if cast_data:
                print("   ✅ Found")
                print(f"   Author: @{cast_data['author'].get('username', 'unknown')}")
                print(f"   Text: {cast_data['text'][:60]}...")
                print(f"   Reactions: 👍 {cast_data.get('reactions', {}).get('likes_count', 0)} | "
                      f"🔄 {cast_data.get('reactions', {}).get('recasts_count', 0)}")
                
                return Cast(
                    hash=cast_data["hash"],
                    author_fid=cast_data["author"]["fid"],
                    text=cast_data["text"],
                    timestamp=cast_data.get("timestamp", ""),
                    embeds=cast_data.get("embeds", []),
                    mentions=cast_data.get("mentions", []),
                    reactions=cast_data.get("reactions"),
                    replies_count=cast_data.get("replies", {}).get("count", 0),
                    recasts_count=cast_data.get("reactions", {}).get("recasts_count", 0),
                    likes_count=cast_data.get("reactions", {}).get("likes_count", 0)
                )
            else:
                print("   ❌ Not found")
                return None
                
        except requests.exceptions.HTTPError as e:
            print(f"   ❌ HTTP Error: {e.response.status_code}")
            return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def search_casts(
        self,
        query: str,
        limit: int = 25,
        priority_mode: bool = True
    ) -> List[Cast]:
        """
        Search for casts by keyword
        
        Args:
            query: Search query
            limit: Maximum results (default 25, max 100)
            priority_mode: Prioritize quality over recency
        
        Returns:
            List of Cast objects
        """
        print(f"🔎 Searching Casts")
        print(f"   Query: '{query}'")
        print(f"   Limit: {limit}")
        
        try:
            response = self.session.get(
                f"{self.base_url}/cast/search",
                params={
                    "q": query,
                    "limit": limit,
                    "priority_mode": str(priority_mode).lower()
                }
            )
            response.raise_for_status()
            
            data = response.json()
            casts_data = data.get("casts", [])
            
            print(f"   ✅ Found {len(casts_data)} results")
            
            casts = []
            for cast_data in casts_data:
                casts.append(Cast(
                    hash=cast_data["hash"],
                    author_fid=cast_data["author"]["fid"],
                    text=cast_data["text"],
                    timestamp=cast_data.get("timestamp", ""),
                    likes_count=cast_data.get("reactions", {}).get("likes_count", 0),
                    recasts_count=cast_data.get("reactions", {}).get("recasts_count", 0)
                ))
            
            return casts
            
        except requests.exceptions.HTTPError as e:
            print(f"   ❌ HTTP Error: {e.response.status_code}")
            return []
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []
    
    def get_user_casts(
        self,
        fid: int,
        limit: int = 25,
        include_replies: bool = False
    ) -> List[Cast]:
        """
        Get casts from a specific user
        
        Args:
            fid: Farcaster ID of the user
            limit: Maximum results
            include_replies: Include reply casts
        
        Returns:
            List of Cast objects
        """
        print(f"📋 Fetching User Casts")
        print(f"   FID: {fid}")
        print(f"   Limit: {limit}")
        
        try:
            response = self.session.get(
                f"{self.base_url}/feed/user/casts",
                params={
                    "fid": fid,
                    "limit": limit,
                    "include_replies": str(include_replies).lower()
                }
            )
            response.raise_for_status()
            
            data = response.json()
            casts_data = data.get("casts", [])
            
            print(f"   ✅ Found {len(casts_data)} casts")
            
            casts = []
            for cast_data in casts_data:
                casts.append(Cast(
                    hash=cast_data["hash"],
                    author_fid=cast_data["author"]["fid"],
                    text=cast_data["text"],
                    timestamp=cast_data.get("timestamp", ""),
                    channel_id=cast_data.get("channel", {}).get("id")
                ))
            
            return casts
            
        except requests.exceptions.HTTPError as e:
            print(f"   ❌ HTTP Error: {e.response.status_code}")
            return []
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []

def main():
    """Example usage of Cast Manager"""
    
    # Get credentials from environment
    api_key = os.getenv("NEYNAR_API_KEY")
    signer_uuid = os.getenv("NEYNAR_SIGNER_UUID")
    
    if not api_key:
        print("❌ NEYNAR_API_KEY environment variable required")
        print("   Get your API key from: https://dev.neynar.com/")
        return
    
    # Initialize manager
    manager = CastManager(
        api_key=api_key,
        signer_uuid=signer_uuid
    )
    
    # Example 1: Search for casts
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Search Casts")
    print("=" * 70)
    casts = manager.search_casts("farcaster protocol", limit=5)
    for i, cast in enumerate(casts[:3], 1):
        print(f"\n{i}. {cast.text[:100]}...")
        print(f"   👍 {cast.likes_count} | 🔄 {cast.recasts_count}")
    
    # Example 2: Publish a cast (requires signer)
    if signer_uuid:
        print("\n" + "=" * 70)
        print("EXAMPLE 2: Publish Cast")
        print("=" * 70)
        
        cast = manager.publish_cast(
            text="Hello Farcaster! Testing the protocol 🚀",
            embeds=["https://farcaster.xyz"],
            channel_id="farcaster"
        )
        
        if cast:
            # Wait a moment then lookup the cast
            time.sleep(2)
            
            print("\n" + "=" * 70)
            print("EXAMPLE 3: Lookup Cast")
            print("=" * 70)
            found_cast = manager.lookup_cast(cast.hash)
            
            if found_cast:
                print(f"\n✅ Successfully published and retrieved cast")
                print(f"   View at: https://warpcast.com/@username/{cast.hash[:10]}")
    
    print("\n" + "=" * 70)
    print("✅ Examples complete")
    print("=" * 70)

if __name__ == "__main__":
    main()
