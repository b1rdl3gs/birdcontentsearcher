
#!/usr/bin/env python3
"""
Verification Checker for Creator Economy Research

This script implements the verification framework for creator location
and business claims according to the methodology specifications.
"""

import pandas as pd
import re
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Set
import logging
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VerificationChecker:
    """
    Implements verification framework for creator research.
    """
    
    def __init__(self, data_dir: str = "../data"):
        """
        Initialize the verification checker.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = data_dir
        self.state_keywords = {
            'NE': ['nebraska', 'ne', 'omaha', 'lincoln', 'grand island', 'kearney', 'bellevue', 'fremont'],
            'IA': ['iowa', 'ia', 'des moines', 'dsm', 'cedar rapids', 'iowa city', 'davenport', 'waterloo', 'ames']
        }
        
        self.platform_patterns = {
            'X': r'twitter\.com/\w+',
            'Instagram': r'instagram\.com/\w+',
            'TikTok': r'tiktok\.com/@\w+',
            'Reddit': r'reddit\.com/u/\w+',
            'OnlyFans': r'onlyfans\.com/\w+',
            'Fansly': r'fansly\.com/\w+',
            'ManyVids': r'manyvids\.com/\w+'
        }
        
        self.signal_weights = {
            'high': {
                'registered_business': 0.9,
                'press_interview': 0.85,
                'event_booking': 0.8,
                'bio_consistent': 0.8
            },
            'medium': {
                'geotag_multiple': 0.6,
                'collaboration_local': 0.55,
                'city_mentions': 0.5
            },
            'low': {
                'single_hashtag': 0.3,
                'sporadic_reference': 0.25,
                'ambiguous_post': 0.2
            }
        }
        
    def load_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load verification data files.
        
        Returns:
            Dictionary containing DataFrames for each data type
        """
        data = {}
        
        try:
            # Load creators data
            data['creators'] = pd.read_csv(f"{self.data_dir}/exports/creators.csv")
            
            # Load evidence data
            data['evidence'] = pd.read_csv(f"{self.data_dir}/exports/evidence.csv")
            
            # Load platforms data
            data['platforms'] = pd.read_csv(f"{self.data_dir}/exports/platforms.csv")
            
        except FileNotFoundError as e:
            logger.error(f"Data file not found: {e}")
            raise
        except pd.errors.EmptyDataError:
            logger.warning("Some data files are empty")
            data = {
                'creators': pd.DataFrame(columns=['creator_id', 'state', 'verification_confidence']),
                'evidence': pd.DataFrame(columns=['creator_id', 'signal_type', 'weight']),
                'platforms': pd.DataFrame(columns=['creator_id', 'platform', 'handle'])
            }
        
        return data
    
    def extract_creator_id(self, handle: str, platform: str) -> str:
        """
        Generate anonymized creator ID from handle and platform.
        
        Args:
            handle: Creator handle
            platform: Platform name
            
        Returns:
            SHA-256 hash as creator ID
        """
        content = f"{handle}@{platform}".lower()
        return hashlib.sha256(content.encode()).hexdigest()
    
    def detect_location_mentions(self, text: str) -> Dict[str, List[str]]:
        """
        Detect location mentions in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary mapping states to found location keywords
        """
        if pd.isna(text) or not text:
            return {}
        
        text_lower = text.lower()
        found_locations = {}
        
        for state, keywords in self.state_keywords.items():
            found_keywords = []
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords.append(keyword)
            
            if found_keywords:
                found_locations[state] = found_keywords
        
        return found_locations
    
    def verify_bio_location(self, bio_text: str, creator_state: str) -> Tuple[float, str]:
        """
        Verify location claims in creator bio.
        
        Args:
            bio_text: Creator bio text
            creator_state: Expected state (NE/IA)
            
        Returns:
            Tuple of (confidence_score, verification_notes)
        """
        if pd.isna(bio_text) or not bio_text:
            return 0.0, "No bio available"
        
        locations = self.detect_location_mentions(bio_text)
        
        # High confidence: exact state match in bio
        if creator_state in locations:
            state_keywords = self.state_keywords[creator_state]
            found_state_keywords = [kw for kw in state_keywords if kw in bio_text.lower()]
            
            if len(found_state_keywords) >= 2:
                return 0.8, f"Multiple location references: {', '.join(found_state_keywords)}"
            elif len(found_state_keywords) == 1:
                return 0.7, f"Single location reference: {found_state_keywords[0]}"
        
        # Medium confidence: nearby location mentions
        for state, keywords in locations.items():
            if state != creator_state and len(keywords) >= 2:
                return 0.4, f"Multiple {state} references: {', '.join(keywords)}"
        
        # Low confidence: single hashtag or mention
        if locations:
            state, keywords = list(locations.items())[0]
            return 0.25, f"Single {state} reference: {keywords[0]}"
        
        return 0.0, "No location references found"
    
    def verify_geotag_consistency(self, creator_id: str, evidence_data: pd.DataFrame) -> Tuple[float, str]:
        """
        Verify geotag consistency over time.
        
        Args:
            creator_id: Creator identifier
            evidence_data: Evidence DataFrame
            
        Returns:
            Tuple of (confidence_score, verification_notes)
        """
        creator_evidence = evidence_data[
            (evidence_data['creator_id'] == creator_id) & 
            (evidence_data['signal_type'] == 'geotag')
        ]
        
        if creator_evidence.empty:
            return 0.0, "No geotag evidence"
        
        # Count geotags by date range
        recent_evidence = creator_evidence[
            pd.to_datetime(creator_evidence['collection_date']) > datetime.now() - timedelta(days=90)
        ]
        
        if len(recent_evidence) >= 5:
            return 0.6, f"Consistent geotags: {len(recent_evidence)} recent instances"
        elif len(recent_evidence) >= 2:
            return 0.4, f"Multiple geotags: {len(recent_evidence)} recent instances"
        elif len(recent_evidence) == 1:
            return 0.2, "Single recent geotag"
        else:
            # Check older geotags
            if len(creator_evidence) >= 3:
                return 0.3, f"Historical geotags: {len(creator_evidence)} instances (older)"
            else:
                return 0.15, f"Few historical geotags: {len(creator_evidence)} instances"
    
    def verify_business_registration(self, creator_id: str, evidence_data: pd.DataFrame, creator_state: str) -> Tuple[float, str]:
        """
        Verify business registration evidence.
        
        Args:
            creator_id: Creator identifier
            evidence_data: Evidence DataFrame
            creator_state: Expected state
            
        Returns:
            Tuple of (confidence_score, verification_notes)
        """
        creator_evidence = evidence_data[
            (evidence_data['creator_id'] == creator_id) & 
            (evidence_data['signal_type'] == 'registry')
        ]
        
        if creator_evidence.empty:
            return 0.0, "No business registration evidence"
        
        # Check for state-specific registration
        state_evidence = creator_evidence[
            creator_evidence['description'].str.contains(creator_state, case=False, na=False)
        ]
        
        if len(state_evidence) >= 1:
            return 0.9, f"Business registered in {creator_state}"
        
        # Check for any registration
        if len(creator_evidence) >= 1:
            return 0.5, "Business registration found (state unclear)"
        
        return 0.0, "No valid registration evidence"
    
    def verify_collaboration_evidence(self, creator_id: str, evidence_data: pd.DataFrame, creator_state: str) -> Tuple[float, str]:
        """
        Verify collaboration evidence with local entities.
        
        Args:
            creator_id: Creator identifier
            evidence_data: Evidence DataFrame
            creator_state: Expected state
            
        Returns:
            Tuple of (confidence_score, verification_notes)
        """
        creator_evidence = evidence_data[
            (evidence_data['creator_id'] == creator_id) & 
            (evidence_data['signal_type'] == 'collaboration')
        ]
        
        if creator_evidence.empty:
            return 0.0, "No collaboration evidence"
        
        # Check for state-specific collaborations
        state_keywords = self.state_keywords[creator_state]
        state_collabs = 0
        
        for _, evidence in creator_evidence.iterrows():
            description = str(evidence['description']).lower()
            if any(keyword in description for keyword in state_keywords):
                state_collabs += 1
        
        if state_collabs >= 3:
            return 0.55, f"Multiple {creator_state} collaborations: {state_collabs} instances"
        elif state_collabs >= 1:
            return 0.4, f"{creator_state} collaboration: {state_collabs} instance"
        else:
            return 0.2, f"Collaborations found but not {creator_state}-specific"
    
    def verify_platform_consistency(self, creator_id: str, platforms_data: pd.DataFrame) -> Tuple[float, str]:
        """
        Verify consistency across platforms.
        
        Args:
            creator_id: Creator identifier
            platforms_data: Platforms DataFrame
            
        Returns:
            Tuple of (confidence_score, verification_notes)
        """
        creator_platforms = platforms_data[platforms_data['creator_id'] == creator_id]
        
        if len(creator_platforms) <= 1:
            return 0.1, "Single platform presence"
        
        # Check for link hubs
        linked_platforms = creator_platforms[
            creator_platforms['linked_hub'].notna() & 
            (creator_platforms['linked_hub'] != '') & 
            (creator_platforms['linked_hub'] != 'None')
        ]
        
        # Check handle consistency
        handles = creator_platforms['handle'].str.lower().tolist()
        base_handles = set()
        
        for handle in handles:
            # Remove platform-specific prefixes/suffixes
            clean_handle = re.sub(r'[_\-](of|fans|creator|official)$', '', handle)
            base_handles.add(clean_handle)
        
        consistency_score = 0.0
        notes = []
        
        # Link hubs increase confidence
        if len(linked_platforms) >= 2:
            consistency_score += 0.3
            notes.append(f"Multiple link hubs: {len(linked_platforms)}")
        elif len(linked_platforms) == 1:
            consistency_score += 0.15
            notes.append(f"Single link hub")
        
        # Handle consistency increases confidence
        if len(base_handles) <= 2 and len(handles) >= 3:  # Similar handles across platforms
            consistency_score += 0.2
            notes.append("Consistent handles across platforms")
        elif len(base_handles) <= 3:
            consistency_score += 0.1
            notes.append("Moderately consistent handles")
        
        # Platform diversity
        if len(creator_platforms) >= 4:
            consistency_score += 0.1
            notes.append(f"High platform diversity: {len(creator_platforms)} platforms")
        elif len(creator_platforms) >= 2:
            consistency_score += 0.05
            notes.append(f"Multiple platforms: {len(creator_platforms)} platforms")
        
        return min(consistency_score, 0.5), "; ".join(notes) if notes else "Basic platform presence"
    
    def calculate_overall_confidence(self, verification_scores: Dict[str, Tuple[float, str]], creator_state: str) -> Tuple[float, str, Dict]:
        """
        Calculate overall verification confidence.
        
        Args:
            verification_scores: Dictionary of verification scores by type
            creator_state: Expected state
            
        Returns:
            Tuple of (overall_confidence, confidence_level, breakdown)
        """
        # Weight different verification types
        weights = {
            'business_registration': 0.3,
            'bio_location': 0.25,
            'geotag_consistency': 0.2,
            'collaboration_evidence': 0.15,
            'platform_consistency': 0.1
        }
        
        weighted_score = 0.0
        breakdown = {}
        
        for verify_type, (score, notes) in verification_scores.items():
            weight = weights.get(verify_type, 0.0)
            contribution = score * weight
            weighted_score += contribution
            
            breakdown[verify_type] = {
                'score': score,
                'weight': weight,
                'contribution': contribution,
                'notes': notes
            }
        
        overall_confidence = min(weighted_score, 1.0)
        
        # Determine confidence level
        if overall_confidence >= 0.75:
            confidence_level = "High"
        elif overall_confidence >= 0.5:
            confidence_level = "Medium"
        elif overall_confidence >= 0.25:
            confidence_level = "Low"
        else:
            confidence_level = "Undetermined"
        
        return overall_confidence, confidence_level, breakdown
    
    def verify_creator(self, creator_id: str, data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Complete verification for a single creator.
        
        Args:
            creator_id: Creator identifier
            data: Dictionary containing all data DataFrames
            
        Returns:
            Dictionary with verification results
        """
        # Get creator info
        creator_info = data['creators'][data['creators']['creator_id'] == creator_id]
        if creator_info.empty:
            return {'error': 'Creator not found'}
        
        creator = creator_info.iloc[0]
        creator_state = creator.get('state', 'Undetermined')
        
        verification_results = {}
        
        # Verify bio location
        platforms = data['platforms'][data['platforms']['creator_id'] == creator_id]
        bio_text = None
        for _, platform in platforms.iterrows():
            # In real implementation, would fetch bio from platform
            bio_text = f"Creator bio for {platform.get('handle')}"  # Placeholder
            break
        
        bio_score, bio_notes = self.verify_bio_location(bio_text, creator_state)
        verification_results['bio_location'] = (bio_score, bio_notes)
        
        # Verify geotag consistency
        geotag_score, geotag_notes = self.verify_geotag_consistency(creator_id, data['evidence'])
        verification_results['geotag_consistency'] = (geotag_score, geotag_notes)
        
        # Verify business registration
        business_score, business_notes = self.verify_business_registration(creator_id, data['evidence'], creator_state)
        verification_results['business_registration'] = (business_score, business_notes)
        
        # Verify collaboration evidence
        collab_score, collab_notes = self.verify_collaboration_evidence(creator_id, data['evidence'], creator_state)
        verification_results['collaboration_evidence'] = (collab_score, collab_notes)
        
        # Verify platform consistency
        platform_score, platform_notes = self.verify_platform_consistency(creator_id, platforms)
        verification_results['platform_consistency'] = (platform_score, platform_notes)
        
        # Calculate overall confidence
        overall_confidence, confidence_level, breakdown = self.calculate_overall_confidence(
            verification_results, creator_state
        )
        
        return {
            'creator_id': creator_id,
            'creator_state': creator_state,
            'overall_confidence': overall_confidence,
            'confidence_level': confidence_level,
            'verification_breakdown': breakdown,
            'verification_timestamp': datetime.now().isoformat()
        }
    
    def run_verification_audit(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Run verification audit on all creators.
        
        Args:
            data: Dictionary containing all data DataFrames
            
        Returns:
            DataFrame with verification results
        """
        verification_results = []
        
        for creator_id in data['creators']['creator_id'].unique():
            try:
                result = self.verify_creator(creator_id, data)
                
                if 'error' not in result:
                    # Flatten results for CSV output
                    row = {
                        'creator_id': result['creator_id'],
                        'creator_state': result['creator_state'],
                        'overall_confidence': result['overall_confidence'],
                        'confidence_level': result['confidence_level'],
                        'verification_timestamp': result['verification_timestamp']
                    }
                    
                    # Add individual verification scores
                    for verify_type, details in result['verification_breakdown'].items():
                        row[f'{verify_type}_score'] = details['score']
                        row[f'{verify_type}_notes'] = details['notes']
                    
                    verification_results.append(row)
                    
            except Exception as e:
                logger.error(f"Error verifying creator {creator_id}: {e}")
                continue
        
        return pd.DataFrame(verification_results)
    
    def generate_verification_report(self, verification_df: pd.DataFrame) -> Dict:
        """
        Generate verification summary report.
        
        Args:
            verification_df: DataFrame with verification results
            
        Returns:
            Dictionary with verification summary
        """
        if verification_df.empty:
            return {'error': 'No verification data available'}
        
        report = {
            'total_creators': len(verification_df),
            'confidence_distribution': verification_df['confidence_level'].value_counts().to_dict(),
            'average_confidence': verification_df['overall_confidence'].mean(),
            'state_breakdown': {},
            'verification_stats': {}
        }
        
        # State breakdown
        for state in ['NE', 'IA']:
            state_data = verification_df[verification_df['creator_state'] == state]
            if not state_data.empty:
                report['state_breakdown'][state] = {
                    'count': len(state_data),
                    'avg_confidence': state_data['overall_confidence'].mean(),
                    'confidence_levels': state_data['confidence_level'].value_counts().to_dict()
                }
        
        # Verification type statistics
        verification_types = ['bio_location', 'geotag_consistency', 'business_registration', 'collaboration_evidence', 'platform_consistency']
        
        for verify_type in verification_types:
            score_col = f'{verify_type}_score'
            if score_col in verification_df.columns:
                report['verification_stats'][verify_type] = {
                    'avg_score': verification_df[score_col].mean(),
                    'max_score': verification_df[score_col].max(),
                    'min_score': verification_df[score_col].min(),
                    'creators_with_evidence': (verification_df[score_col] > 0).sum()
                }
        
        return report


def main():
    """
    Main function to run verification audit.
    """
    checker = VerificationChecker()
    
    try:
        # Load data
        data = checker.load_data()
        
        # Run verification audit
        verification_results = checker.run_verification_audit(data)
        
        # Save results
        if not verification_results.empty:
            verification_results.to_csv("../data/exports/verification_results.csv", index=False)
            logger.info(f"Saved verification results for {len(verification_results)} creators")
        
        # Generate report
        report = checker.generate_verification_report(verification_results)
        
        # Save report
        with open("../data/exports/verification_report.json", 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info("Verification audit completed successfully")
        logger.info(f"Average confidence score: {report.get('average_confidence', 0):.3f}")
        
    except Exception as e:
        logger.error(f"Error in verification audit: {e}")
        raise


if __name__ == "__main__":
    main()
