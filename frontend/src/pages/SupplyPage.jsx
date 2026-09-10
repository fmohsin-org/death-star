import { useState } from 'react'

const inventory = [
  { id: 'TBG-001', name: 'Tibanna Gas (Grade A)', qty: 12500, unit: 'kg', reorder: 5000, supplier: 'Cloud City Mining', price: 450 },
  { id: 'KYB-001', name: 'Kyber Crystal (Synthetic)', qty: 340, unit: 'units', reorder: 100, supplier: 'Jedha Quarry', price: 89000 },
  { id: 'KYB-002', name: 'Kyber Crystal (Natural)', qty: 28, unit: 'units', reorder: 50, supplier: 'Ilum Extraction', price: 245000 },
  { id: 'DUR-001', name: 'Durasteel Plating', qty: 48200, unit: 'panels', reorder: 10000, supplier: 'Kuat Drive Yards', price: 120 },
  { id: 'BLS-001', name: 'Blaster Power Packs', qty: 892000, unit: 'units', reorder: 200000, supplier: 'BlasTech Industries', price: 15 },
  { id: 'HYP-001', name: 'Hypermatter Fuel', qty: 8900, unit: 'tons', reorder: 3000, supplier: 'Sienar Fleet Systems', price: 2200 },
  { id: 'RAT-001', name: 'Field Rations (Standard)', qty: 2400000, unit: 'units', reorder: 500000, supplier: 'Imperial Commissary', price: 3 },
  { id: 'MED-001', name: 'Bacta Supplies', qty: 4200, unit: 'liters', reorder: 2000, supplier: 'Thyferra Corp', price: 800 },
]

const payments = [
  { id: 'PAY-4821', contractor: 'Kuat Drive Yards', amount: 15840000, card: '**** **** **** 4421', status: 'PROCESSED', date: '2024-03-15' },
  { id: 'PAY-4822', contractor: 'BlasTech Industries', amount: 2680000, card: '**** **** **** 7733', status: 'PROCESSED', date: '2024-03-14' },
  { id: 'PAY-4823', contractor: 'Sienar Fleet Systems', amount: 9200000, card: '**** **** **** 1199', status: 'PENDING', date: '2024-03-16' },
]

export default function SupplyPage() {
  const [tab, setTab] = useState('inventory')
  const [search, setSearch] = useState('')

  const filtered = inventory.filter(i =>
    i.name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div>
      <h1 className="page-title">Supply Chain</h1>
      <p className="page-subtitle">Logistics, Inventory + Procurement</p>

      <div className="tabs">
        <button className={`tab ${tab === 'inventory' ? 'active' : ''}`} onClick={() => setTab('inventory')}>Inventory</button>
        <button className={`tab ${tab === 'payments' ? 'active' : ''}`} onClick={() => setTab('payments')}>Payments</button>
        <button className={`tab ${tab === 'suppliers' ? 'active' : ''}`} onClick={() => setTab('suppliers')}>Suppliers</button>
      </div>

      {tab === 'inventory' && (
        <>
          <div className="search-bar">
            <div className="vuln-indicator" style={{ flex: 1, display: 'flex' }}>
              <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search inventory..." style={{ flex: 1 }} />
              <span className="vuln-dot" style={{ marginLeft: -20, marginTop: 14 }} />
              <span className="vuln-tooltip">CWE-89: searchInventory() concatenates input into SQL (SupplyService.java:56)</span>
            </div>
            <button className="btn btn-primary">Search</button>
          </div>
          <div className="card">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Item</th>
                  <th>Quantity</th>
                  <th>Supplier</th>
                  <th>Unit Price</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(i => (
                  <tr key={i.id}>
                    <td className="mono">{i.id}</td>
                    <td style={{ color: 'var(--text-primary)' }}>{i.name}</td>
                    <td className="mono">{i.qty.toLocaleString()} {i.unit}</td>
                    <td>
                      <span className="vuln-indicator">
                        {i.supplier}
                        <span className="vuln-dot" />
                        <span className="vuln-tooltip">CWE-918: proxySupplierRequest() opens HTTP to any URL (SSRF)</span>
                      </span>
                    </td>
                    <td className="mono">{i.price.toLocaleString()} cr</td>
                    <td>
                      {i.qty <= i.reorder ? (
                        <span className="severity-badge sev-high">LOW STOCK</span>
                      ) : (
                        <span style={{ color: 'var(--safe)', fontSize: '0.8rem' }}>IN STOCK</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {tab === 'payments' && (
        <div className="card">
          <div className="section-title" style={{ marginTop: 0 }}>
            <span className="vuln-indicator">
              Payment Transactions
              <span className="vuln-dot" />
              <span className="vuln-tooltip">CWE-311: PCI-DSS violations -- raw card numbers + CVV stored, logged, and encrypted with DES</span>
            </span>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Payment ID</th>
                <th>Contractor</th>
                <th>Amount</th>
                <th>Card</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {payments.map(p => (
                <tr key={p.id}>
                  <td className="mono">{p.id}</td>
                  <td>{p.contractor}</td>
                  <td className="mono">{p.amount.toLocaleString()} cr</td>
                  <td>
                    <span className="vuln-indicator">
                      <span className="mono">{p.card}</span>
                      <span className="vuln-dot" />
                      <span className="vuln-tooltip">CWE-312: raw_card_number stored, CVV persisted (PaymentService.java)</span>
                    </span>
                  </td>
                  <td>
                    <span className={`severity-badge ${p.status === 'PROCESSED' ? 'sev-low' : 'sev-medium'}`}>{p.status}</span>
                  </td>
                  <td className="mono" style={{ fontSize: '0.8rem' }}>{p.date}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="terminal" style={{ marginTop: 16, fontSize: '0.72rem' }}>
            <span style={{ color: 'var(--danger)' }}>// Hardcoded in PaymentService.java</span>{'\n'}
            STRIPE_SECRET = "sk_live_51Abc123def456ghi789jkl..."{'\n'}
            STRIPE_WEBHOOK = "whsec_imperial_payment_9a8b7c..."{'\n'}
            TREASURY_ACCOUNT = "acct_1Imperial2Death3Star"{'\n'}
            DES_KEY = "Imp3r1al"{'\n'}
          </div>
        </div>
      )}

      {tab === 'suppliers' && (
        <div className="card">
          <div className="section-title" style={{ marginTop: 0 }}>Supplier API Keys</div>
          <div className="terminal" style={{ fontSize: '0.72rem' }}>
            <span style={{ color: 'var(--danger)' }}>// Hardcoded in SupplyConfig.java</span>{'\n'}
            KUAT_DRIVE_YARDS_API   = "kdy_sk_live_9f8e7d6c5b4a..."{'\n'}
            SIENAR_FLEET_API       = "sfs_sk_live_1a2b3c4d5e6f..."{'\n'}
            BLASTECH_INDUSTRIES    = "bti_sk_live_a1b2c3d4e5f6..."{'\n'}
            CZERKA_ARMS_TOKEN      = "czk_tk_live_7h8i9j0k1l2m..."{'\n'}
            CORELLIAN_ENGINEERING  = "cec_wh_live_3n4o5p6q7r8s..."{'\n'}
            PAYMENT_GATEWAY_SK     = "pgw_sk_live_t9u0v1w2x3y4..."{'\n'}
            IMPERIAL_TREASURY      = "imp_treasury_bearer_z5a6b7..."{'\n'}
            AES_KEY                = "AES256-Imperial-Supply-K3y-2024!"{'\n'}
          </div>
        </div>
      )}
    </div>
  )
}
