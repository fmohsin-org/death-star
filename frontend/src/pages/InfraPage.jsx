import { useState } from 'react'

const dockerImages = [
  { service: 'gateway', base: 'openjdk:11-jdk-slim-buster', baseStatus: 'EOL', runsAs: 'root', ssh: true, debug: '5005', secretsInEnv: 4 },
  { service: 'weapons', base: 'golang:1.16', baseStatus: 'EOL', runsAs: 'root', ssh: true, debug: '2345', secretsInEnv: 3 },
  { service: 'crew', base: 'python:3.8-slim', baseStatus: 'EOL', runsAs: 'root', ssh: true, debug: '5678', secretsInEnv: 3 },
  { service: 'comms', base: 'node:14', baseStatus: 'EOL', runsAs: 'root', ssh: true, debug: '9229', secretsInEnv: 4 },
  { service: 'life-support', base: 'dotnet/sdk:6.0', baseStatus: 'EOL', runsAs: 'root', ssh: true, debug: '-', secretsInEnv: 3 },
  { service: 'supply', base: 'openjdk:11-jdk-slim-buster', baseStatus: 'EOL', runsAs: 'root', ssh: true, debug: '5005', secretsInEnv: 3 },
  { service: 'docking', base: 'python:3.8-slim', baseStatus: 'EOL', runsAs: 'root', ssh: true, debug: '5678', secretsInEnv: 3 },
  { service: 'targeting', base: 'nvidia/cuda:11.8-devel', baseStatus: 'OK', runsAs: 'root', ssh: true, debug: '5678', secretsInEnv: 4 },
  { service: 'security-core', base: 'ubuntu:18.04', baseStatus: 'EOL', runsAs: 'root', ssh: true, debug: '-', secretsInEnv: 4 },
]

const k8sIssues = [
  { resource: 'All Deployments', issue: 'privileged: true', severity: 'CRITICAL' },
  { resource: 'All Deployments', issue: 'runAsUser: 0 (root)', severity: 'CRITICAL' },
  { resource: 'All Deployments', issue: 'hostNetwork: true', severity: 'CRITICAL' },
  { resource: 'All Deployments', issue: 'hostPID: true', severity: 'CRITICAL' },
  { resource: 'All Deployments', issue: 'Docker socket mounted', severity: 'CRITICAL' },
  { resource: 'All Deployments', issue: 'Host / mounted at /host (R/W)', severity: 'CRITICAL' },
  { resource: 'RBAC', issue: 'system:unauthenticated -> cluster-admin', severity: 'CRITICAL' },
  { resource: 'RBAC', issue: 'system:authenticated -> cluster-admin', severity: 'CRITICAL' },
  { resource: 'NetworkPolicy', issue: 'Allow all ingress + egress', severity: 'CRITICAL' },
  { resource: 'ConfigMaps', issue: 'DB passwords, cloud creds in ConfigMap (not Secret)', severity: 'CRITICAL' },
  { resource: 'Services', issue: 'Debug + SSH ports on NodePort', severity: 'HIGH' },
]

const terraformIssues = [
  { module: 'main.tf', issue: 'Hardcoded AWS access + secret keys in provider', severity: 'CRITICAL' },
  { module: 'variables.tf', issue: 'enable_encryption=false, enable_waf=false, enable_cloudtrail=false', severity: 'CRITICAL' },
  { module: 'compute', issue: 'IMDSv1 enabled, secrets in user_data, curl|bash', severity: 'CRITICAL' },
  { module: 'database', issue: 'publicly_accessible=true, storage_encrypted=false', severity: 'CRITICAL' },
  { module: 'iam', issue: 'Principal:* on all roles, Action:* Resource:*', severity: 'CRITICAL' },
  { module: 'network', issue: '0.0.0.0/0 on SSH, RDP, DB, debug ports', severity: 'CRITICAL' },
  { module: 'storage', issue: 'S3 public-read-write, public access blocks disabled', severity: 'CRITICAL' },
]

