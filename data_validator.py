
#!/usr/bin/env python3
"""
Data Validator for Creator Economy Research

This script validates data quality, consistency, and compliance
with the research methodology and privacy requirements.
"""

import pandas as pd
import re
import hashlib
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataValidator:
    """
    Validates data quality and compliance for creator research.
    """
    
    def __init__(self, data_dir: str = "../data"):
        """
        Initialize the data validator.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = data_dir
        self.validation_errors = []
        self.validation_warnings = []
        
        # Privacy patterns to detect
        self.pii_patterns = {
            'phone': r'\b\d{3}-\d{3}-\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'address': r'\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)'
        }
        
        # Valid values for categorical fields
        self.valid_states = ['NE', 'IA', 'Undetermined']
        self.valid_confidence_levels = ['High', 'Medium', 'Low', 'Undetermined']
        self.valid_platforms = ['X', 'Instagram', 'TikTok', 'Reddit', 'OnlyFans', 'Fansly', 'ManyVids', 'YouTube', 'Twitch', 'Other']
        
    def load_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all data files for validation.
        
        Returns:
            Dictionary containing DataFrames for each data type
        """
        data = {}
        
        try:
            data['creators'] = pd.read_csv(f"{self.data_dir}/exports/creators.csv")
            data['platforms'] = pd.read_csv(f"{self.data_dir}/exports/platforms.csv")
            data['metrics'] = pd.read_csv(f"{self.data_dir}/exports/metrics.csv")
            data['business'] = pd.read_csv(f"{self.data_dir}/exports/business.csv")
            data['evidence'] = pd.read_csv(f"{self.data_dir}/exports/evidence.csv")
            
        except FileNotFoundError as e:
            logger.error(f"Data file not found: {e}")
            raise
        except pd.errors.EmptyDataError as e:
            logger.error(f"Empty data file: {e}")
            raise
            
        return data
    
    def validate_creator_ids(self, creators_df: pd.DataFrame) -> List[str]:
        """
        Validate creator ID format and uniqueness.
        
        Args:
            creators_df: Creators DataFrame
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check for missing creator IDs
        missing_ids = creators_df['creator_id'].isna().sum()
        if missing_ids > 0:
            errors.append(f"Missing creator IDs: {missing_ids} records")
        
        # Check for duplicate creator IDs
        duplicate_ids = creators_df['creator_id'].duplicated().sum()
        if duplicate_ids > 0:
            errors.append(f"Duplicate creator IDs: {duplicate_ids} records")
        
        # Check ID format (should be 64-character hex)
        invalid_format = creators_df[~creators_df['creator_id'].str.match(r'^[a-f0-9]{64}$', na=False)]
        if not invalid_format.empty:
            errors.append(f"Invalid creator ID format: {len(invalid_format)} records")
        
        return errors
    
    def validate_categorical_fields(self, creators_df: pd.DataFrame) -> List[str]:
        """
        Validate categorical field values.
        
        Args:
            creators_df: Creators DataFrame
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate states
        invalid_states = creators_df[~creators_df['state'].isin(self.valid_states)]
        if not invalid_states.empty:
            errors.append(f"Invalid state values: {len(invalid_states)} records")
        
        # Validate confidence levels
        invalid_confidence = creators_df[~creators_df['verification_level'].isin(self.valid_confidence_levels)]
        if not invalid_confidence.empty:
            errors.append(f"Invalid confidence levels: {len(invalid_confidence)} records")
        
        # Validate confidence score range
        invalid_scores = creators_df[
            (creators_df['verification_confidence'] < 0) | 
            (creators_df['verification_confidence'] > 1)
        ]
        if not invalid_scores.empty:
            errors.append(f"Confidence scores out of range: {len(invalid_scores)} records")
        
        return errors
    
    def detect_pii_violations(self, data: Dict[str, pd.DataFrame]) -> List[str]:
        """
        Detect potential PII violations in data.
        
        Args:
            data: Dictionary containing all data DataFrames
            
        Returns:
            List of PII violation warnings
        """
        violations = []
        
        for table_name, df in data.items():
            if df.empty:
                continue
                
            # Check text columns for PII patterns
            text_columns = df.select_dtypes(include=['object']).columns
            
            for col in text_columns:
                if col == 'creator_id':  # Skip creator IDs
                    continue
                    
                # Check each PII pattern
                for pii_type, pattern in self.pii_patterns.items():
                    matches = df[col].str.contains(pattern, regex=True, na=False)
                    if matches.any():
                        violations.append(
                            f"Potential {pii_type} PII in {table_name}.{col}: {matches.sum()} records"
                        )
        
        return violations
    
    def validate_data_consistency(self, data: Dict[str, pd.DataFrame]) -> List[str]:
        """
        Validate data consistency across tables.
        
        Args:
            data: Dictionary containing all data DataFrames
            
        Returns:
            List of consistency errors
        """
        errors = []
        
        # Check foreign key consistency
        creator_ids = set(data['creators']['creator_id'])
        
        # Platforms table consistency
        orphan_platforms = data['platforms'][~data['platforms']['creator_id'].isin(creator_ids)]
        if not orphan_platforms.empty:
            errors.append(f"Orphan platform records: {len(orphan_platforms)} records")
        
        # Metrics table consistency
        orphan_metrics = data['metrics'][~data['metrics']['creator_id'].isin(creator_ids)]
        if not orphan_metrics.empty:
            errors.append(f"Orphan metric records: {len(orphan_metrics)} records")
        
        # Business table consistency
        orphan_business = data['business'][~data['business']['creator_id'].isin(creator_ids)]
        if not orphan_business.empty:
            errors.append(f"Orphan business records: {len(orphan_business)} records")
        
        # Evidence table consistency
        orphan_evidence = data['evidence'][~data['evidence']['creator_id'].isin(creator_ids)]
        if not orphan_evidence.empty:
            errors.append(f"Orphan evidence records: {len(orphan_evidence)} records")
        
        # Check platform validity
        invalid_platforms = data['platforms'][~data['platforms']['platform'].isin(self.valid_platforms)]
        if not invalid_platforms.empty:
            errors.append(f"Invalid platform names: {len(invalid_platforms)} records")
        
        return errors
    
    def validate_date_consistency(self, data: Dict[str, pd.DataFrame]) -> List[str]:
        """
        Validate date fields for consistency and reasonable ranges.
        
        Args:
            data: Dictionary containing all data DataFrames
            
        Returns:
            List of date validation errors
        """
        errors = []
        
        # Validate creator dates
        creators_df = data['creators']
        
        # Check if first_seen is before last_active
        invalid_date_order = creators_df[
            pd.to_datetime(creators_df['first_seen']) > pd.to_datetime(creators_df['last_active'])
        ]
        if not invalid_date_order.empty:
            errors.append(f"Invalid date order (first_seen > last_active): {len(invalid_date_order)} records")
        
        # Check for future dates
        today = datetime.now()
        future_first_seen = creators_df[pd.to_datetime(creators_df['first_seen']) > today]
        if not future_first_seen.empty:
            errors.append(f"Future first_seen dates: {len(future_first_seen)} records")
        
        future_last_active = creators_df[pd.to_datetime(creators_df['last_active']) > today]
        if not future_last_active.empty:
            errors.append(f"Future last_active dates: {len(future_last_active)} records")
        
        # Validate metrics dates
        metrics_df = data['metrics']
        future_metrics = metrics_df[pd.to_datetime(metrics_df['snapshot_date']) > today]
        if not future_metrics.empty:
            errors.append(f"Future snapshot dates: {len(future_metrics)} records")
        
        return errors
    
    def validate_metrics_ranges(self, metrics_df: pd.DataFrame) -> List[str]:
        """
        Validate metrics for reasonable value ranges.
        
        Args:
            metrics_df: Metrics DataFrame
            
        Returns:
            List of metric validation errors
        """
        errors = []
        
        # Check for negative values in counts
        count_columns = ['followers', 'following', 'posts_count', 'subscriber_count']
        
        for col in count_columns:
            if col in metrics_df.columns:
                negative_values = metrics_df[metrics_df[col] < 0]
                if not negative_values.empty:
                    errors.append(f"Negative values in {col}: {len(negative_values)} records")
        
        # Check for extremely high engagement rates (>100%)
        if 'engagement_rate' in metrics_df.columns:
            high_engagement = metrics_df[metrics_df['engagement_rate'] > 1.0]
            if not high_engagement.empty:
                errors.append(f"Engagement rates > 100%: {len(high_engagement)} records")
        
        # Check for zero followers with positive engagement
        zero_followers = metrics_df[
            (metrics_df['followers'] == 0) & 
            (metrics_df['engagement_rate'] > 0)
        ]
        if not zero_followers.empty:
            errors.append(f"Engagement with zero followers: {len(zero_followers)} records")
        
        return errors
    
    def validate_evidence_weights(self, evidence_df: pd.DataFrame) -> List[str]:
        """
        Validate evidence weight ranges and values.
        
        Args:
            evidence_df: Evidence DataFrame
            
        Returns:
            List of evidence validation errors
        """
        errors = []
        
        # Check weight range
        invalid_weights = evidence_df[
            (evidence_df['weight'] < 0) | 
            (evidence_df['weight'] > 1)
        ]
        if not invalid_weights.empty:
            errors.append(f"Evidence weights out of range: {len(invalid_weights)} records")
        
        # Check confidence impact range
        invalid_impact = evidence_df[
            (evidence_df['confidence_impact'] < -1) | 
            (evidence_df['confidence_impact'] > 1)
        ]
        if not invalid_impact.empty:
            errors.append(f"Confidence impact out of range: {len(invalid_impact)} records")
        
        return errors
    
    def generate_quality_report(self, data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Generate comprehensive data quality report.
        
        Args:
            data: Dictionary containing all data DataFrames
            
        Returns:
            Dictionary containing quality metrics and issues
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {},
            'tables': {},
            'errors': [],
            'warnings': []
        }
        
        # Table summaries
        for table_name, df in data.items():
            report['tables'][table_name] = {
                'record_count': len(df),
                'column_count': len(df.columns),
                'null_counts': df.isnull().sum().to_dict(),
                'duplicate_rows': df.duplicated().sum()
            }
        
        # Overall summary
        total_records = sum(len(df) for df in data.values())
        report['summary'] = {
            'total_records': total_records,
            'total_tables': len(data),
            'total_errors': len(self.validation_errors),
            'total_warnings': len(self.validation_warnings)
        }
        
        # Add errors and warnings
        report['errors'] = self.validation_errors
        report['warnings'] = self.validation_warnings
        
        return report
    
    def run_validation(self) -> Dict:
        """
        Run complete data validation.
        
        Returns:
            Validation report dictionary
        """
        try:
            # Load data
            data = self.load_data()
            logger.info("Data loaded for validation")
            
            # Run validations
            self.validation_errors.extend(self.validate_creator_ids(data['creators']))
            self.validation_errors.extend(self.validate_categorical_fields(data['creators']))
            self.validation_errors.extend(self.validate_data_consistency(data))
            self.validation_errors.extend(self.validate_date_consistency(data))
            self.validation_errors.extend(self.validate_metrics_ranges(data['metrics']))
            self.validation_errors.extend(self.validate_evidence_weights(data['evidence']))
            
            # PII violations as warnings
            pii_violations = self.detect_pii_violations(data)
            self.validation_warnings.extend(pii_violations)
            
            # Generate report
            report = self.generate_quality_report(data)
            
            logger.info(f"Validation completed: {len(self.validation_errors)} errors, {len(self.validation_warnings)} warnings")
            
            return report
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise


def main():
    """
    Main function to run data validation.
    """
    validator = DataValidator()
    
    try:
        report = validator.run_validation()
        
        # Save report
        import json
        with open("../data/exports/validation_report.json", 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info("Validation report saved")
        
        # Print summary
        print(f"\
Data Validation Summary:")
        print(f"Total Records: {report['summary']['total_records']}")
        print(f"Total Tables: {report['summary']['total_tables']}")
        print(f"Errors: {report['summary']['total_errors']}")
        print(f"Warnings: {report['summary']['total_warnings']}")
        
        if report['errors']:
            print(f"\
Errors:")
            for error in report['errors'][:10]:  # Show first 10
                print(f"  - {error}")
        
        if report['warnings']:
            print(f"\
Warnings:")
            for warning in report['warnings'][:10]:  # Show first 10
                print(f"  - {warning}")
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise


if __name__ == "__main__":
    main()
