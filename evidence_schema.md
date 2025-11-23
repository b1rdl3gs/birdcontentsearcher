Evidence Audit Schema

Table: evidence.csv

Description

Verification evidence and audit trail for creator location and business claims.


Fields

Field Name	Data Type	Required	Description	Validation
creator_id	string	Yes	Creator unique identifier	Foreign key to creators.creator_id
evidence_id	string	Yes	Unique evidence identifier	UUID format
signal_type	string	Yes	Type of verification signal	Values: bio, press, geotag, event, registry, collaboration, business, other
signal_subtype	string	No	Subcategory of signal	Varies by signal_type
description	text	No	Evidence description	Max: 1000 characters
url	string	No	Source URL	Valid URL format
screenshot_path	string	No	Screenshot file path	File path reference
excerpt	text	No	Relevant text excerpt	Max: 500 characters
weight	float	Yes	Evidence weight in [0,1]	Min: 0.0, Max: 1.0
confidence_impact	float	No	Impact on overall confidence	Min: -1.0, Max: 1.0
collection_date	date	Yes	Date evidence collected	Format: YYYY-MM-DD
collector	string	No	Who collected evidence	Max: 100 characters
verification_status	string	No	Evidence verification status	Values: Verified, Pending, Disputed, Invalid
is_public	boolean	No	Evidence is publicly accessible	Values: true, false
expires_date	date	No	Evidence expiration date	Format: YYYY-MM-DD
tags	string	No	Evidence tags	Format: comma-separated values
notes	text	No	Additional notes	Max: 300 characters

Signal Types and Subtypes

bio (Bio Information)
• location_mention: Explicit location in bio
• business_mention: Business info in bio
• contact_info: Contact information in bio
• state_reference: State reference in bio


press (Media Coverage)
• interview: Creator interview
• feature: Media feature article
• mention: Media mention
• profile: Professional profile


geotag (Geographic Tags)
• post_geotag: Geotagged post
• story_geotag: Geotagged story
• check_in: Location check-in
• venue_tag: Venue tagging


event (Event Participation)
• booking: Event booking confirmation
• appearance: Event appearance
• performance: Performance listing
• hosting: Event hosting


registry (Business Records)
• llc_filing: LLC registration filing
• business_license: Business license record
• dba_filing: DBA registration
• permit: Business permit record


collaboration (Collaboration Evidence)
• photographer_tag: Local photographer tag
• studio_credit: Studio credit
• local_collab: Local collaborator mention
• joint_project: Joint project credit


business (Business Evidence)
• website: Business website
• email_domain: Business email domain
• phone_number: Business phone listing
• address: Business address listing


CSV Template

creator_id,evidence_id,signal_type,signal_subtype,description,url,screenshot_path,excerpt,weight,confidence_impact,collection_date,collector,verification_status,is_public,expires_date,tags,notes
ne-8f2c1a4b9c3d7e8f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f,evidence-001,bio,location_mention,Creator bio states "Omaha, NE based" and mentions local studio,https://twitter.com/ne_omaha_creator,screenshots/bio_ne_omaha.png,"Omaha, NE | Professional Content Creator",0.8,0.15,2024-03-10,auto_bot,Verified,true,2024-06-10,location,bio,High confidence bio signal
ia-91a77b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1,evidence-002,geotag,post_geotag,Instagram post geotagged to downtown Des Moines venue,https://instagram.com/p/abc123,,null,0.6,0.10,2024-03-08,auto_bot,Verified,true,2024-06-08,geotag,instagram,Multiple geotags over 30 days


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
    "evidence_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique evidence identifier"
    },
    "signal_type": {
      "type": "string",
      "enum": ["bio", "press", "geotag", "event", "registry", "collaboration", "business", "other"],
      "description": "Type of verification signal"
    },
    "signal_subtype": {
      "type": "string",
      "description": "Subcategory of signal"
    },
    "description": {
      "type": "string",
      "maxLength": 1000,
      "description": "Evidence description"
    },
    "url": {
      "type": "string",
      "format": "uri",
      "description": "Source URL"
    },
    "screenshot_path": {
      "type": "string",
      "description": "Screenshot file path"
    },
    "excerpt": {
      "type": "string",
      "maxLength": 500,
      "description": "Relevant text excerpt"
    },
    "weight": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Evidence weight"
    },
    "confidence_impact": {
      "type": "number",
      "minimum": -1.0,
      "maximum": 1.0,
      "description": "Impact on overall confidence"
    },
    "collection_date": {
      "type": "string",
      "format": "date",
      "description": "Date evidence collected"
    },
    "collector": {
      "type": "string",
      "maxLength": 100,
      "description": "Who collected evidence"
    },
    "verification_status": {
      "type": "string",
      "enum": ["Verified", "Pending", "Disputed", "Invalid", null],
      "description": "Evidence verification status"
    },
    "is_public": {
      "type": ["boolean", "null"],
      "description": "Evidence is publicly accessible"
    },
    "expires_date": {
      "type": "string",
      "format": "date",
      "description": "Evidence expiration date"
    },
    "tags": {
      "type": "string",
      "description": "Evidence tags (comma-separated)"
    },
    "notes": {
      "type": "string",
      "maxLength": 300,
      "description": "Additional notes"
    }
  },
  "required": ["creator_id", "evidence_id", "signal_type", "weight", "collection_date"]
}


Evidence Collection Protocol

Quality Standards
1. **Screenshot Capture**: Always capture visual evidence when available
2. **URL Preservation**: Store direct URLs with timestamps
3. **Text Excerpts**: Extract relevant text snippets
4. **Weight Assignment**: Use standardized weight guidelines
5. **Regular Audits**: Review evidence for accuracy and relevance


Storage Requirements
• Screenshots stored in `/screenshots/` directory
• Evidence files organized by creator_id
• Regular backup of all evidence materials
• Secure access controls for sensitive evidence


Verification Workflow
1. **Collection**: Automated or manual evidence gathering
2. **Validation**: Verify evidence authenticity and relevance
3. **Weight Assignment**: Apply standardized scoring
4. **Impact Calculation**: Calculate confidence impact
5. **Review**: Manual review of high-value evidence
6. **Archive**: Store with appropriate metadata
