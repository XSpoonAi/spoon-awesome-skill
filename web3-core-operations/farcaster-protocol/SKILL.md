---
name: Farcaster Social Protocol Handler
category: Web3 Core Operations
subcategory: SocialFi
description: Manage casts, reactions, and Frames on Farcaster decentralized social protocol
tags: [farcaster, socialfi, decentralized-social, neynar, frames, web3-social]
difficulty: intermediate
status: production
version: 1.0.0

activation_triggers:
  - cast
  - recast
  - farcaster
  - frame
  - like cast
  - publish to farcaster
  - social protocol

parameters:
  api_key:
    description: Neynar API key for Farcaster access
    required: true
    example: "your_neynar_api_key"
  signer_uuid:
    description: Managed signer UUID for write operations
    required: false
    example: "19d0c5fd-9b33-4a48-a0e2-bc7b0555baec"

requirements:
  python: ">=3.8"
  packages:
    - requests
  external:
    - Neynar API key (free tier available)
    - Neynar signer UUID (for posting)
---

# Farcaster Social Protocol Handler

## Overview

Complete integration with Farcaster, a decentralized social protocol built on Optimism. Manage casts (posts), reactions (likes/recasts), and interactive Frames (Mini Apps) via the Neynar API.

**Protocol Type**: Decentralized Social (SocialFi)  
**Network**: Optimism (L2)  
**API Provider**: Neynar (managed infrastructure)  
**Status**: Production Ready  

## Key Capabilities

### 1. **Cast Management** (cast_manager.py)
- ✅ Publish casts with text, embeds, and mentions
- ✅ Post to channels or reply to other casts
- ✅ Delete your own casts
- ✅ Search casts by keyword
- ✅ Lookup casts by hash or URL
- ✅ Fetch user's cast history
- ✅ Channel-based posting (topic communities)

### 2. **Reaction Management** (reaction_manager.py)
- ✅ Like casts (show appreciation)
- ✅ Recast (reshare) casts
- ✅ Unlike and unrecast
- ✅ Get reaction counts and details
- ✅ Fetch user's reaction history
- ✅ Bulk like operations
- ✅ Reaction aggregation

### 3. **Frame Handling** (frame_handler.py)
- ✅ Validate Frame URLs
- ✅ Parse Frame metadata from HTML
- ✅ Generate Frame HTML tags
- ✅ Support interactive buttons (post, link, mint, tx)
- ✅ Input field handling
- ✅ State management
- ✅ Transaction frame support

## Components

### cast_manager.py
**Purpose**: Manage Farcaster casts (posts)

**Classes**:
- `CastManager` - Main cast handler
- `Cast` - Cast data structure
- `CastEmbed` - Embed configuration

**Methods**:
```python
publish_cast(text, embeds, channel_id, parent)  # Post a cast
delete_cast(cast_hash)                           # Delete your cast
lookup_cast(identifier, by_url)                  # Fetch cast details
search_casts(query, limit, priority_mode)        # Search for casts
get_user_casts(fid, limit, include_replies)      # Get user's casts
```

### reaction_manager.py
**Purpose**: Handle likes and recasts

**Classes**:
- `ReactionManager` - Main reaction handler
- `Reaction` - Reaction data structure
- `ReactionSummary` - Aggregated reaction counts

**Methods**:
```python
like_cast(cast_hash, target_author_fid)          # Like a cast
unlike_cast(cast_hash, target_author_fid)        # Remove like
recast(cast_hash, target_author_fid)             # Recast (reshare)
unrecast(cast_hash, target_author_fid)           # Remove recast
get_reactions(cast_hash, reaction_type, limit)   # Get reaction summary
get_user_reactions(fid, reaction_type, limit)    # Get user reactions
bulk_like_casts(cast_hashes, delay_ms)           # Like multiple casts
```

### frame_handler.py
**Purpose**: Interactive Frame/Mini App management

**Classes**:
- `FrameHandler` - Main frame handler
- `FrameMetadata` - Frame configuration
- `FrameButton` - Button configuration
- `FrameValidation` - Validation result

