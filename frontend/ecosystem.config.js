module.exports = {
  apps: [
    {
      name: 'funeng-frontend',
      script: 'pnpm',
      args: 'dev --host 0.0.0.0 --port 5173',
      cwd: '/home/admin/.openclaw/workspace/coder/funeng/frontend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'development'
      }
    }
  ]
};
