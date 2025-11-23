Platform Presence Schema

Table: platforms.csv

Description

Platform-specific presence and linking information for each creator.


Fields

Field Name	Data Type	Required	Description	Validation
creator_id	string	Yes	Creator unique identifier	Foreign key to creators.creator_id
platform	string	Yes	Platform name	Values: X, Instagram, TikTok, Reddit, OnlyFans, Fansly, ManyVids, YouTube, Twitch, Other
handle	string	Yes	Platform handle/username	No @ symbol, alphanumeric + underscores
url	string	Yes	Full profile URL	Valid URL format
linked_hub	string	No	Link hub platform	Values: Linktree, Beacons, Carrd, Custom, None, Unknown
linked_hub_url	string	No	Link hub URL	Valid URL format
is_verified	boolean	No	Platform verification status	Values: true, false, null
followers_count	integer	No	Current followers count	Non-negative integer
following_count	integer	No	Current following count	Non-negative integer
posts_count	integer	No	Total posts count	Non-negative integer
account_created	date	No	Account creation date	Format: YYYY-MM-DD
last_activity	date	No	Last post/activity date	Format: YYYY-MM-DD
is_primary	boolean	No	Whether this is primary platform	Values: true, false
platform_tier	string	No	Platform-specific tier	Values: Basic, Premium, Pro, Enterprise, Unknown
notes	text	No	Additional platform notes	Max: 300 characters

Platform Values
• **X**: Twitter/X platform
• **Instagram**: Instagram platform  
• **TikTok**: TikTok platform
• **Reddit**: Reddit platform
• **OnlyFans**: OnlyFans platform
• **Fansly**: Fansly platform
• **ManyVids**: ManyVids platform
• **YouTube**: YouTube platform
• **Twitch**: Twitch platform
• **Other**: Other platforms not listed


CSV Template

creator_id,platform,handle,url,linked_hub,linked_hub_url,is_verified,followers_count,following_count,posts_count,account_created,last_activity,is_primary,platform_tier,notes
ne-8f2c1a4b9c3d7e8f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f,X,ne_omaha_creator,https://twitter.com/ne_omaha_creator,Linktree,https://linktr.ee/neomaha,true,15234,892,1456,2022-03-15,2024-03-10,true,Premium,Active engagement platform
ne-8f2c1a4b9c3d7e8f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f,Instagram,ne.omaha.creator,https://instagram.com/ne.omaha.creator,,,false,28456,1203,892,2022-05-20,2024-03-08,false,Basic,Discovery platform
ia-91a77b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1,OnlyFans,ia_desmoines,https://onlyfans.com/ia_desmoines,Beacons,https://beacons.ai/ia_desmoines,null,3847,12,234,2023-01-10,2024-03-11,true,Premium,Primary monetization


JSON Schema

{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "creator_id": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$",
      "description": "Creator unique identifier"
    },
    "platform": {
      "type": "string",
      "enum": ["X", "Instagram", "TikTok", "Reddit", "OnlyFans", "Fansly", "ManyVids", "YouTube", "Twitch", "Other"]
    },
    "handle": {
      "type": "string",
      "pattern": "^[a-zA-Z0-9_]+$",
      "description": "Platform handle without @ symbol"
    },
    "url": {
      "type": "string",
      "format": "uri",
      "description": "Full profile URL"
    },
    "linked_hub": {
      "type": "string",
      "enum": ["Linktree", "Beacons", "Carrd", "Custom", "None", "Unknown", null]
    },
    "linked_hub_url": {
      "type": "string",
      "format": "uri",
      "description": "Link hub URL"
    },
    "is_verified": {
      "type": ["boolean", "null"],
      "description": "Platform verification badge"
    },
    "followers_count": {
      "type": ["integer", "null"],
      "minimum": 0,
      "description": "Current followers count"
    },
    "following_count": {
      "type": ["integer", "null"],
      "minimum": 0,
      "description": "Current following count"
    },
    "posts_count": {
      "type": ["integer", "null"],
      "minimum": 0,
      "description": "Total posts count"
    },
    "account_created": {
      "type": "string",
      "format": "date",
      "description": "Account creation date"
    },
    "last_activity": {
      "type": "string",
      "format": "date",
      "description": "Last post/activity date"
    },
    "is_primary": {
      "type": ["boolean", "null"],
      "description": "Primary platform indicator"
    },
    "platform_tier": {
      "type": "string",
      "enum": ["Basic", "Premium", "Pro", "Enterprise", "Unknown", null]
    },
    "notes": {
      "type": "string",
      "maxLength": 300,
      "description": "Additional platform notes"
    }
  },
  "required": ["creator_id", "platform", "handle", "url"]
}