**Methods**:
```python
validate_frame(url)                              # Validate Frame URL
fetch_frame_metadata(url)                        # Fetch Frame metadata
parse_frame_html(html)                           # Parse HTML for Frame tags
generate_frame_html(metadata)                    # Generate Frame HTML
is_frame_url(url)                                # Check if URL is Frame
```

## Usage Examples

### Example 1: Publish a Cast

```python
from cast_manager import CastManager

manager = CastManager(
    api_key="your_neynar_api_key",
    signer_uuid="your_signer_uuid"
)

cast = manager.publish_cast(
    text="Exploring decentralized social protocols! 🚀 #Farcaster",
    embeds=["https://farcaster.xyz"],
    channel_id="farcaster"
)

print(f"Published: {cast.hash}")
# View: https://warpcast.com/@username/0x71d5225f
```

**Expected Output**:
```
======================================================================
FARCASTER CAST MANAGER
======================================================================
✅ Write access enabled
   Signer UUID: 19d0c5fd...bc7b0555

📝 Publishing Cast
   Text: Exploring decentralized social protocols! 🚀 #Fa...
   Embeds: 1
   Channel: farcaster
   ✅ Published successfully
   Hash: 0x71d5225f77e0164388b1d4c120825f3a2c1f131c
   View: https://warpcast.com/username/0x71d5225f
```

### Example 2: Search and Like Trending Casts

```python
from cast_manager import CastManager
from reaction_manager import ReactionManager

# Initialize managers
cast_mgr = CastManager(api_key, signer_uuid)
react_mgr = ReactionManager(api_key, signer_uuid)

# Search for trending casts
casts = cast_mgr.search_casts("web3 protocol", limit=10, priority_mode=True)

# Like top casts
for cast in casts[:5]:
    if cast.likes_count > 10:
        react_mgr.like_cast(cast.hash)
        print(f"Liked: {cast.text[:60]}")
```

**Expected Output**:
```
🔎 Searching Casts
   Query: 'web3 protocol'
   Limit: 10
   ✅ Found 10 results

👍 Liking Cast
   Cast: 0x71d5225f77e01643...
   ✅ Like added
Liked: Just deployed a new web3 protocol for decentralized storage...

👍 Liking Cast
   Cast: 0x3702ec1b9a28f4e2...
   ✅ Like added
Liked: Excited to share our progress on the decentralized protocol...
```

### Example 3: Reply to a Cast

```python
from cast_manager import CastManager

manager = CastManager(api_key, signer_uuid)

# Lookup original cast
original = manager.lookup_cast("0x71d5225f77e0164388b1d4c120825f3a2c1f131c")

# Reply to it
reply = manager.publish_cast(
    text="Great insights! Looking forward to seeing more 👏",
    parent=original.hash,
    parent_author_fid=original.author_fid
)

print(f"Replied to @{original.author_fid}")
```

**Expected Output**:
```
🔍 Looking up Cast
   Identifier: 0x71d5225f77e0164388b1d4c120825f3a2c1f131c...
   ✅ Found
   Author: @username
   Text: Exploring decentralized social protocols! 🚀 #Farcaster...
   Reactions: 👍 15 | 🔄 3

📝 Publishing Cast
   Text: Great insights! Looking forward to seeing more 👏
   Reply to: 0x71d5225f77e01643...
   ✅ Published successfully
   Hash: 0x8f3d1a2b4c5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a
```

### Example 4: Get Reaction Analytics

```python
from reaction_manager import ReactionManager

manager = ReactionManager(api_key)

# Get reaction summary for a cast
summary = manager.get_reactions("0x71d5225f77e0164388b1d4c120825f3a2c1f131c")

print(f"Total Engagement: {summary.likes_count + summary.recasts_count}")
print(f"Likes: {summary.likes_count}")
print(f"Recasts: {summary.recasts_count}")

# Get top likers
for like in summary.likes[:5]:
    print(f"  Liked by FID {like['user']['fid']}")
```

