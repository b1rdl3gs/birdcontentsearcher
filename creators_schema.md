Creator Master Record Schema

Table: creators.csv

Description

Master record for each verified creator with location and business information.


Fields

Field Name	Data Type	Required	Description	Validation
creator_id	string	Yes	Unique anonymized identifier (SHA-256 hash)	Regex: ^[a-f0-9]{64}$
state	string	Yes	State abbreviation	Values: NE, IA, Undetermined
city_region	string	Yes	Metropolitan region	Values: Omaha, Lincoln, DesMoines, CedarRapids, IowaCity, GrandIsland, Kearney, OnlineOnly, Undetermined
verification_confidence	float	Yes	Confidence score in [0,1]	Min: 0.0, Max: 1.0
verification_level	string	Yes	Verification confidence level	Values: High, Medium, Low, Undetermined
primary_platform	string	Yes	Main platform for creator business	Values: X, Instagram, TikTok, Reddit, OnlyFans, Fansly, ManyVids, Undetermined
content_types	string	Yes	Content category tags	Format: comma-separated values
first_seen	date	Yes	First discovery date	Format: YYYY-MM-DD
last_active	date	Yes	Last activity date	Format: YYYY-MM-DD
business_entity_type	string	No	Business registration type	Values: LLC, SoleProprietorship, Partnership, Corporation, Unknown, NotApplicable
has_agency_affiliation	boolean	No	Agency affiliation status	Values: true, false, null
estimated_tier	string	No	Creator tier based on metrics	Values: Micro, Mid, Macro, Top, Undetermined
notes	text	No	Additional verification notes	Max: 500 characters

Content Types Values
• solo
• duo
• studio
• cosplay
• alt
• glamour
• fetish
• fitness
• lifestyle
• customs
• premium
• other


CSV Template

creator_id,state,city_region,verification_confidence,verification_level,primary_platform,content_types,first_seen,last_active,business_entity_type,has_agency_affiliation,estimated_tier,notes
ne-8f2c1a4b9c3d7e8f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f,NE,Omaha,0.82,High,X,solo,cosplay,2024-01-15,2024-03-10,LLC,false,Mid,High confidence due to registered business
ia-91a77b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1,IA,DesMoines,0.76,Medium,Instagram,alt,fitness,2024-02-01,2024-03-12,SoleProprietorship,true,Mid,Verified through multiple location signals


JSON Schema

{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "creator_id": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$",
      "description": "Unique anonymized identifier"
    },
    "state": {
      "type": "string",
      "enum": ["NE", "IA", "Undetermined"]
    },
    "city_region": {
      "type": "string",
      "enum": ["Omaha", "Lincoln", "DesMoines", "CedarRapids", "IowaCity", "GrandIsland", "Kearney", "OnlineOnly", "Undetermined"]
    },
    "verification_confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    },
    "verification_level": {
      "type": "string",
      "enum": ["High", "Medium", "Low", "Undetermined"]
    },
    "primary_platform": {
      "type": "string",
      "enum": ["X", "Instagram", "TikTok", "Reddit", "OnlyFans", "Fansly", "ManyVids", "Undetermined"]
    },
    "content_types": {
      "type": "string",
      "pattern": "^[a-z,]+$"
    },
    "first_seen": {
      "type": "string",
      "format": "date"
    },
    "last_active": {
      "type": "string",
      "format": "date"
    },
    "business_entity_type": {
      "type": "string",
      "enum": ["LLC", "SoleProprietorship", "Partnership", "Corporation", "Unknown", "NotApplicable"]
    },
    "has_agency_affiliation": {
      "type": ["boolean", "null"]
    },
    "estimated_tier": {
      "type": "string",
      "enum": ["Micro", "Mid", "Macro", "Top", "Undetermined"]
    },
    "notes": {
      "type": "string",
      "maxLength": 500
    }
  },
  "required": ["creator_id", "state", "city_region", "verification_confidence", "verification_level", "primary_platform", "content_types", "first_seen", "last_active"]
}
