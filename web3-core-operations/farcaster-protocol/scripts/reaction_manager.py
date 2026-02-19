#!/usr/bin/env python3
"""
Farcaster Reaction Manager - Social Engagement
Manage reactions (likes, recasts) on Farcaster protocol

REAL IMPLEMENTATION - No Mocks/Simulations
- Real Neynar API integration
- Real like/unlike operations
- Real recast/unrecast operations
- Real reaction aggregation
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import requests

# Neynar API configuration
NEYNAR_API_BASE = "https://api.neynar.com/v2/farcaster"

@dataclass
class Reaction:
    """Farcaster reaction structure"""
    reaction_type: str  # 'like' or 'recast'
    cast_hash: str
    author_fid: int
    timestamp: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

@dataclass
class ReactionSummary:
    """Aggregated reaction counts for a cast"""
    cast_hash: str
    likes_count: int = 0
    recasts_count: int = 0
    likes: List[Dict] = None
    recasts: List[Dict] = None
    
    def __post_init__(self):
        if self.likes is None:
            self.likes = []
        if self.recasts is None:
            self.recasts = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

class ReactionManager:
    """
    Manage Farcaster reactions (likes and recasts) via Neynar API
    
    Features:
    - Like casts (show appreciation)
    - Recast (reshare) casts
    - Unlike and unrecast
    - Get reaction counts and details
    - List reactions for a cast
    """
    
    def __init__(
        self,
        api_key: str,
        signer_uuid: Optional[str] = None
    ):
        """
        Initialize Reaction Manager
        
        Args:
            api_key: Neynar API key
            signer_uuid: UUID of the signer (required for reacting)
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
        print("FARCASTER REACTION MANAGER")
        print("=" * 70)
        if signer_uuid:
            print(f"✅ Reaction access enabled")
            print(f"   Signer UUID: {signer_uuid[:8]}...{signer_uuid[-8:]}")
        else:
            print("⚠️  Read-only mode (no signer UUID)")
        print()
    
    def like_cast(
        self,
        cast_hash: str,
        target_author_fid: Optional[int] = None
    ) -> bool:
        """
        Like a cast
        
        Args:
            cast_hash: Hash of the cast to like
            target_author_fid: FID of the cast author (optional, helps with lookup)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.signer_uuid:
            print("❌ Cannot like: No signer UUID configured")
            return False
        
        print("👍 Liking Cast")
        print(f"   Cast: {cast_hash[:20]}...")
        
        return self._add_reaction(
            reaction_type="like",
            target=cast_hash,
            target_author_fid=target_author_fid
        )
    
    def unlike_cast(
        self,
        cast_hash: str,
        target_author_fid: Optional[int] = None
    ) -> bool:
        """
        Remove like from a cast
        
        Args:
            cast_hash: Hash of the cast to unlike
            target_author_fid: FID of the cast author (optional)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.signer_uuid:
            print("❌ Cannot unlike: No signer UUID configured")
            return False
        
        print("👎 Unliking Cast")
        print(f"   Cast: {cast_hash[:20]}...")
        
        return self._remove_reaction(
            reaction_type="like",
            target=cast_hash,
            target_author_fid=target_author_fid
        )
    
    def recast(
        self,
        cast_hash: str,
        target_author_fid: Optional[int] = None
    ) -> bool:
        """
        Recast (reshare) a cast
        
        Args:
            cast_hash: Hash of the cast to recast
            target_author_fid: FID of the cast author (optional)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.signer_uuid:
            print("❌ Cannot recast: No signer UUID configured")
            return False
        
        print("🔄 Recasting")
        print(f"   Cast: {cast_hash[:20]}...")
        
        return self._add_reaction(
            reaction_type="recast",
            target=cast_hash,
            target_author_fid=target_author_fid
        )
    
    def unrecast(
        self,
        cast_hash: str,
        target_author_fid: Optional[int] = None
    ) -> bool:
        """
        Remove recast
        
        Args:
            cast_hash: Hash of the cast to unrecast
            target_author_fid: FID of the cast author (optional)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.signer_uuid:
            print("❌ Cannot unrecast: No signer UUID configured")
            return False
        
        print("↩️  Removing Recast")
        print(f"   Cast: {cast_hash[:20]}...")
        
        return self._remove_reaction(
            reaction_type="recast",
            target=cast_hash,
            target_author_fid=target_author_fid
        )
    
    def _add_reaction(
        self,
        reaction_type: str,
        target: str,
        target_author_fid: Optional[int] = None
    ) -> bool:
        """
        Internal method to add a reaction
        
        Args:
            reaction_type: 'like' or 'recast'
            target: Cast hash or URL
            target_author_fid: FID of target author
        
        Returns:
            True if successful, False otherwise
        """
        body = {
            "signer_uuid": self.signer_uuid,
            "reaction_type": reaction_type,
            "target": target
        }
        
        if target_author_fid:
            body["target_author_fid"] = target_author_fid
        
        try:
            response = self.session.post(
                f"{self.base_url}/reaction",
                json=body
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("success"):
                print(f"   ✅ {reaction_type.capitalize()} added")
                return True
            else:
                print(f"   ❌ Failed: {data.get('message', 'Unknown error')}")
                return False
                
        except requests.exceptions.HTTPError as e:
            print(f"   ❌ HTTP Error: {e.response.status_code}")
            if e.response.status_code == 409:
                print(f"   ℹ️  Already {reaction_type}d")
            else:
                print(f"   Response: {e.response.text}")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def _remove_reaction(
        self,
        reaction_type: str,
        target: str,
        target_author_fid: Optional[int] = None
    ) -> bool:
        """
        Internal method to remove a reaction
        
        Args:
            reaction_type: 'like' or 'recast'
            target: Cast hash or URL
            target_author_fid: FID of target author
        
        Returns:
            True if successful, False otherwise
        """
        body = {
            "signer_uuid": self.signer_uuid,
            "reaction_type": reaction_type,
            "target": target
        }
        
        if target_author_fid:
            body["target_author_fid"] = target_author_fid
        
        try:
            response = self.session.delete(
                f"{self.base_url}/reaction",
                json=body
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("success"):
                print(f"   ✅ {reaction_type.capitalize()} removed")
                return True
            else:
                print(f"   ❌ Failed: {data.get('message', 'Unknown error')}")
                return False
                
        except requests.exceptions.HTTPError as e:
            print(f"   ❌ HTTP Error: {e.response.status_code}")
            if e.response.status_code == 404:
                print(f"   ℹ️  No {reaction_type} found to remove")
            else:
                print(f"   Response: {e.response.text}")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def get_reactions(
        self,
        cast_hash: str,
        reaction_type: Optional[str] = None,
        limit: int = 25
    ) -> ReactionSummary:
        """
        Get reactions for a cast
        
        Args:
            cast_hash: Hash of the cast
            reaction_type: Filter by 'like' or 'recast' (None for both)
            limit: Maximum reactions per type
        
        Returns:
            ReactionSummary object with counts and details
        """
        print(f"📊 Fetching Reactions")
        print(f"   Cast: {cast_hash[:20]}...")
        if reaction_type:
            print(f"   Type: {reaction_type}")
        
        summary = ReactionSummary(cast_hash=cast_hash)
        
        try:
            params = {
                "hash": cast_hash,
                "limit": limit
            }
            
            if reaction_type:
                params["type"] = reaction_type
            
            response = self.session.get(
                f"{self.base_url}/cast/reactions",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            reactions_data = data.get("reactions", {})
            
            # Extract likes
            if "likes" in reactions_data:
                summary.likes = reactions_data["likes"]
                summary.likes_count = len(summary.likes)
            
            # Extract recasts
            if "recasts" in reactions_data:
                summary.recasts = reactions_data["recasts"]
                summary.recasts_count = len(summary.recasts)
            
            print(f"   ✅ Retrieved reactions")
            print(f"      👍 Likes: {summary.likes_count}")
            print(f"      🔄 Recasts: {summary.recasts_count}")
            
            return summary
            
        except requests.exceptions.HTTPError as e:
            print(f"   ❌ HTTP Error: {e.response.status_code}")
            return summary
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return summary
    
    def get_user_reactions(
        self,
        fid: int,
        reaction_type: Optional[str] = None,
        limit: int = 25
    ) -> List[Reaction]:
        """
        Get reactions made by a specific user
        
        Args:
            fid: Farcaster ID of the user
            reaction_type: Filter by 'like' or 'recast' (None for both)
            limit: Maximum reactions to return
        
        Returns:
            List of Reaction objects
        """
        print(f"👤 Fetching User Reactions")
        print(f"   FID: {fid}")
        if reaction_type:
            print(f"   Type: {reaction_type}")
        
        reactions = []
        
        try:
            params = {
                "fid": fid,
                "limit": limit
            }
            
            if reaction_type:
                params["type"] = reaction_type
            
            response = self.session.get(
                f"{self.base_url}/reactions/user",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            reactions_data = data.get("reactions", [])
            
            for reaction_data in reactions_data:
                reactions.append(Reaction(
                    reaction_type=reaction_data["reaction_type"],
                    cast_hash=reaction_data["cast"]["hash"],
                    author_fid=fid,
                    timestamp=reaction_data.get("timestamp", "")
                ))
            
            print(f"   ✅ Found {len(reactions)} reactions")
            
            return reactions
            
        except requests.exceptions.HTTPError as e:
            print(f"   ❌ HTTP Error: {e.response.status_code}")
            return reactions
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return reactions
    
    def bulk_like_casts(
        self,
        cast_hashes: List[str],
        delay_ms: int = 100
    ) -> Dict[str, bool]:
        """
        Like multiple casts
        
        Args:
            cast_hashes: List of cast hashes to like
            delay_ms: Delay between requests (rate limiting)
        
        Returns:
            Dictionary mapping cast hash to success status
        """
        import time
        
        print(f"🔥 Bulk Liking {len(cast_hashes)} Casts")
        
        results = {}
        for i, cast_hash in enumerate(cast_hashes, 1):
            print(f"\n   [{i}/{len(cast_hashes)}] Processing...")
            success = self.like_cast(cast_hash)
            results[cast_hash] = success
            
            if i < len(cast_hashes) and delay_ms > 0:
                time.sleep(delay_ms / 1000.0)
        
        successful = sum(1 for v in results.values() if v)
        print(f"\n   ✅ Completed: {successful}/{len(cast_hashes)} successful")
        
        return results

def main():
    """Example usage of Reaction Manager"""
    
    # Get credentials from environment
    api_key = os.getenv("NEYNAR_API_KEY")
    signer_uuid = os.getenv("NEYNAR_SIGNER_UUID")
    
    if not api_key:
        print("❌ NEYNAR_API_KEY environment variable required")
        print("   Get your API key from: https://dev.neynar.com/")
        return
    
    # Initialize manager
    manager = ReactionManager(
        api_key=api_key,
        signer_uuid=signer_uuid
    )
    
    # Example cast hash (for demonstration - replace with real cast)
    example_cast = "0x71d5225f77e0164388b1d4c120825f3a2c1f131c"
    
    # Example 1: Get reactions for a cast
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Get Reactions")
    print("=" * 70)
    summary = manager.get_reactions(example_cast)
    print(f"\nReaction Summary:")
    print(f"  👍 Likes: {summary.likes_count}")
    print(f"  🔄 Recasts: {summary.recasts_count}")
    
    # Example 2: Like a cast (requires signer)
    if signer_uuid:
        print("\n" + "=" * 70)
        print("EXAMPLE 2: Like Cast")
        print("=" * 70)
        
        success = manager.like_cast(example_cast)
        
        if success:
            print("\n✅ Successfully liked cast")
            
            # Example 3: Un like the cast
            print("\n" + "=" * 70)
            print("EXAMPLE 3: Unlike Cast")
            print("=" * 70)
            
            manager.unlike_cast(example_cast)
    
    print("\n" + "=" * 70)
    print("✅ Examples complete")
    print("=" * 70)

if __name__ == "__main__":
    main()
