#!/usr/bin/env python3
"""
Advanced Analytics System
Tracks conversions, response times, lead sources, and performance metrics
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

class AdvancedAnalytics:
    def __init__(self, storage_path: str = "/tmp/advanced_analytics.json"):
        self.storage_path = Path(storage_path)
        self.data = {
            'conversions': [],
            'response_times': [],
            'lead_sources': defaultdict(int),
            'daily_stats': {},
            'hourly_activity': defaultdict(int)
        }
        self.load_data()

    def load_data(self):
        """Load analytics data"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.data['conversions'] = loaded.get('conversions', [])
                    self.data['response_times'] = loaded.get('response_times', [])
                    self.data['lead_sources'] = defaultdict(int, loaded.get('lead_sources', {}))
                    self.data['daily_stats'] = loaded.get('daily_stats', {})
                    self.data['hourly_activity'] = defaultdict(int, loaded.get('hourly_activity', {}))
        except Exception as e:
            print(f"[WARNING] Could not load analytics: {e}")

    def save_data(self):
        """Save analytics data"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            # Convert defaultdict to dict for JSON serialization
            save_data = {
                'conversions': self.data['conversions'],
                'response_times': self.data['response_times'],
                'lead_sources': dict(self.data['lead_sources']),
                'daily_stats': self.data['daily_stats'],
                'hourly_activity': dict(self.data['hourly_activity'])
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[WARNING] Could not save analytics: {e}")

    def track_message_received(self, contact_id: str, timestamp: datetime = None):
        """Track when a message is received"""
        if timestamp is None:
            timestamp = datetime.now()

        # Track hourly activity
        hour_key = timestamp.strftime('%H:00')
        self.data['hourly_activity'][hour_key] += 1

        # Track daily stats
        date_key = timestamp.strftime('%Y-%m-%d')
        if date_key not in self.data['daily_stats']:
            self.data['daily_stats'][date_key] = {
                'messages_received': 0,
                'responses_sent': 0,
                'new_leads': 0,
                'conversions': 0
            }
        self.data['daily_stats'][date_key]['messages_received'] += 1

        self.save_data()

    def track_response_sent(self, contact_id: str, response_time_seconds: float, timestamp: datetime = None):
        """Track response time"""
        if timestamp is None:
            timestamp = datetime.now()

        # Store response time
        self.data['response_times'].append({
            'contact_id': contact_id,
            'response_time': response_time_seconds,
            'timestamp': timestamp.isoformat()
        })

        # Keep only last 1000 response times
        if len(self.data['response_times']) > 1000:
            self.data['response_times'] = self.data['response_times'][-1000:]

        # Track daily stats
        date_key = timestamp.strftime('%Y-%m-%d')
        if date_key not in self.data['daily_stats']:
            self.data['daily_stats'][date_key] = {
                'messages_received': 0,
                'responses_sent': 0,
                'new_leads': 0,
                'conversions': 0
            }
        self.data['daily_stats'][date_key]['responses_sent'] += 1

        self.save_data()

    def track_new_lead(self, contact_id: str, source: str = 'whatsapp', timestamp: datetime = None):
        """Track new lead acquisition"""
        if timestamp is None:
            timestamp = datetime.now()

        # Track lead source
        self.data['lead_sources'][source] += 1

        # Track daily stats
        date_key = timestamp.strftime('%Y-%m-%d')
        if date_key not in self.data['daily_stats']:
            self.data['daily_stats'][date_key] = {
                'messages_received': 0,
                'responses_sent': 0,
                'new_leads': 0,
                'conversions': 0
            }
        self.data['daily_stats'][date_key]['new_leads'] += 1

        self.save_data()

    def track_conversion(self, contact_id: str, conversion_type: str, value: float = 0, timestamp: datetime = None):
        """
        Track conversion event

        Args:
            contact_id: Lead phone number
            conversion_type: Type of conversion (e.g., 'meeting_scheduled', 'project_started', 'payment_received')
            value: Monetary value of conversion
            timestamp: When conversion happened
        """
        if timestamp is None:
            timestamp = datetime.now()

        conversion = {
            'contact_id': contact_id,
            'type': conversion_type,
            'value': value,
            'timestamp': timestamp.isoformat()
        }
        self.data['conversions'].append(conversion)

        # Track daily stats
        date_key = timestamp.strftime('%Y-%m-%d')
        if date_key not in self.data['daily_stats']:
            self.data['daily_stats'][date_key] = {
                'messages_received': 0,
                'responses_sent': 0,
                'new_leads': 0,
                'conversions': 0
            }
        self.data['daily_stats'][date_key]['conversions'] += 1

        self.save_data()

    def get_response_time_stats(self, days: int = 7) -> Dict:
        """Get response time statistics for last N days"""
        cutoff = datetime.now() - timedelta(days=days)

        recent_times = [
            rt['response_time']
            for rt in self.data['response_times']
            if datetime.fromisoformat(rt['timestamp']) > cutoff
        ]

        if not recent_times:
            return {
                'average': 0,
                'median': 0,
                'min': 0,
                'max': 0,
                'count': 0
            }

        recent_times.sort()
        count = len(recent_times)

        return {
            'average': sum(recent_times) / count,
            'median': recent_times[count // 2],
            'min': recent_times[0],
            'max': recent_times[-1],
            'count': count
        }

    def get_conversion_rate(self, days: int = 30) -> Dict:
        """Calculate conversion rate for last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.strftime('%Y-%m-%d')

        total_leads = 0
        total_conversions = 0

        for date_str, stats in self.data['daily_stats'].items():
            if date_str >= cutoff_str:
                total_leads += stats['new_leads']
                total_conversions += stats['conversions']

        conversion_rate = (total_conversions / total_leads * 100) if total_leads > 0 else 0

        return {
            'total_leads': total_leads,
            'total_conversions': total_conversions,
            'conversion_rate': round(conversion_rate, 2),
            'period_days': days
        }

    def get_hourly_activity_pattern(self) -> Dict:
        """Get hourly activity pattern (which hours are busiest)"""
        # Sort by hour
        sorted_hours = sorted(self.data['hourly_activity'].items())

        return {
            'hourly_breakdown': dict(sorted_hours),
            'busiest_hour': max(self.data['hourly_activity'].items(), key=lambda x: x[1])[0] if self.data['hourly_activity'] else 'N/A',
            'quietest_hour': min(self.data['hourly_activity'].items(), key=lambda x: x[1])[0] if self.data['hourly_activity'] else 'N/A'
        }

    def get_lead_source_breakdown(self) -> Dict:
        """Get breakdown of lead sources"""
        total = sum(self.data['lead_sources'].values())

        breakdown = {}
        for source, count in self.data['lead_sources'].items():
            percentage = (count / total * 100) if total > 0 else 0
            breakdown[source] = {
                'count': count,
                'percentage': round(percentage, 2)
            }

        return {
            'total_leads': total,
            'sources': breakdown
        }

    def get_daily_trend(self, days: int = 7) -> List[Dict]:
        """Get daily trend for last N days"""
        trend = []

        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_key = date.strftime('%Y-%m-%d')

            stats = self.data['daily_stats'].get(date_key, {
                'messages_received': 0,
                'responses_sent': 0,
                'new_leads': 0,
                'conversions': 0
            })

            trend.append({
                'date': date_key,
                'messages_received': stats['messages_received'],
                'responses_sent': stats['responses_sent'],
                'new_leads': stats['new_leads'],
                'conversions': stats['conversions']
            })

        return list(reversed(trend))

    def get_revenue_stats(self, days: int = 30) -> Dict:
        """Get revenue statistics from conversions"""
        cutoff = datetime.now() - timedelta(days=days)

        total_revenue = 0
        conversion_count = 0

        for conversion in self.data['conversions']:
            conv_time = datetime.fromisoformat(conversion['timestamp'])
            if conv_time > cutoff:
                total_revenue += conversion.get('value', 0)
                conversion_count += 1

        avg_value = (total_revenue / conversion_count) if conversion_count > 0 else 0

        return {
            'total_revenue': total_revenue,
            'conversion_count': conversion_count,
            'average_value': round(avg_value, 2),
            'period_days': days
        }

    def get_comprehensive_report(self) -> Dict:
        """Get comprehensive analytics report"""
        return {
            'response_times': self.get_response_time_stats(7),
            'conversion_rate': self.get_conversion_rate(30),
            'hourly_activity': self.get_hourly_activity_pattern(),
            'lead_sources': self.get_lead_source_breakdown(),
            'daily_trend': self.get_daily_trend(7),
            'revenue': self.get_revenue_stats(30)
        }