**Expected Output**:
```
📊 Fetching Reactions
   Cast: 0x71d5225f77e01643...
   ✅ Retrieved reactions
      👍 Likes: 23
      🔄 Recasts: 5

Total Engagement: 28
Likes: 23
Recasts: 5
  Liked by FID 12345
  Liked by FID 67890
  Liked by FID 24680
```

### Example 5: Validate and Create a Frame

```python
from frame_handler import FrameHandler, FrameMetadata, FrameButton, FrameButtonAction

handler = FrameHandler(api_key)

# Validate existing Frame
validation = handler.validate_frame("https://gallery.so/frame")

if validation.valid:
    print(f"✅ Valid Frame with {len(validation.metadata.buttons)} buttons")

# Create new Frame metadata
frame = FrameMetadata(
    version="vNext",
    image="https://myapp.com/quiz-image.png",
    image_aspect_ratio="1:1",
    input_text="Enter your guess",
    post_url="https://myapp.com/api/submit",
    buttons=[
        FrameButton(1, "Option A", FrameButtonAction.POST),
        FrameButton(2, "Option B", FrameButtonAction.POST),
        FrameButton(3, "See Results", FrameButtonAction.LINK, 
                   target="https://myapp.com/results")
    ]
)

# Generate HTML for web page
html = handler.generate_frame_html(frame)
print("Frame HTML generated for embedding")
```

**Expected Output**:
```
🔍 Validating Frame
   URL: https://gallery.so/frame
   ✅ Frame is valid
   Version: vNext
   Buttons: 2

✅ Valid Frame with 2 buttons

🏗️  Generating Frame HTML
   ✅ Generated 10 meta tags
Frame HTML generated for embedding
```

### Example 6: Monitor Channel Activity

```python
from cast_manager import CastManager
import time

manager = CastManager(api_key)

while True:
    # Search recent casts in channel
    casts = manager.search_casts("channel:farcaster", limit=5)
    
    for cast in casts:
        print(f"@{cast.author_fid}: {cast.text[:80]}")
        print(f"  👍 {cast.likes_count} | 🔄 {cast.recasts_count}")
    
    print("\n---Refreshing in 60s---\n")
    time.sleep(60)
```

**Expected Output**:
```
🔎 Searching Casts
   Query: 'channel:farcaster'
   Limit: 5
   ✅ Found 5 results

@3: Just launched a new feature for decentralized identity management...
  👍 45 | 🔄 12
@15789: Excited to share our Farcaster integration roadmap for Q2...
  👍 33 | 🔄 8
@9876: Built a Frame that lets you mint NFTs directly in the feed!...
  👍 67 | 🔄 23

---Refreshing in 60s---
```

## Testing

### Prerequisites

1. **Get Neynar API Key**:
   - Visit https://dev.neynar.com/
   - Sign up and create an app
   - Copy your API key

2. **Get Signer UUID** (optional, for posting):
   - In Neynar dashboard, create a managed signer
   - Copy the signer UUID

3. **Set Environment Variables**:
   ```bash
   export NEYNAR_API_KEY="your_api_key"
   export NEYNAR_SIGNER_UUID="your_signer_uuid"  # Optional
   ```

### Run Tests

```bash
# Test cast manager
python cast_manager.py

# Test reaction manager
python reaction_manager.py

# Test frame handler
python frame_handler.py
```

### Manual Testing

```python
# Test read operations (no signer needed)
from cast_manager import CastManager

manager = CastManager(api_key="your_api_key")
casts = manager.search_casts("farcaster", limit=5)

for cast in casts:
    print(f"{cast.text[:60]}... (👍 {cast.likes_count})")
```

## Common Issues & Solutions

### Issue 1: "No signer UUID configured"
**Cause**: Attempting write operations without signer  
**Solution**: Set `NEYNAR_SIGNER_UUID` environment variable  
**Workaround**: Use read-only operations (search, lookup)

