// PM2 Ecosystem Configuration for Cloud Deployment
module.exports = {
  apps: [
    {
      name: 'cloud-file-watcher',
      script: 'venv/bin/python',
      args: 'scripts/cloud_file_watcher.py',
      cwd: '/home/ubuntu/ai-employee',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'development',
        AGENT_TYPE: 'cloud',
        VAULT_PATH: '/home/ubuntu/ai-employee/vault-sync'
      },
      env_production: {
        NODE_ENV: 'production',
        AGENT_TYPE: 'cloud',
        VAULT_PATH: '/home/ubuntu/ai-employee/vault-sync'
      },
      error_file: 'logs/cloud-file-watcher-error.log',
      out_file: 'logs/cloud-file-watcher-out.log',
      log_file: 'logs/cloud-file-watcher-combined.log',
      time: true
    },
    {
      name: 'cloud-gmail-watcher',
      script: 'venv/bin/python',
      args: 'scripts/cloud_gmail_watcher.py',
      cwd: '/home/ubuntu/ai-employee',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'development',
        AGENT_TYPE: 'cloud'
      },
      env_production: {
        NODE_ENV: 'production',
        AGENT_TYPE: 'cloud'
      },
      error_file: 'logs/cloud-gmail-watcher-error.log',
      out_file: 'logs/cloud-gmail-watcher-out.log',
      log_file: 'logs/cloud-gmail-watcher-combined.log',
      time: true
    },
    {
      name: 'cloud-orchestrator',
      script: 'venv/bin/python',
      args: 'scripts/cloud_orchestrator.py',
      cwd: '/home/ubuntu/ai-employee',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development',
        AGENT_TYPE: 'cloud'
      },
      env_production: {
        NODE_ENV: 'production',
        AGENT_TYPE: 'cloud'
      },
      error_file: 'logs/cloud-orchestrator-error.log',
      out_file: 'logs/cloud-orchestrator-out.log',
      log_file: 'logs/cloud-orchestrator-combined.log',
      time: true
    },
    {
      name: 'vault-sync-daemon',
      script: 'venv/bin/python',
      args: 'scripts/vault_sync_daemon.py',
      cwd: '/home/ubuntu/ai-employee',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        NODE_ENV: 'development',
        SYNC_INTERVAL: '30'
      },
      env_production: {
        NODE_ENV: 'production',
        SYNC_INTERVAL: '60'
      },
      error_file: 'logs/vault-sync-error.log',
      out_file: 'logs/vault-sync-out.log',
      log_file: 'logs/vault-sync-combined.log',
      time: true
    }
  ]
};