if __name__ == "__main__":
    # Test advanced analytics
    print("="*70)
    print("TESTING ADVANCED ANALYTICS")
    print("="*70)

    analytics = AdvancedAnalytics("/tmp/test_advanced_analytics.json")

    # Simulate some data
    now = datetime.now()

    # Track messages and responses
    for i in range(10):
        analytics.track_message_received(f"92300123456{i}", now - timedelta(hours=i))
        analytics.track_response_sent(f"92300123456{i}", 2.5, now - timedelta(hours=i))

    # Track new leads
    analytics.track_new_lead("923001234567", "whatsapp")
    analytics.track_new_lead("923001234568", "whatsapp")
    analytics.track_new_lead("923001234569", "referral")

    # Track conversions
    analytics.track_conversion("923001234567", "meeting_scheduled", 0)
    analytics.track_conversion("923001234568", "project_started", 5000)

    # Get comprehensive report
    report = analytics.get_comprehensive_report()

    print("\n[RESPONSE TIMES]")
    print(f"Average: {report['response_times']['average']:.2f}s")
    print(f"Median: {report['response_times']['median']:.2f}s")
    print(f"Count: {report['response_times']['count']}")

    print("\n[CONVERSION RATE]")
    print(f"Leads: {report['conversion_rate']['total_leads']}")
    print(f"Conversions: {report['conversion_rate']['total_conversions']}")
    print(f"Rate: {report['conversion_rate']['conversion_rate']}%")

    print("\n[LEAD SOURCES]")
    for source, data in report['lead_sources']['sources'].items():
        print(f"{source}: {data['count']} ({data['percentage']}%)")

    print("\n[REVENUE]")
    print(f"Total: ${report['revenue']['total_revenue']}")
    print(f"Average per conversion: ${report['revenue']['average_value']}")

    print("\n" + "="*70)
    print("ADVANCED ANALYTICS TEST COMPLETE")
    print("="*70)