### Issue 2: HTTP 401 Unauthorized
**Cause**: Invalid or missing API key  
**Solution**: Verify `NEYNAR_API_KEY` is correct  
**Check**: Test key at https://docs.neynar.com/

### Issue 3: HTTP 429 Too Many Requests
**Cause**: Rate limit exceeded  
**Solution**: Use `delay_ms` parameter in bulk operations  
**Upgrade**: Consider paid Neynar plan for higher limits

### Issue 4: Cast not found
**Cause**: Cast hash is invalid or cast was deleted  
**Solution**: Verify hash format (0x...) and cast exists  
**Alternative**: Use URL lookup with `by_url=True`

### Issue 5: Frame validation fails
**Cause**: Missing required meta tags  
**Solution**: Ensure all required fc:frame tags present  
**Tool**: Use https://warpcast.com/~/developers/frames validator

## Production Deployment

### Security Checklist

- [ ] API keys stored in secure environment variables or secrets manager
- [ ] Signer UUID never committed to version control
- [ ] Rate limiting implemented to avoid API throttling
- [ ] TLS/HTTPS enabled for all API communications
- [ ] Error logging configured (but don't log sensitive data)
- [ ] Health checks for API connectivity
- [ ] Backup authentication mechanism

### Performance Optimization

```python
# Use bulk operations for efficiency
reaction_mgr = ReactionManager(api_key, signer_uuid)
cast_hashes = ["0x...", "0x...", "0x..."]

# Like multiple casts with rate limiting
reaction_mgr.bulk_like_casts(cast_hashes, delay_ms=200)
```

### Monitoring

```python
import logging

logging.basicConfig(level=logging.INFO)

try:
    cast = manager.publish_cast(text="Hello!")
    logging.info(f"Cast published: {cast.hash}")
except Exception as e:
    logging.error(f"Cast failed: {e}")
```

## Farcaster Concepts

### Protocol Architecture
- **Onchain** (Optimism): FID registration, storage rental, fname registry
- **Offchain** (Hubs): Message storage and validation (Hubble nodes)
- **Clients**: Applications built on protocol (Warpcast, custom apps)

### Key Terms
- **FID**: Farcaster ID (unique user identifier, e.g., `3`)
- **fname**: Username (e.g., `@username`)
- **Cast**: Post/message on Farcaster
- **Recast**: Reshare of a cast (like retweet)
- **Channel**: Topic-based community (e.g., `/farcaster`, `/crypto`)
- **Frame**: Interactive Mini App embedded in feed
- **Signer**: Ed25519 keypair for message signing
- **Hub**: Node storing and validating Farcaster messages

### Cost Model
- **FID Registration**: ~$10 USD (one-time, on Optimism)
- **Storage Rental**: Included with FID registration (renewable)
- **Posting**: Free (no gas fees for messages)
- **Neynar API**: Free tier available, paid plans for higher limits

## References

- **Farcaster Protocol Docs**: https://docs.farcaster.xyz/
- **Neynar API Reference**: https://docs.neynar.com/reference
- **Frame Specification**: https://docs.farcaster.xyz/reference/frames/spec
- **Warpcast Client**: https://warpcast.com/
- **Frame Validator Tool**: https://warpcast.com/~/developers/frames
- **Farcaster GitHub**: https://github.com/farcasterxyz
- **Neynar SDK**: https://github.com/neynarxyz/neynar-node-sdk

## Extensions

### Potential Enhancements
- WebSocket support for real-time updates
- Advanced search with filters (by channel, date, author)
- Cast thread management (fetch full conversations)
- User profile management
- Notification handling
- Direct cast (private messages)
- Wallet verification and display
- NFT collection display

### Integration Ideas
- Discord bot for Farcaster notifications
- Telegram bot for casting
- Twitter cross-poster
- Analytics dashboard
- Trending content aggregator
- Automated engagement bot
- Content moderation tools

---

**Status**: Production Ready  
**Version**: 1.0.0  
**Last Updated**: 2024  
**Maintainer**: Spoon Awesome Skills Team
