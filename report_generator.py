
#!/usr/bin/env python3
"""
Report Generator for Creator Economy Research

This script generates comprehensive reports and dashboards
from the collected and analyzed creator data.
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Generates reports and dashboards for creator economy research.
    """
    
    def __init__(self, data_dir: str = "../data", output_dir: str = "../reports"):
        """
        Initialize the report generator.
        
        Args:
            data_dir: Directory containing data files
            output_dir: Directory for output reports
        """
        self.data_dir = data_dir
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Platform colors for visualizations
        self.platform_colors = {
            'X': '#1DA1F2',
            'Instagram': '#E4405F',
            'TikTok': '#000000',
            'Reddit': '#FF4500',
            'OnlyFans': '#00AFF0',
            'Fansly': '#FF6B6B',
            'ManyVids': '#800080',
            'YouTube': '#FF0000',
            'Twitch': '#9146FF'
        }
        
        # State colors
        self.state_colors = {
            'NE': '#D73F09',  # Nebraska Cornhuskers
            'IA': '#FCD116'   # Iowa Hawkeyes
        }
    
    def load_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all required data files.
        
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
            
            # Load calculated metrics if available
            try:
                data['calculated_metrics'] = pd.read_csv(f"{self.data_dir}/exports/calculated_metrics.csv")
                data['regional_metrics'] = pd.read_csv(f"{self.data_dir}/exports/regional_metrics.csv")
            except FileNotFoundError:
                logger.warning("Calculated metrics not found, some features may be limited")
                data['calculated_metrics'] = pd.DataFrame()
                data['regional_metrics'] = pd.DataFrame()
            
        except FileNotFoundError as e:
            logger.error(f"Data file not found: {e}")
            raise
            
        return data
    
    def generate_state_summary(self, state: str, data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Generate summary statistics for a specific state.
        
        Args:
            state: State abbreviation (NE or IA)
            data: Dictionary containing data DataFrames
            
        Returns:
            Dictionary with state summary statistics
        """
        creators_df = data['creators'][data['creators']['state'] == state]
        
        if creators_df.empty:
            return {'error': f'No data found for state {state}'}
        
        # Get platforms for state creators
        state_creator_ids = creators_df['creator_id'].tolist()
        platforms_df = data['platforms'][data['platforms']['creator_id'].isin(state_creator_ids)]
        metrics_df = data['metrics'][data['metrics']['creator_id'].isin(state_creator_ids)]
        business_df = data['business'][data['business']['creator_id'].isin(state_creator_ids)]
        
        # Basic statistics
        summary = {
            'state': state,
            'total_creators': len(creators_df),
            'avg_confidence': creators_df['verification_confidence'].mean(),
            'confidence_distribution': creators_df['verification_level'].value_counts().to_dict(),
            'city_regions': creators_df['city_region'].value_counts().to_dict(),
            'platform_distribution': platforms_df['platform'].value_counts().to_dict(),
            'business_entities': business_df['business_entity'].value_counts().to_dict() if not business_df.empty else {},
            'agency_affiliations': business_df['has_agency_affiliation'].value_counts().to_dict() if not business_df.empty else {}
        }
        
        # Calculate metrics if available
        if not metrics_df.empty:
            latest_metrics = metrics_df.loc[metrics_df.groupby(['creator_id', 'platform'])['snapshot_date'].idxmax()]
            
            summary.update({
                'total_followers': latest_metrics['followers'].fillna(0).sum(),
                'avg_engagement_rate': latest_metrics['engagement_rate'].mean(),
                'avg_growth_rate': latest_metrics['growth_rate_30d'].mean() if 'growth_rate_30d' in latest_metrics.columns else 0,
                'total_posts': latest_metrics['posts_count'].fillna(0).sum()
            })
        
        # Calculate calculated metrics if available
        if not data['calculated_metrics'].empty:
            state_calculated = data['calculated_metrics'][data['calculated_metrics']['creator_id'].isin(state_creator_ids)]
            
            if not state_calculated.empty:
                summary.update({
                    'avg_footprint_score': state_calculated['footprint_score'].mean(),
                    'avg_business_presence_index': state_calculated['business_presence_index'].mean(),
                    'tier_distribution': state_calculated['estimated_tier'].value_counts().to_dict()
                })
        
        return summary
    
    def generate_time_series_data(self, state: str, data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Generate time series data for trends analysis.
        
        Args:
            state: State abbreviation
            data: Dictionary containing data DataFrames
            
        Returns:
            Dictionary with time series data
        """
        creators_df = data['creators'][data['creators']['state'] == state]
        state_creator_ids = creators_df['creator_id'].tolist()
        metrics_df = data['metrics'][data['metrics']['creator_id'].isin(state_creator_ids)]
        
        if metrics_df.empty:
            return {}
        
        # Group by date and calculate daily aggregates
        daily_metrics = metrics_df.groupby('snapshot_date').agg({
            'followers': 'sum',
            'posts_count': 'sum',
            'engagement_rate': 'mean'
        }).reset_index()
        
        # Add cumulative creator count
        creator_dates = creators_df.groupby('first_seen').size().cumsum().reset_index()
        creator_dates.columns = ['date', 'cumulative_creators']
        
        return {
            'daily_metrics': daily_metrics.to_dict('records'),
            'creator_growth': creator_dates.to_dict('records')
        }
    
    def create_dashboard_data(self, state: str, data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Create data structure for HTML dashboard template.
        
        Args:
            state: State abbreviation
            data: Dictionary containing data DataFrames
            
        Returns:
            Dictionary with dashboard data
        """
        summary = self.generate_state_summary(state, data)
        time_series = self.generate_time_series_data(state, data)
        
        # Prepare chart data
        dashboard_data = {
            'state': state,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_creators': summary.get('total_creators', 0),
            'avg_confidence': f"{summary.get('avg_confidence', 0):.1%}",
            'total_followers': f"{summary.get('total_followers', 0):,}",
            'avg_engagement': f"{summary.get('avg_engagement_rate', 0):.2%}",
            'creator_growth': '+5.2%',  # Placeholder - would calculate from historical data
            'confidence_trend': '+2.1%',  # Placeholder
            'follower_growth': '+8.7%',  # Placeholder
            'engagement_trend': 'positive',  # Would calculate from trend analysis
            'engagement_change': '+3.4%',  # Placeholder
            'regions': summary.get('city_regions', {}),
            'platform_distribution': summary.get('platform_distribution', {}),
            'platform_colors': self.platform_colors,
            'confidence_distribution': {
                'labels': list(summary.get('confidence_distribution', {}).keys()),
                'data': list(summary.get('confidence_distribution', {}).values())
            },
            'platform_chart': {
                'labels': list(summary.get('platform_distribution', {}).keys()),
                'data': list(summary.get('platform_distribution', {}).values())
            },
            'growth_chart': {
                'labels': [d['snapshot_date'] for d in time_series.get('daily_metrics', [])[-30:]],
                'creators': [len(state_creators) for d in time_series.get('creator_growth', [])[-30:]],  # Placeholder
                'followers': [d['followers'] for d in time_series.get('daily_metrics', [])[-30:]]
            },
            'tier_chart': {
                'labels': list(summary.get('tier_distribution', {}).keys()),
                'data': list(summary.get('tier_distribution', {}).values())
            }
        }
        
        return dashboard_data
    
    def generate_html_dashboard(self, state: str, data: Dict[str, pd.DataFrame], template_path: str = None) -> str:
        """
        Generate HTML dashboard for a state.
        
        Args:
            state: State abbreviation
            data: Dictionary containing data DataFrames
            template_path: Path to HTML template
            
        Returns:
            Generated HTML content
        """
        if template_path is None:
            template_path = f"{self.data_dir}/../templates/state_dashboard_template.html"
        
        # Create dashboard data
        dashboard_data = self.create_dashboard_data(state, data)
        
        try:
            with open(template_path, 'r') as f:
                template = f.read()
            
            # Simple template replacement (in production, use Jinja2 or similar)
            html_content = template
            
            # Replace placeholders with actual data
            for key, value in dashboard_data.items():
                if isinstance(value, str):
                    html_content = html_content.replace('{{' + key + '}}', value)
                elif isinstance(value, dict):
                    # Handle simple dict replacements
                    if key == 'platform_colors':
                        continue  # Handled in JavaScript
                    elif key == 'confidence_distribution':
                        html_content = html_content.replace('{{' + key + '.labels|tojson}}', str(value.get('labels', [])))
                        html_content = html_content.replace('{{' + key + '.data|tojson}}', str(value.get('data', [])))
                    elif key == 'platform_chart':
                        html_content = html_content.replace('{{' + key + '.labels|tojson}}', str(value.get('labels', [])))
                        html_content = html_content.replace('{{' + key + '.data|tojson}}', str(value.get('data', [])))
                    elif key == 'growth_chart':
                        html_content = html_content.replace('{{' + key + '.labels|tojson}}', str(value.get('labels', [])))
                        html_content = html_content.replace('{{' + key + '.creators|tojson}}', str(value.get('creators', [])))
                        html_content = html_content.replace('{{' + key + '.followers|tojson}}', str(value.get('followers', [])))
                    elif key == 'tier_chart':
                        html_content = html_content.replace('{{' + key + '.labels|tojson}}', str(value.get('labels', [])))
                        html_content = html_content.replace('{{' + key + '.data|tojson}}', str(value.get('data', [])))
                elif isinstance(value, list):
                    html_content = html_content.replace('{{' + key + '}}', str(value))
            
            return html_content
            
        except FileNotFoundError:
            logger.error(f"Template not found: {template_path}")
            return self.generate_simple_dashboard(state, dashboard_data)
    
    def generate_simple_dashboard(self, state: str, data: Dict) -> str:
        """
        Generate a simple HTML dashboard when template is not available.
        
        Args:
            state: State abbreviation
            data: Dashboard data dictionary
            
        Returns:
            Simple HTML dashboard
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Creator Economy Dashboard - {state}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
                .stat {{ background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .stat-value {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
                .stat-label {{ color: #7f8c8d; }}
                .section {{ margin: 30px 0; }}
                .section h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Creator Economy Dashboard</h1>
                <h2>{state} - Regional Analysis</h2>
                <p>Last updated: {data.get('timestamp', 'N/A')}</p>
            </div>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{data.get('total_creators', 0)}</div>
                    <div class="stat-label">Total Creators</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{data.get('avg_confidence', '0%')}</div>
                    <div class="stat-label">Avg Confidence</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{data.get('total_followers', '0')}</div>
                    <div class="stat-label">Total Reach</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{data.get('avg_engagement', '0%')}</div>
                    <div class="stat-label">Avg Engagement</div>
                </div>
            </div>
            
            <div class="section">
                <h2>Platform Distribution</h2>
                <ul>
        """
        
        for platform, count in data.get('platform_distribution', {}).items():
            html += f"                    <li>{platform}: {count}</li>\
"
        
        html += """
                </ul>
            </div>
            
            <div class="section">
                <h2>Regional Distribution</h2>
                <ul>
        """
        
        for region, count in data.get('regions', {}).items():
            html += f"                    <li>{region}: {count}</li>\
"
        
        html += """
                </ul>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def generate_comparative_analysis(self, data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Generate comparative analysis between states.
        
        Args:
            data: Dictionary containing data DataFrames
            
        Returns:
            Dictionary with comparative metrics
        """
        ne_summary = self.generate_state_summary('NE', data)
        ia_summary = self.generate_state_summary('IA', data)
        
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'nebraska': ne_summary,
            'iowa': ia_summary,
            'comparison': {}
        }
        
        # Calculate comparative metrics
        metrics_to_compare = [
            'total_creators', 'avg_confidence', 'total_followers', 
            'avg_engagement_rate', 'total_posts'
        ]
        
        for metric in metrics_to_compare:
            ne_val = ne_summary.get(metric, 0)
            ia_val = ia_summary.get(metric, 0)
            
            comparison['comparison'][metric] = {
                'nebraska': ne_val,
                'iowa': ia_val,
                'difference': ne_val - ia_val,
                'percentage_diff': ((ne_val - ia_val) / ia_val * 100) if ia_val > 0 else 0
            }
        
        return comparison
    
    def export_to_json(self, data: Dict, filename: str) -> str:
        """
        Export data to JSON file.
        
        Args:
            data: Data to export
            filename: Output filename
            
        Returns:
            Path to exported file
        """
        output_path = self.output_dir / filename
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Data exported to {output_path}")
        return str(output_path)
    
    def generate_all_reports(self, states: List[str] = None) -> Dict[str, str]:
        """
        Generate all available reports.
        
        Args:
            states: List of states to generate reports for
            
        Returns:
            Dictionary mapping report types to file paths
        """
        if states is None:
            states = ['NE', 'IA']
        
        # Load data
        data = self.load_data()
        
        generated_files = {}
        
        # Generate state reports
        for state in states:
            try:
                # State summary
                summary = self.generate_state_summary(state, data)
                summary_file = self.export_to_json(summary, f'{state.lower()}_summary.json')
                generated_files[f'{state}_summary'] = summary_file
                
                # HTML dashboard
                dashboard_html = self.generate_html_dashboard(state, data)
                dashboard_file = self.output_dir / f'{state.lower()}_dashboard.html'
                with open(dashboard_file, 'w') as f:
                    f.write(dashboard_html)
                generated_files[f'{state}_dashboard'] = str(dashboard_file)
                
                logger.info(f"Generated {state} reports")
                
            except Exception as e:
                logger.error(f"Error generating {state} reports: {e}")
        
        # Generate comparative analysis
        try:
            comparison = self.generate_comparative_analysis(data)
            comparison_file = self.export_to_json(comparison, 'comparative_analysis.json')
            generated_files['comparative'] = comparison_file
            
            logger.info("Generated comparative analysis")
            
        except Exception as e:
            logger.error(f"Error generating comparative analysis: {e}")
        
        # Generate combined report
        try:
            combined_data = {
                'timestamp': datetime.now().isoformat(),
                'states': {},
                'comparative': comparison if 'comparison' in locals() else {}
            }
            
            for state in states:
                combined_data['states'][state] = self.generate_state_summary(state, data)
            
            combined_file = self.export_to_json(combined_data, 'combined_report.json')
            generated_files['combined'] = combined_file
            
            logger.info("Generated combined report")
            
        except Exception as e:
            logger.error(f"Error generating combined report: {e}")
        
        return generated_files


def main():
    """
    Main function to generate reports.
    """
    generator = ReportGenerator()
    
    try:
        generated_files = generator.generate_all_reports()
        
        print(f"\
Generated Reports:")
        for report_type, file_path in generated_files.items():
            print(f"  {report_type}: {file_path}")
        
        logger.info("Report generation completed successfully")
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise


if __name__ == "__main__":
    main()
