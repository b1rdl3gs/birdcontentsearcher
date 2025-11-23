
#!/usr/bin/env python3
"""
Metrics Calculator for Creator Economy Research

This script calculates various engagement and business metrics for creators
based on the collected data following the methodology specifications.
"""

import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MetricsCalculator:
    """
    Calculates engagement and business metrics for creator economy research.
    """
    
    def __init__(self, data_dir: str = "../data"):
        """
        Initialize the metrics calculator.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = data_dir
        self.platform_weights = {
            'X': 0.8,        # High discoverability
            'Instagram': 0.9,  # High visual engagement
            'TikTok': 0.85,   # High growth potential
            'Reddit': 0.6,    # Niche communities
            'OnlyFans': 0.4,  # Lower discoverability
            'Fansly': 0.4,    # Lower discoverability
            'ManyVids': 0.3,  # Niche marketplace
            'YouTube': 0.7,   # Broad reach
            'Twitch': 0.5     # Live streaming focus
        }
        
    def load_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all required data files.
        
        Returns:
            Dictionary containing DataFrames for each data type
        """
        data = {}
        
        try:
            # Load creators data
            data['creators'] = pd.read_csv(f"{self.data_dir}/exports/creators.csv")
            logger.info(f"Loaded {len(data['creators'])} creators")
            
            # Load platforms data
            data['platforms'] = pd.read_csv(f"{self.data_dir}/exports/platforms.csv")
            logger.info(f"Loaded {len(data['platforms'])} platform records")
            
            # Load metrics data
            data['metrics'] = pd.read_csv(f"{self.data_dir}/exports/metrics.csv")
            logger.info(f"Loaded {len(data['metrics'])} metric records")
            
            # Load business data
            data['business'] = pd.read_csv(f"{self.data_dir}/exports/business.csv")
            logger.info(f"Loaded {len(data['business'])} business records")
            
        except FileNotFoundError as e:
            logger.error(f"Data file not found: {e}")
            raise
        except pd.errors.EmptyDataError:
            logger.warning("Some data files are empty")
            # Create empty DataFrames with expected columns
            data = {
                'creators': pd.DataFrame(columns=['creator_id', 'state', 'city_region', 'verification_confidence', 'primary_platform', 'content_types']),
                'platforms': pd.DataFrame(columns=['creator_id', 'platform', 'followers_count']),
                'metrics': pd.DataFrame(columns=['creator_id', 'platform', 'snapshot_date', 'followers', 'avg_likes_post', 'avg_comments_post']),
                'business': pd.DataFrame(columns=['creator_id', 'business_entity', 'booking_email', 'agency_affiliation'])
            }
        
        return data
    
    def calculate_engagement_rate(self, likes: float, comments: float, followers: int) -> Optional[float]:
        """
        Calculate engagement rate per post.
        
        Formula: ER_post = (avg_likes_post + avg_comments_post) / followers
        
        Args:
            likes: Average likes per post
            comments: Average comments per post
            followers: Total followers
            
        Returns:
            Engagement rate as decimal (0.05 = 5%) or None if invalid
        """
        if followers <= 0:
            return None
        
        if pd.isna(likes) or pd.isna(comments):
            return None
        
        engagement = (likes + comments) / followers
        return min(engagement, 1.0)  # Cap at 100%
    
    def calculate_growth_rate(self, current_followers: int, previous_followers: int) -> Optional[float]:
        """
        Calculate growth rate between two time periods.
        
        Formula: Growth = (followers_current - followers_previous) / followers_previous
        
        Args:
            current_followers: Current follower count
            previous_followers: Previous follower count
            
        Returns:
            Growth rate as decimal or None if invalid
        """
        if previous_followers <= 0:
            return None
        
        if pd.isna(current_followers) or pd.isna(previous_followers):
            return None
        
        growth = (current_followers - previous_followers) / previous_followers
        return growth
    
    def calculate_footprint_score(self, creator_platforms: pd.DataFrame) -> float:
        """
        Calculate cross-platform footprint score.
        
        Formula: Footprint = \u03a3(log(1 + followers_p) * w_p)
        
        Args:
            creator_platforms: DataFrame with creator's platform data
            
        Returns:
            Footprint score as float
        """
        footprint = 0.0
        
        for _, platform in creator_platforms.iterrows():
            followers = platform.get('followers_count', 0)
            platform_name = platform.get('platform', 'Unknown')
            weight = self.platform_weights.get(platform_name, 0.5)
            
            if followers > 0:
                footprint += math.log(1 + followers) * weight
        
        return footprint
    
    def calculate_integration_score(self, creator_platforms: pd.DataFrame) -> float:
        """
        Calculate cross-link integration score.
        
        Formula: Integration = links_to_other_platforms / total_platforms_present
        
        Args:
            creator_platforms: DataFrame with creator's platform data
            
        Returns:
            Integration score between 0 and 1
        """
        total_platforms = len(creator_platforms)
        if total_platforms <= 1:
            return 0.0
        
        # Count platforms with linked hubs
        linked_platforms = creator_platforms['linked_hub'].notna().sum()
        linked_platforms += creator_platforms['linked_hub'].ne('').sum()
        linked_platforms += creator_platforms['linked_hub'].ne('None').sum()
        
        # Count URLs that mention other platforms
        cross_links = 0
        for _, platform in creator_platforms.iterrows():
            url = str(platform.get('url', '')).lower()
            handle = str(platform.get('handle', '')).lower()
            
            # Check if URL or handle references other platforms
            other_platforms = creator_platforms[creator_platforms['platform'] != platform['platform']]
            for _, other in other_platforms.iterrows():
                other_handle = str(other.get('handle', '')).lower()
                if other_handle in url or other_handle in handle:
                    cross_links += 1
        
        total_links = linked_platforms + cross_links
        return min(total_links / total_platforms, 1.0)
    
    def calculate_business_presence_index(self, business_data: Dict) -> float:
        """
        Calculate Business Presence Index (BPI).
        
        Formula: BPI = \u03a3(1 for each business indicator)
        
        Args:
            business_data: Dictionary with business information
            
        Returns:
            BPI score between 0 and 5
        """
        bpi = 0
        
        # Check for registered business entity
        if business_data.get('business_entity') and business_data['business_entity'] not in ['Unknown', 'NotApplicable', '']:
            bpi += 1
        
        # Check for booking email
        if business_data.get('booking_email') and '@' in business_data['booking_email']:
            bpi += 1
        
        # Check for agency affiliation
        if business_data.get('agency_affiliation') and business_data['agency_affiliation'].strip():
            bpi += 1
        
        # Check for shopfronts
        if business_data.get('shopfronts') and business_data['shopfronts'].strip():
            bpi += 1
        
        # Check for visible pricing
        if business_data.get('pricing_visible') and business_data['pricing_visible'] in ['Yes', 'Partial']:
            bpi += 1
        
        return bpi
    
    def calculate_creator_tier(self, footprint_score: float, avg_engagement: float, bpi: float) -> str:
        """
        Estimate creator tier based on metrics.
        
        Args:
            footprint_score: Cross-platform footprint score
            avg_engagement: Average engagement rate
            bpi: Business Presence Index
            
        Returns:
            Creator tier: Micro, Mid, Macro, Top, or Undetermined
        """
        # Calculate composite score
        composite_score = (
            footprint_score * 0.4 +
            avg_engagement * 100 * 0.3 +  # Scale engagement to comparable range
            bpi * 20 * 0.3  # Scale BPI to comparable range
        )
        
        if composite_score >= 150:
            return "Top"
        elif composite_score >= 80:
            return "Macro"
        elif composite_score >= 30:
            return "Mid"
        elif composite_score >= 5:
            return "Micro"
        else:
            return "Undetermined"
    
    def process_creator_metrics(self, creator_id: str, data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Process all metrics for a single creator.
        
        Args:
            creator_id: Creator identifier
            data: Dictionary containing all data DataFrames
            
        Returns:
            Dictionary with calculated metrics
        """
        metrics = {}
        
        # Get creator platforms
        creator_platforms = data['platforms'][data['platforms']['creator_id'] == creator_id]
        
        # Get creator metrics
        creator_metrics = data['metrics'][data['metrics']['creator_id'] == creator_id]
        
        # Get creator business data
        creator_business = data['business'][data['business']['creator_id'] == creator_id]
        business_data = creator_business.iloc[0].to_dict() if not creator_business.empty else {}
        
        # Calculate engagement rates
        engagement_rates = []
        for _, metric in creator_metrics.iterrows():
            er = self.calculate_engagement_rate(
                metric.get('avg_likes_post', 0),
                metric.get('avg_comments_post', 0),
                metric.get('followers', 0)
            )
            if er is not None:
                engagement_rates.append(er)
        
        metrics['avg_engagement_rate'] = np.mean(engagement_rates) if engagement_rates else 0.0
        metrics['engagement_rates_by_platform'] = {}
        
        for platform_name in creator_metrics['platform'].unique():
            platform_metrics = creator_metrics[creator_metrics['platform'] == platform_name]
            platform_engagement = []
            
            for _, metric in platform_metrics.iterrows():
                er = self.calculate_engagement_rate(
                    metric.get('avg_likes_post', 0),
                    metric.get('avg_comments_post', 0),
                    metric.get('followers', 0)
                )
                if er is not None:
                    platform_engagement.append(er)
            
            if platform_engagement:
                metrics['engagement_rates_by_platform'][platform_name] = np.mean(platform_engagement)
        
        # Calculate footprint score
        metrics['footprint_score'] = self.calculate_footprint_score(creator_platforms)
        
        # Calculate integration score
        metrics['integration_score'] = self.calculate_integration_score(creator_platforms)
        
        # Calculate BPI
        metrics['business_presence_index'] = self.calculate_business_presence_index(business_data)
        
        # Estimate creator tier
        metrics['estimated_tier'] = self.calculate_creator_tier(
            metrics['footprint_score'],
            metrics['avg_engagement_rate'],
            metrics['business_presence_index']
        )
        
        # Calculate growth rates
        growth_rates = {}
        for platform_name in creator_metrics['platform'].unique():
            platform_metrics = creator_metrics[creator_metrics['platform'] == platform_name].sort_values('snapshot_date')
            
            if len(platform_metrics) >= 2:
                latest = platform_metrics.iloc[-1]
                previous = platform_metrics.iloc[-2]
                
                growth = self.calculate_growth_rate(
                    latest.get('followers', 0),
                    previous.get('followers', 0)
                )
                
                if growth is not None:
                    growth_rates[platform_name] = growth
        
        metrics['growth_rates_by_platform'] = growth_rates
        metrics['avg_growth_rate'] = np.mean(list(growth_rates.values())) if growth_rates else 0.0
        
        # Platform distribution
        metrics['platform_count'] = len(creator_platforms)
        metrics['platforms'] = creator_platforms['platform'].tolist()
        
        # Total followers across platforms
        total_followers = creator_platforms['followers_count'].fillna(0).sum()
        metrics['total_followers'] = int(total_followers)
        
        return metrics
    
    def generate_regional_metrics(self, data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Generate aggregate metrics by state and region.
        
        Args:
            data: Dictionary containing all data DataFrames
            
        Returns:
            Dictionary with regional metrics
        """
        regional_metrics = {}
        
        # Merge creators with their metrics
        creator_metrics_list = []
        for creator_id in data['creators']['creator_id'].unique():
            try:
                metrics = self.process_creator_metrics(creator_id, data)
                creator_info = data['creators'][data['creators']['creator_id'] == creator_id].iloc[0]
                
                creator_metrics = {
                    'creator_id': creator_id,
                    'state': creator_info.get('state'),
                    'city_region': creator_info.get('city_region'),
                    'verification_confidence': creator_info.get('verification_confidence'),
                    **metrics
                }
                creator_metrics_list.append(creator_metrics)
            except Exception as e:
                logger.warning(f"Error processing creator {creator_id}: {e}")
                continue
        
        creator_metrics_df = pd.DataFrame(creator_metrics_list)
        
        if creator_metrics_df.empty:
            return {}
        
        # Calculate metrics by state
        for state in ['NE', 'IA']:
            state_data = creator_metrics_df[creator_metrics_df['state'] == state]
            
            if state_data.empty:
                continue
            
            regional_metrics[state] = {
                'creator_count': len(state_data),
                'avg_footprint_score': state_data['footprint_score'].mean(),
                'avg_engagement_rate': state_data['avg_engagement_rate'].mean(),
                'avg_growth_rate': state_data['avg_growth_rate'].mean(),
                'avg_bpi': state_data['business_presence_index'].mean(),
                'total_followers': state_data['total_followers'].sum(),
                'tier_distribution': state_data['estimated_tier'].value_counts().to_dict(),
                'platform_distribution': state_data['platforms'].explode().value_counts().head(10).to_dict()
            }
            
            # Metrics by city region
            for region in state_data['city_region'].unique():
                if pd.isna(region):
                    continue
                    
                region_data = state_data[state_data['city_region'] == region]
                regional_metrics[state]['regions'] = regional_metrics[state].get('regions', {})
                regional_metrics[state]['regions'][region] = {
                    'creator_count': len(region_data),
                    'avg_footprint_score': region_data['footprint_score'].mean(),
                    'avg_engagement_rate': region_data['avg_engagement_rate'].mean(),
                    'total_followers': region_data['total_followers'].sum()
                }
        
        return regional_metrics
    
    def save_calculated_metrics(self, metrics: Dict, output_file: str = "../data/exports/calculated_metrics.csv"):
        """
        Save calculated metrics to CSV file.
        
        Args:
            metrics: Dictionary with calculated metrics
            output_file: Output file path
        """
        # Convert to DataFrame
        metrics_list = []
        
        for creator_id, creator_metrics in metrics.items():
            if 'creators' not in creator_id:
                continue
                
            row = {
                'creator_id': creator_id,
                'footprint_score': creator_metrics.get('footprint_score', 0),
                'integration_score': creator_metrics.get('integration_score', 0),
                'business_presence_index': creator_metrics.get('business_presence_index', 0),
                'avg_engagement_rate': creator_metrics.get('avg_engagement_rate', 0),
                'avg_growth_rate': creator_metrics.get('avg_growth_rate', 0),
                'estimated_tier': creator_metrics.get('estimated_tier', 'Undetermined'),
                'platform_count': creator_metrics.get('platform_count', 0),
                'total_followers': creator_metrics.get('total_followers', 0)
            }
            
            # Add platform-specific engagement rates
            for platform, rate in creator_metrics.get('engagement_rates_by_platform', {}).items():
                row[f'engagement_rate_{platform.lower()}'] = rate
            
            # Add platform-specific growth rates
            for platform, rate in creator_metrics.get('growth_rates_by_platform', {}).items():
                row[f'growth_rate_{platform.lower()}'] = rate
            
            metrics_list.append(row)
        
        if metrics_list:
            metrics_df = pd.DataFrame(metrics_list)
            metrics_df.to_csv(output_file, index=False)
            logger.info(f"Saved {len(metrics_df)} calculated metrics to {output_file}")
        else:
            logger.warning("No metrics to save")


def main():
    """
    Main function to run metrics calculation.
    """
    calculator = MetricsCalculator()
    
    try:
        # Load data
        data = calculator.load_data()
        
        # Process all creators
        all_creator_metrics = {}
        for creator_id in data['creators']['creator_id'].unique():
            try:
                creator_metrics = calculator.process_creator_metrics(creator_id, data)
                all_creator_metrics[creator_id] = creator_metrics
            except Exception as e:
                logger.error(f"Error processing creator {creator_id}: {e}")
                continue
        
        # Generate regional metrics
        regional_metrics = calculator.generate_regional_metrics(data)
        
        # Save results
        calculator.save_calculated_metrics(all_creator_metrics)
        
        # Save regional metrics
        regional_df = pd.DataFrame([
            {
                'state': state,
                'creator_count': metrics['creator_count'],
                'avg_footprint_score': metrics['avg_footprint_score'],
                'avg_engagement_rate': metrics['avg_engagement_rate'],
                'avg_growth_rate': metrics['avg_growth_rate'],
                'avg_bpi': metrics['avg_bpi'],
                'total_followers': metrics['total_followers']
            }
            for state, metrics in regional_metrics.items()
        ])
        
        regional_df.to_csv("../data/exports/regional_metrics.csv", index=False)
        logger.info(f"Saved regional metrics for {len(regional_df)} states")
        
        logger.info("Metrics calculation completed successfully")
        
    except Exception as e:
        logger.error(f"Error in metrics calculation: {e}")
        raise


if __name__ == "__main__":
    main()
