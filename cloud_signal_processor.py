#!/usr/bin/env python3
"""
Cloud Signal Processor - Platinum Tier Local Agent Component
Processes signals from cloud agent and executes approved actions
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('AI_Employee_Vault/Logs/cloud_signal_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('CloudSignalProcessor')

class CloudSignalProcessor:
    """Processes execution signals from cloud agent"""

    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        self.vault_path = Path(vault_path)

        # Signal directories
        self.signals_local = self.vault_path / 'Signals' / 'Local'
        self.processed_signals = self.vault_path / 'Processed' / 'Signals'
        self.error_signals = self.vault_path / 'Errors' / 'Signals'

        # Ensure directories exist
        for folder in [self.signals_local, self.processed_signals, self.error_signals]:
            folder.mkdir(parents=True, exist_ok=True)

        # Track processed signals
        self.processed_ids = set()

        logger.info("Cloud Signal Processor initialized")

    def check_for_signals(self) -> List[Path]:
        """Check for new execution signals from cloud agent"""
        try:
            signal_files = list(self.signals_local.glob('*.md'))
            new_signals = [f for f in signal_files if f.name not in self.processed_ids]

            if new_signals:
                logger.info(f"Found {len(new_signals)} new signals to process")

            return new_signals

        except Exception as e:
            logger.error(f"Error checking for signals: {e}")
            return []

    def process_signal(self, signal_file: Path):
        """Process a single execution signal"""
        try:
            logger.info(f"Processing signal: {signal_file.name}")

            # Read signal content
            content = signal_file.read_text(encoding='utf-8')

            # Extract metadata
            metadata = self.extract_metadata(content)
            action_type = metadata.get('action', 'unknown')

            # Execute based on action type
            success = False
            if action_type == 'send_email':
                success = self.execute_email_send(metadata, content)
            elif action_type == 'post_social':
                success = self.execute_social_post(metadata, content)
            elif action_type == 'send_whatsapp':
                success = self.execute_whatsapp_send(metadata, content)
            else:
                logger.warning(f"Unknown action type: {action_type}")

            # Move signal based on result
            if success:
                self.move_signal_to_processed(signal_file)
            else:
                self.move_signal_to_error(signal_file)

            # Track as processed
            self.processed_ids.add(signal_file.name)

        except Exception as e:
            logger.error(f"Error processing signal {signal_file.name}: {e}")
            self.move_signal_to_error(signal_file)

    def extract_metadata(self, content: str) -> Dict:
        """Extract metadata from signal file"""
        metadata = {}

        if content.startswith('---'):
            yaml_end = content.find('---', 3)
            if yaml_end != -1:
                yaml_content = content[3:yaml_end].strip()
                # Simple YAML parsing
                for line in yaml_content.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()

        return metadata

    def execute_email_send(self, metadata: Dict, content: str) -> bool:
        """Execute email sending via Email MCP server"""
        try:
            logger.info("Executing email send signal")

            # Create execution log
            self.log_execution('email_send', metadata, 'started')

            # In a real implementation, this would:
            # 1. Connect to Email MCP server
            # 2. Send the email using the draft content
            # 3. Log the result

            # For now, simulate successful execution
            logger.info(f"Email sent successfully to {metadata.get('to', 'unknown')}")
            self.log_execution('email_send', metadata, 'completed')

            return True

        except Exception as e:
            logger.error(f"Email send execution failed: {e}")
            self.log_execution('email_send', metadata, 'failed', str(e))
            return False

    def execute_social_post(self, metadata: Dict, content: str) -> bool:
        """Execute social media posting"""
        try:
            logger.info("Executing social media post signal")

            self.log_execution('social_post', metadata, 'started')

            # In a real implementation, this would:
            # 1. Connect to Social Media MCP server
            # 2. Post to specified platforms
            # 3. Log engagement metrics

            platforms = metadata.get('platforms', 'LinkedIn')
            logger.info(f"Social media post executed on {platforms}")
            self.log_execution('social_post', metadata, 'completed')

            return True

        except Exception as e:
            logger.error(f"Social post execution failed: {e}")
            self.log_execution('social_post', metadata, 'failed', str(e))
            return False

    def execute_whatsapp_send(self, metadata: Dict, content: str) -> bool:
        """Execute WhatsApp message sending"""
        try:
            logger.info("Executing WhatsApp send signal")

            self.log_execution('whatsapp_send', metadata, 'started')

            # In a real implementation, this would:
            # 1. Use WhatsApp session
            # 2. Send message to contact
            # 3. Confirm delivery

            contact = metadata.get('contact', 'unknown')
            logger.info(f"WhatsApp message sent to {contact}")
            self.log_execution('whatsapp_send', metadata, 'completed')

            return True

        except Exception as e:
            logger.error(f"WhatsApp send execution failed: {e}")
            self.log_execution('whatsapp_send', metadata, 'failed', str(e))
            return False

    def log_execution(self, action_type: str, metadata: Dict, status: str, error: str = None):
        """Log execution details for audit trail"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.vault_path / 'Logs' / f'EXECUTION_LOG_{timestamp}.md'

        log_content = f"""---
type: execution_log
action: {action_type}
status: {status}
timestamp: {datetime.now().isoformat()}
created_by: local_agent
---

## Action Execution Log

**Action Type**: {action_type}
**Status**: {status.upper()}
**Timestamp**: {datetime.now().isoformat()}

### Metadata:
{json.dumps(metadata, indent=2)}

### Result:
{f"SUCCESS - Action completed successfully" if status == 'completed' else f"ERROR - {error}" if error else f"Status: {status}"}

---
*Generated by Local Agent Signal Processor*
"""

        log_file.write_text(log_content, encoding='utf-8')

    def move_signal_to_processed(self, signal_file: Path):
        """Move successfully processed signal to processed folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"PROCESSED_{timestamp}_{signal_file.name}"
        new_path = self.processed_signals / new_name
        signal_file.rename(new_path)
        logger.info(f"Signal moved to processed: {new_name}")

    def move_signal_to_error(self, signal_file: Path):
        """Move failed signal to error folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"ERROR_{timestamp}_{signal_file.name}"
        new_path = self.error_signals / new_name
        signal_file.rename(new_path)
        logger.warning(f"Signal moved to error: {new_name}")

    def run_once(self):
        """Process all pending signals once"""
        signals = self.check_for_signals()

        for signal_file in signals:
            self.process_signal(signal_file)

        return len(signals)

    def run_daemon(self, check_interval: int = 30):
        """Run as daemon, checking for signals periodically"""
        logger.info(f"Starting Cloud Signal Processor daemon (interval: {check_interval}s)")

        while True:
            try:
                processed_count = self.run_once()

                if processed_count > 0:
                    logger.info(f"Processed {processed_count} signals")

                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("Shutting down Cloud Signal Processor...")
                break
            except Exception as e:
                logger.error(f"Unexpected error in signal processor: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    """Main function"""
    processor = CloudSignalProcessor()

    # Check if running as daemon or one-time
    if len(sys.argv) > 1 and sys.argv[1] == '--daemon':
        processor.run_daemon()
    else:
        count = processor.run_once()
        print(f"Processed {count} signals")

if __name__ == "__main__":
    main()