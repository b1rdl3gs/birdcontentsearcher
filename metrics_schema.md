Public Engagement Metrics Schema

Table: metrics.csv

Description

Time-series engagement metrics for creator platforms.


Fields

Field Name	Data Type	Required	Description	Validation
creator_id	string	Yes	Creator unique identifier	Foreign key to creators.creator_id
platform	string	Yes	Platform name	Values: X, Instagram, TikTok, Reddit, OnlyFans, Fansly, ManyVids, YouTube, Twitch, Other
snapshot_date	date	Yes	Date of metric collection	Format: YYYY-MM-DD
followers	integer	No	Followers count	Non-negative integer
following	integer	No	Following count	Non-negative integer
posts_count	integer	No	Total posts count	Non-negative integer
avg_likes_post	float	No	Average likes per post	Non-negative float
avg_comments_post	float	No	Average comments per post	Non-negative float
avg_shares_post	float	No	Average shares per post	Non-negative float
engagement_rate	float	No	Calculated engagement rate	Format: decimal (0.05 = 5%)
recent_posts_count	integer	No	Posts in last 30 days	Non-negative integer
story_views_avg	float	No	Average story views	Non-negative float
video_views_avg	float	No	Average video views	Non-negative float
subscriber_count	integer	No	Subscriber count (subscription platforms)	Non-negative integer
monthly_revenue_estimate	float	No	Estimated monthly revenue	Non-negative float
growth_rate_30d	float	No	30-day growth rate	Format: decimal
data_source	string	No	Source of metric data	Values: API, Scraping, Manual, Estimate
collection_method	string	No	Collection method details	Max: 100 characters
notes	text	No	Additional metric notes	Max: 300 characters

Calculated Fields

Engagement Rate Formula

ER_post = (avg_likes_post + avg_comments_post) / followers


Growth Rate Formula

Growth_30d = (followers_current - followers_30d_ago) / followers_30d_ago


CSV Template

creator_id,platform,snapshot_date,followers,following,posts_count,avg_likes_post,avg_comments_post,avg_shares_post,engagement_rate,recent_posts_count,story_views_avg,video_views_avg,subscriber_count,monthly_revenue_estimate,growth_rate_30d,data_source,collection_method,notes
ne-8f2c1a4b9c3d7e8f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f,X,2024-03-10,15234,892,1456,234.5,45.2,12.8,0.0183,28,3421.5,5678.3,null,null,0.0234,API,TwitterAPI,v4.0 endpoint
ne-8f2c1a4b9c3d7e8f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f,Instagram,2024-03-10,28456,1203,892,1567.8,234.1,67.3,0.0635,15,8923.4,12345.6,null,null,0.0456,Scraping,BeautifulSoup,Mobile user agent
ia-91a77b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1,OnlyFans,2024-03-11,3847,12,234,null,null,null,null,8,2456.7,null,3847,5432.10,0.0876,Manual,DirectObservation,Free follower count visible


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
    "snapshot_date": {
      "type": "string",
      "format": "date",
      "description": "Date of metric collection"
    },
    "followers": {
      "type": ["integer", "null"],
      "minimum": 0,
      "description": "Followers count"
    },
    "following": {
      "type": ["integer", "null"],
      "minimum": 0,
      "description": "Following count"
    },
    "posts_count": {
      "type": ["integer", "null"],
      "minimum": 0,
      "description": "Total posts count"
    },
    "avg_likes_post": {
      "type": ["number", "null"],
      "minimum": 0,
      "description": "Average likes per post"
    },
    "avg_comments_post": {
      "type": ["number", "null"],
      "minimum": 0,
      "description": "Average comments per post"
    },
    "avg_shares_post": {
      "type": ["number", "null"],
      "minimum": 0,
      "description": "Average shares per post"
    },
    "engagement_rate": {
      "type": ["number", "null"],
      "minimum": 0,
      "description": "Calculated engagement rate"
    },
    "recent_posts_count": {
      "type": ["integer", "null"],
      "minimum": 0,
      "description": "Posts in last 30 days"
    },
    "story_views_avg": {
      "type": ["number", "null"],
      "minimum": 0,
      "description": "Average story views"
    },
    "video_views_avg": {
      "type": ["number", "null"],
      "minimum": 0,
      "description": "Average video views"
    },
    "subscriber_count": {
      "type": ["integer", "null"],
      "minimum": 0,
      "description": "Subscriber count"
    },
    "monthly_revenue_estimate": {
      "type": ["number", "null"],
      "minimum": 0,
      "description": "Estimated monthly revenue"
    },
    "growth_rate_30d": {
      "type": ["number", "null"],
      "description": "30-day growth rate"
    },
    "data_source": {
      "type": "string",
      "enum": ["API", "Scraping", "Manual", "Estimate", null],
      "description": "Source of metric data"
    },
    "collection_method": {
      "type": "string",
      "maxLength": 100,
      "description": "Collection method details"
    },
    "notes": {
      "type": "string",
      "maxLength": 300,
      "description": "Additional metric notes"
    }
  },
  "required": ["creator_id", "platform", "snapshot_date"]
}


Additional Metrics Tables

Engagement Details (engagement_details.csv)

For detailed post-level analysis:
• creator_id, platform, post_id, post_date, likes, comments, shares, views, content_type


Historical Snapshots (historical_snapshots.csv)

For longitudinal analysis:
• creator_id, snapshot_date, total_platforms, total_followers, avg_engagement, estimated_tier
