Business and Market Presence Schema

Table: business.csv

Description

Business entity information and market presence for creators.


Fields

Field Name	Data Type	Required	Description	Validation
creator_id	string	Yes	Creator unique identifier	Foreign key to creators.creator_id
business_entity	string	No	Business registration type	Values: LLC, SoleProprietorship, Partnership, Corporation, Unknown, NotApplicable
business_name	string	No	Registered business name	Max: 200 characters
registration_state	string	No	State of business registration	Values: NE, IA, Other, Unknown
registration_date	date	No	Business registration date	Format: YYYY-MM-DD
business_license	string	No	Business license number	Max: 50 characters
booking_email	string	No	Public business booking email	Email format validation
contact_phone	string	No	Public business phone	Phone format validation
website_url	string	No	Business website	Valid URL format
agency_affiliation	string	No	Agency name	Max: 200 characters
agency_type	string	No	Agency relationship type	Values: Exclusive, NonExclusive, Management, Booking, Unknown
shopfronts	string	No	Shop platforms	Format: comma-separated values
pricing_visible	string	No	Pricing visibility level	Values: Yes, No, Partial, Hidden
payment_methods	string	No	Accepted payment methods	Format: comma-separated values
services_offered	string	No	Services provided	Format: comma-separated values
collaboration_open	boolean	No	Open to collaborations	Values: true, false, null
booking_required	boolean	No	Booking requirement status	Values: true, false, null
business_description	text	No	Business description	Max: 500 characters
notes	text	No	Additional business notes	Max: 300 characters

Shopfront Values
• ManyVids
• Clip4Sale
• Customs4U
• Clips4Sale
• iWantClips
• Other


Payment Method Values
• CreditCard
• PayPal
• Crypto
• CashApp
• Venmo
• BankTransfer
• Other


Service Types
• Photosets
• Videos
• LiveStreams
• Customs
• VideoCalls
• Messaging
• MeetAndGreet
• Other


CSV Template

creator_id,business_entity,business_name,registration_state,registration_date,business_license,booking_email,contact_phone,website_url,agency_affiliation,agency_type,shopfronts,pricing_visible,payment_methods,services_offered,collaboration_open,booking_required,business_description,notes
ne-8f2c1a4b9c3d7e8f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f,LLC,Omaha Creations LLC,NE,2023-06-15,2023-LLC-0847,bookings@omahacreations.com,555-0123,https://omahacreations.com,,NonExclusive,ManyVids,Partial,CreditCard,PayPal,Photosets,Videos,Customs,true,true,Professional content creation studio specializing in glamour and cosplay photography,Fully licensed and insured
ia-91a77b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1,SoleProprietorship,,IA,,,,,,,,,,,Customs4Sale,Yes,Crypto,PayPal,Customs,VideoCalls,true,false,Independent creator offering custom content and video calls,Operates independently


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
    "business_entity": {
      "type": "string",
      "enum": ["LLC", "SoleProprietorship", "Partnership", "Corporation", "Unknown", "NotApplicable", null],
      "description": "Business registration type"
    },
    "business_name": {
      "type": "string",
      "maxLength": 200,
      "description": "Registered business name"
    },
    "registration_state": {
      "type": "string",
      "enum": ["NE", "IA", "Other", "Unknown", null],
      "description": "State of business registration"
    },
    "registration_date": {
      "type": "string",
      "format": "date",
      "description": "Business registration date"
    },
    "business_license": {
      "type": "string",
      "maxLength": 50,
      "description": "Business license number"
    },
    "booking_email": {
      "type": "string",
      "format": "email",
      "description": "Public business booking email"
    },
    "contact_phone": {
      "type": "string",
      "maxLength": 20,
      "description": "Public business phone"
    },
    "website_url": {
      "type": "string",
      "format": "uri",
      "description": "Business website"
    },
    "agency_affiliation": {
      "type": "string",
      "maxLength": 200,
      "description": "Agency name"
    },
    "agency_type": {
      "type": "string",
      "enum": ["Exclusive", "NonExclusive", "Management", "Booking", "Unknown", null],
      "description": "Agency relationship type"
    },
    "shopfronts": {
      "type": "string",
      "description": "Shop platforms (comma-separated)"
    },
    "pricing_visible": {
      "type": "string",
      "enum": ["Yes", "No", "Partial", "Hidden", null],
      "description": "Pricing visibility level"
    },
    "payment_methods": {
      "type": "string",
      "description": "Accepted payment methods (comma-separated)"
    },
    "services_offered": {
      "type": "string",
      "description": "Services provided (comma-separated)"
    },
    "collaboration_open": {
      "type": ["boolean", "null"],
      "description": "Open to collaborations"
    },
    "booking_required": {
      "type": ["boolean", "null"],
      "description": "Booking requirement status"
    },
    "business_description": {
      "type": "string",
      "maxLength": 500,
      "description": "Business description"
    },
    "notes": {
      "type": "string",
      "maxLength": 300,
      "description": "Additional business notes"
    }
  },
  "required": ["creator_id"]
}
