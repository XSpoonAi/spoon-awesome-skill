# Farcaster Social Protocol Handler

**Decentralized social interactions on Farcaster protocol**

Manage casts (posts), reactions (likes/recasts), and interactive Frames on the Farcaster decentralized social protocol via Neynar API.

## Overview

Farcaster is a decentralized social protocol built on Optimism. This skill provides production-ready tools to:

- **Publish Casts**: Post text, embeds, and replies to channels
- **Manage Reactions**: Like and recast content
- **Handle Frames**: Interactive Mini Apps embedded in feeds
- **Search & Discover**: Find casts, users, and trending content

### Key Features

✅ **Real Neynar API Integration** - Production-grade infrastructure  
✅ **Complete CRUD Operations** - Create, read, update, delete  
✅ **Reaction Management** - Like, recast, unlike, unrecast  
✅ **Frame Validation** - Validate and parse interactive content  
✅ **Channel Support** - Post to topic-based communities  
✅ **Idempotency** - Safe retry mechanisms built-in  
✅ **Error Handling** - Comprehensive error management  

## Installation

### Prerequisites

- Python 3.8 or higher
- Neynar API key (get from [dev.neynar.com](https://dev.neynar.com/))

### Setup

1. **Install dependencies**:
   ```bash
   pip install requests
   ```

2. **Set environment variables**:
   ```bash
   export NEYNAR_API_KEY="your_api_key_here"
   export NEYNAR_SIGNER_UUID="your_signer_uuid"  # For write operations
   ```

3. **Get Neynar credentials**:
   - Sign up at https://dev.neynar.com/
   - Create an app to get API key
   - Generate a managed signer for posting (optional)

## Quick Start

### Cast Manager - Publishing Content

```python
from cast_manager import CastManager

# Initialize
manager = CastManager(
    api_key="your_neynar_api_key",
    signer_uuid="your_signer_uuid"
)

# Publish a cast
cast = manager.publish_cast(
    text="Hello Farcaster! 🚀",
    embeds=["https://farcaster.xyz"],
    channel_id="farcaster"
)

# Search casts
casts = manager.search_casts("web3 protocol", limit=10)

# Get user casts
user_casts = manager.get_user_casts(fid=3, limit=25)
```

### Reaction Manager - Social Engagement

```python
from reaction_manager import ReactionManager

# Initialize
manager = ReactionManager(
    api_key="your_neynar_api_key",
    signer_uuid="your_signer_uuid"
)

# Like a cast
manager.like_cast("0x71d5225f77e0164388b1d4c120825f3a2c1f131c")

# Recast (reshare)
manager.recast("0x71d5225f77e0164388b1d4c120825f3a2c1f131c")

# Get reaction summary
summary = manager.get_reactions("0x71d5225f...")
print(f"Likes: {summary.likes_count}")
print(f"Recasts: {summary.recasts_count}")
```

### Frame Handler - Interactive Content

```python
from frame_handler import FrameHandler

# Initialize
handler = FrameHandler(api_key="your_neynar_api_key")

# Validate a Frame URL
validation = handler.validate_frame("https://example.com/frame")

if validation.valid:
    print(f"Buttons: {len(validation.metadata.buttons)}")
    for btn in validation.metadata.buttons:
        print(f"  {btn.label} ({btn.action.value})")

# Generate Frame HTML
from frame_handler import FrameMetadata, FrameButton, FrameButtonAction

metadata = FrameMetadata(
    version="vNext",
    image="https://example.com/image.png",
    post_url="https://example.com/api/frame",
    buttons=[
        FrameButton(1, "Click Me", FrameButtonAction.POST),
        FrameButton(2, "Visit", FrameButtonAction.LINK, target="https://example.com")
    ]
)

html = handler.generate_frame_html(metadata)
```

## Usage Examples

### Example 1: Social Bot

```python
# Bot that likes and recasts popular casts

from cast_manager import CastManager
from reaction_manager import ReactionManager

cast_mgr = CastManager(api_key, signer_uuid)
react_mgr = ReactionManager(api_key, signer_uuid)

# Search for trending casts
casts = cast_mgr.search_casts("farcaster", limit=10, priority_mode=True)

# Engage with top casts
for cast in casts[:5]:
    if cast.likes_count > 10:
        react_mgr.like_cast(cast.hash)
        print(f"Liked: {cast.text[:50]}")
```

### Example 2: Channel Monitor

```python
# Monitor a channel for new casts

from cast_manager import CastManager
import time

manager = CastManager(api_key)

while True:
    # Get recent casts from channel
    casts = manager.search_casts("query", limit=5)
    
    for cast in casts:
        print(f"@{cast.author_fid}: {cast.text}")
    
    time.sleep(60)  # Check every minute
```

### Example 3: Frame Creator

```python
# Create and validate an interactive Frame

from frame_handler import FrameHandler, FrameMetadata, FrameButton, FrameButtonAction

handler = FrameHandler(api_key)

# Define Frame metadata
frame = FrameMetadata(
    version="vNext",
    image="https://yoursite.com/quiz.png",
    image_aspect_ratio="1:1",
    input_text="Enter your answer",
    post_url="https://yoursite.com/api/quiz",
    buttons=[
        FrameButton(1, "Option A", FrameButtonAction.POST),
        FrameButton(2, "Option B", FrameButtonAction.POST),
        FrameButton(3, "Results", FrameButtonAction.LINK, target="https://yoursite.com/results")
    ]
)

# Generate HTML for your web page
html = handler.generate_frame_html(frame)
print(html)
```

## API Reference

### CastManager

| Method | Description |
|--------|-------------|
| `publish_cast(text, embeds, channel_id, parent)` | Publish a cast |
| `delete_cast(cast_hash)` | Delete your cast |
| `lookup_cast(identifier, by_url)` | Fetch cast details |
| `search_casts(query, limit, priority_mode)` | Search casts |
| `get_user_casts(fid, limit, include_replies)` | Get user's casts |

### ReactionManager

| Method | Description |
|--------|-------------|
| `like_cast(cast_hash, target_author_fid)` | Like a cast |
| `unlike_cast(cast_hash, target_author_fid)` | Remove like |
| `recast(cast_hash, target_author_fid)` | Recast (reshare) |
| `unrecast(cast_hash, target_author_fid)` | Remove recast |
| `get_reactions(cast_hash, reaction_type, limit)` | Get reaction summary |
| `get_user_reactions(fid, reaction_type, limit)` | Get user's reactions |
| `bulk_like_casts(cast_hashes, delay_ms)` | Like multiple casts |

### FrameHandler

| Method | Description |
|--------|-------------|
| `validate_frame(url)` | Validate Frame URL |
| `fetch_frame_metadata(url)` | Fetch Frame metadata |
| `parse_frame_html(html)` | Parse HTML for Frame tags |
| `generate_frame_html(metadata)` | Generate Frame HTML |
| `is_frame_url(url)` | Check if URL is a Frame |

## Configuration

### Environment Variables

```bash
# Required for all operations
NEYNAR_API_KEY=your_api_key_here

# Required for write operations (casting, reactions)
NEYNAR_SIGNER_UUID=your_signer_uuid_here
```

### Rate Limiting

Neynar API has rate limits:
- Free tier: 1,000 requests/day
- Paid tiers: Higher limits available

Use `delay_ms` parameter in bulk operations to respect rate limits.

## Farcaster Concepts

### FID (Farcaster ID)
Unique integer identifier for each user on Farcaster. Example: `3`

### Cast
A post on Farcaster (equivalent to a tweet). Can include:
- Text (max 320 characters)
- Embeds (images, URLs, other casts)
- Mentions (@username)
- Channel tags

### Channel
Topic-based communities on Farcaster. Examples:
- `/farcaster` - Main protocol discussion
- `/warpcast` - Warpcast app discussion
- `/crypto` - Cryptocurrency topics

### Frame
Interactive embedded content in casts. Supports:
- Buttons (post, link, mint, transaction)
- Input fields
- State management
- Transaction requests

### Signer
Managed authentication for write operations. Neynar provides managed signers (signer_uuid) that abstract key management.

## Troubleshooting

### Error: "No signer UUID configured"
**Solution**: Set `NEYNAR_SIGNER_UUID` environment variable for write operations.

### Error: HTTP 401 Unauthorized
**Solution**: Check your `NEYNAR_API_KEY` is correct and active.

### Error: HTTP 429 Too Many Requests
**Solution**: You've exceeded rate limits. Wait and retry, or upgrade plan.

### Error: HTTP 409 Conflict
**Solution**: You've already liked/recasted this cast. Use unlike/unrecast first.

### Cast not appearing immediately
**Solution**: Casts may take a few seconds to propagate across Farcaster network.

## Production Checklist

- [ ] API key stored securely (environment variables, secrets manager)
- [ ] Signer UUID protected (never commit to version control)
- [ ] Rate limiting implemented for bulk operations
- [ ] Error handling and retries configured
- [ ] Logging enabled for debugging
- [ ] Health checks for API connectivity
- [ ] Backup authentication method (if main API fails)

## Resources

- **Farcaster Protocol**: https://docs.farcaster.xyz/
- **Neynar API**: https://docs.neynar.com/
- **Warpcast** (popular client): https://warpcast.com/
- **Frame Validator**: https://warpcast.com/~/developers/frames

## Support

For issues or questions:
- Farcaster Discord: https://discord.gg/farcaster
- Neynar Support: https://docs.neynar.com/
- GitHub Issues: [Your repository]

## License

MIT License - See LICENSE file for details

---

**Built for Spoon Awesome Skills** - Decentralized Social Integration