export default function InfraPage() {
  const [tab, setTab] = useState('docker')

  return (
    <div>
      <h1 className="page-title">Infrastructure</h1>
      <p className="page-subtitle">Container, Kubernetes + Terraform Security</p>

      <div className="stats-row">
        <div className="stat-card stat-critical">
          <div className="stat-value">100+</div>
          <div className="stat-label">Container Issues</div>
        </div>
        <div className="stat-card stat-critical">
          <div className="stat-value">24</div>
          <div className="stat-label">K8s Issues</div>
        </div>
        <div className="stat-card stat-critical">
          <div className="stat-value">53</div>
          <div className="stat-label">Terraform Issues</div>
        </div>
        <div className="stat-card stat-high">
          <div className="stat-value">60+</div>
          <div className="stat-label">CI/CD Issues</div>
        </div>
      </div>

      <div className="tabs">
        <button className={`tab ${tab === 'docker' ? 'active' : ''}`} onClick={() => setTab('docker')}>Dockerfiles</button>
        <button className={`tab ${tab === 'k8s' ? 'active' : ''}`} onClick={() => setTab('k8s')}>Kubernetes</button>
        <button className={`tab ${tab === 'terraform' ? 'active' : ''}`} onClick={() => setTab('terraform')}>Terraform</button>
        <button className={`tab ${tab === 'cicd' ? 'active' : ''}`} onClick={() => setTab('cicd')}>CI/CD</button>
      </div>

      {tab === 'docker' && (
        <div className="card">
          <table className="data-table">
            <thead>
              <tr>
                <th>Service</th>
                <th>Base Image</th>
                <th>Status</th>
                <th>User</th>
                <th>SSH</th>
                <th>Debug Port</th>
                <th>Secrets</th>
              </tr>
            </thead>
            <tbody>
              {dockerImages.map(d => (
                <tr key={d.service}>
                  <td className="mono" style={{ color: 'var(--text-primary)' }}>{d.service}</td>
                  <td className="mono" style={{ fontSize: '0.78rem' }}>{d.base}</td>
                  <td>
                    <span className={`severity-badge ${d.baseStatus === 'EOL' ? 'sev-critical' : 'sev-low'}`}>{d.baseStatus}</span>
                  </td>
                  <td><span className="severity-badge sev-critical">{d.runsAs}</span></td>
                  <td><span style={{ color: 'var(--danger)' }}>{d.ssh ? 'YES' : 'NO'}</span></td>
                  <td className="mono">{d.debug}</td>
                  <td><span className="severity-badge sev-critical">{d.secretsInEnv} in ENV</span></td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ marginTop: 12, fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            All images: no USER directive, openssh-server installed, COPY . . ships source, no multi-stage builds, no health checks
          </div>
        </div>
      )}

      {tab === 'k8s' && (
        <div className="card">
          <table className="data-table">
            <thead>
              <tr>
                <th>Resource</th>
                <th>Issue</th>
                <th>Severity</th>
              </tr>
            </thead>
            <tbody>
              {k8sIssues.map((k, i) => (
                <tr key={i}>
                  <td className="mono" style={{ color: 'var(--text-primary)' }}>{k.resource}</td>
                  <td>{k.issue}</td>
                  <td><span className={`severity-badge sev-${k.severity.toLowerCase()}`}>{k.severity}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'terraform' && (
        <div className="card">
          <table className="data-table">
            <thead>
              <tr>
                <th>Module</th>
                <th>Issue</th>
                <th>Severity</th>
              </tr>
            </thead>
            <tbody>
              {terraformIssues.map((t, i) => (
                <tr key={i}>
                  <td className="mono" style={{ color: 'var(--text-primary)' }}>{t.module}</td>
                  <td>{t.issue}</td>
                  <td><span className={`severity-badge sev-${t.severity.toLowerCase()}`}>{t.severity}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'cicd' && (
        <div className="card">
          <div className="section-title" style={{ marginTop: 0 }}>GitHub Actions Workflows (10 files, 60+ issues)</div>
          <div className="terminal" style={{ fontSize: '0.72rem' }}>
            <span style={{ color: 'var(--danger)' }}>Script Injection vectors:</span>{'\n'}
            {'  ci.yml:31        - ${{ github.event.pull_request.title }} in shell\n'}
            {'  ci.yml:33        - ${{ github.event.pull_request.body }} in shell\n'}
            {'  ci.yml:48        - ${{ github.event.comment.body }} in shell\n'}
            {'  ci.yml:78        - eval() with PR title in github-script\n'}
            {'  release.yml:100  - PR body in template literal\n\n'}
            <span style={{ color: 'var(--danger)' }}>Pwn Request (pull_request_target + checkout PR head):</span>{'\n'}
            {'  deploy-production.yml - builds + deploys untrusted PR code\n'}
            {'  release.yml           - publishes to NPM/PyPI/Docker from PR\n\n'}
            <span style={{ color: 'var(--danger)' }}>Auto-merge without security review:</span>{'\n'}
            {'  dependabot-auto-merge.yml - audit-level:none, allow-major-updates\n\n'}
            <span style={{ color: 'var(--danger)' }}>Secrets committed to workflow files:</span>{'\n'}
            {'  SSH private keys, AWS credentials, Vault tokens, Docker passwords,\n'}
            {'  NPM tokens, PyPI tokens, GPG passphrases, GCP service account JSON,\n'}
            {'  Kubeconfig with bearer token, Stripe keys, registry credentials\n\n'}
            <span style={{ color: 'var(--danger)' }}>CodeQL configured to EXCLUDE critical/high findings:</span>{'\n'}
            {'  codeql-analysis.yml:151 - exclude tags: /security-severity:(critical|high)/\n'}
          </div>
        </div>
      )}
    </div>
  )
}
