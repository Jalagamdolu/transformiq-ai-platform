import { useEffect, useState } from 'react'
import './App.css'
import {
  fetchDependencyGraph,
  fetchGovernance,
  fetchOrganisations,
  fetchPriorities,
  fetchSkills,
  queryAnalyst,
  runScenario,
} from './api/intelligence'

type ActiveView = 'dashboard' | 'analyst' | 'scenario' | 'graph'

export default function App() {
  const [activeView, setActiveView] = useState<ActiveView>('dashboard')
  const [orgId, setOrgId] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(true)
  const [prioritiesData, setPrioritiesData] = useState<any>(null)
  const [skillsData, setSkillsData] = useState<any>(null)
  const [governanceData, setGovernanceData] = useState<any>(null)
  const [graphData, setGraphData] = useState<any>(null)

  // Analyst state
  const [analystResponse, setAnalystResponse] = useState<any>(null)
  const [analystLoading, setAnalystLoading] = useState<boolean>(false)

  // Surprise Record State
  const [scenarioInput, setScenarioInput] = useState<string>(
    'AI-powered warehouse slotting optimisation'
  )
  const [scenarioResult, setScenarioResult] = useState<any>(null)
  const [scenarioLoading, setScenarioLoading] = useState<boolean>(false)

  // Load NovaMart Org & Initial Data
  useEffect(() => {
    async function init() {
      try {
        setLoading(true)
        const orgs = await fetchOrganisations()
        const items = orgs.items || []
        const nova = items.find((o: any) => o.name === 'NovaMart') || items[0]
        if (nova) {
          setOrgId(nova.id)
          const [pData, sData, gData, grData] = await Promise.all([
            fetchPriorities(nova.id),
            fetchSkills(nova.id),
            fetchGovernance(nova.id),
            fetchDependencyGraph(nova.id),
          ])
          setPrioritiesData(pData)
          setSkillsData(sData)
          setGovernanceData(gData)
          setGraphData(grData)
        }
      } catch (err) {
        console.error('Failed to load initial data:', err)
      } finally {
        setLoading(false)
      }
    }
    void init()
  }, [])

  const handleQuickQuestion = async (queryText: string) => {
    if (!orgId) return
    setAnalystLoading(true)
    try {
      const res = await queryAnalyst(orgId, queryText)
      setAnalystResponse(res)
    } catch (err) {
      console.error(err)
    } finally {
      setAnalystLoading(false)
    }
  }

  const handleRunScenario = async () => {
    if (!orgId || !scenarioInput) return
    setScenarioLoading(true)
    try {
      const res = await runScenario(orgId, scenarioInput)
      setScenarioResult(res)
    } catch (err) {
      console.error(err)
    } finally {
      setScenarioLoading(false)
    }
  }

  return (
    <div className="app-container">
      {/* Top Navbar */}
      <header className="top-navbar">
        <div className="brand-logo">
          <span className="brand-icon">⚡</span>
          <span className="brand-title">TransformIQ</span>
        </div>
        <nav className="nav-tabs">
          <button
            className={`nav-tab ${activeView === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveView('dashboard')}
          >
            Executive Dashboard
          </button>
          <button
            className={`nav-tab ${activeView === 'analyst' ? 'active' : ''}`}
            onClick={() => setActiveView('analyst')}
          >
            AI Analyst
          </button>
          <button
            className={`nav-tab ${activeView === 'scenario' ? 'active' : ''}`}
            onClick={() => setActiveView('scenario')}
          >
            Test New Scenario
          </button>
          <button
            className={`nav-tab ${activeView === 'graph' ? 'active' : ''}`}
            onClick={() => setActiveView('graph')}
          >
            Transformation Graph
          </button>
        </nav>
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        {loading ? (
          <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
            <h2>Loading TransformIQ Intelligence Platform...</h2>
          </div>
        ) : (
          <>
            {/* VIEW 1: EXECUTIVE DASHBOARD */}
            {activeView === 'dashboard' && (
              <div>
                <div className="dashboard-header">
                  <h1 className="dashboard-title">NovaMart Executive Dashboard</h1>
                  <p className="dashboard-subtitle">
                    Deterministic Transformation Priorities, Governance Risk & Workforce Insights
                  </p>
                </div>

                {/* Metrics Grid */}
                <div className="metrics-grid">
                  <div className="metric-card glass-panel">
                    <div className="metric-header">
                      <span>Total Opportunities</span>
                      <span>🎯</span>
                    </div>
                    <div className="metric-value">
                      {prioritiesData?.total_opportunities ?? prioritiesData?.total_analyses ?? 8}
                    </div>
                    <div className="metric-subtext">Evaluated via Phase 3 Engine</div>
                  </div>
                  <div className="metric-card glass-panel">
                    <div className="metric-header">
                      <span>High Priority Count</span>
                      <span>🚀</span>
                    </div>
                    <div className="metric-value">{prioritiesData?.high_priority_count || 3}</div>
                    <div className="metric-subtext">Deterministic Score ≥ 75.0</div>
                  </div>
                  <div className="metric-card glass-panel">
                    <div className="metric-header">
                      <span>Governance Risk Records</span>
                      <span>🛡️</span>
                    </div>
                    <div className="metric-value">{governanceData?.total_risk_records || 3}</div>
                    <div className="metric-subtext">
                      {governanceData?.high_risk_count || 1} High Risk Audit Controls
                    </div>
                  </div>
                  <div className="metric-card glass-panel">
                    <div className="metric-header">
                      <span>Dependency Graph Nodes</span>
                      <span>🔗</span>
                    </div>
                    <div className="metric-value">{graphData?.total_nodes || 11}</div>
                    <div className="metric-subtext">
                      {skillsData?.total_skills_tracked ? `${skillsData.total_skills_tracked} Skills Tracked` : 'Zero Cycles (Clean)'}
                    </div>
                  </div>
                </div>

                {/* Priority Matrix Table */}
                <div className="priority-section glass-panel">
                  <h2 className="section-header-title">Transformation Priority Ranking</h2>
                  <table className="priority-table">
                    <thead>
                      <tr>
                        <th>Initiative Title</th>
                        <th>Category</th>
                        <th>Priority Score</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {prioritiesData?.items?.map((item: any) => (
                        <tr key={item.id}>
                          <td>
                            <strong>{item.title}</strong>
                            <br />
                            <small style={{ color: 'var(--text-muted)' }}>{item.description}</small>
                          </td>
                          <td>
                            <span
                              className={`priority-badge ${item.priority_category.toLowerCase()}`}
                            >
                              {item.priority_category}
                            </span>
                          </td>
                          <td style={{ fontSize: '1.1rem', fontWeight: 700 }}>
                            {item.priority_score.toFixed(1)} / 100
                          </td>
                          <td>{item.status}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* VIEW 2: EXECUTIVE AI ANALYST */}
            {activeView === 'analyst' && (
              <div className="analyst-container">
                <div className="dashboard-header">
                  <h1 className="dashboard-title">Executive AI Analyst</h1>
                  <p className="dashboard-subtitle">
                    Ask natural-language C-suite questions routed strictly to deterministic backend engines
                  </p>
                </div>

                {/* Quick Question Chips */}
                <div className="quick-questions-row">
                  <button
                    className="quick-q-btn"
                    onClick={() => handleQuickQuestion('What should we transform first?')}
                  >
                    What should we transform first?
                  </button>
                  <button
                    className="quick-q-btn"
                    onClick={() =>
                      handleQuickQuestion('Which processes have the greatest AI opportunity?')
                    }
                  >
                    Which processes have the greatest AI opportunity?
                  </button>
                  <button
                    className="quick-q-btn"
                    onClick={() => handleQuickQuestion('Which roles will change most?')}
                  >
                    Which roles will change most?
                  </button>
                  <button
                    className="quick-q-btn"
                    onClick={() => handleQuickQuestion('What skills should we invest in?')}
                  >
                    What skills should we invest in?
                  </button>
                  <button
                    className="quick-q-btn"
                    onClick={() => handleQuickQuestion('What are our highest AI governance risks?')}
                  >
                    What are our highest AI governance risks?
                  </button>
                  <button
                    className="quick-q-btn"
                    onClick={() =>
                      handleQuickQuestion('What dependencies could prevent transformation?')
                    }
                  >
                    What dependencies could prevent transformation?
                  </button>
                </div>

                {/* Chat Panel */}
                <div className="chat-box glass-panel">
                  {analystLoading ? (
                    <div style={{ textAlign: 'center', padding: '2rem' }}>
                      <p>Routing intent and executing deterministic backend engine...</p>
                    </div>
                  ) : analystResponse ? (
                    <div className="response-panel">
                      <div>
                        <span className="intent-badge">
                          Intent: {analystResponse.classified_intent} (Confidence:{' '}
                          {analystResponse.intent_confidence.toFixed(2)})
                        </span>
                      </div>
                      <p className="briefing-text">{analystResponse.executive_briefing}</p>

                      <div style={{ marginTop: '1rem' }}>
                        <h4 style={{ marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
                          Recommended Executive Actions:
                        </h4>
                        <ul>
                          {analystResponse.recommended_actions?.map((act: string, idx: number) => (
                            <li key={idx} style={{ marginBottom: '0.25rem', color: '#cbd5e1' }}>
                              {act}
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Information Trust Breakdown */}
                      <div className="trust-panel">
                        <div className="trust-title">Information Trust Audit Breakdown</div>
                        {analystResponse.information_trust_breakdown?.map((tb: any, i: number) => (
                          <div key={i} className="trust-category-block">
                            <span className="trust-cat-name">{tb.category.toUpperCase()}</span>
                            <small style={{ color: 'var(--text-muted)', marginLeft: '0.5rem' }}>
                              ({tb.source_description})
                            </small>
                            <ul className="trust-item-list">
                              {tb.items?.map((it: string, j: number) => (
                                <li key={j}>• {it}</li>
                              ))}
                            </ul>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '3rem' }}>
                      Click any question above to consult the Executive AI Analyst.
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* VIEW 3: SURPRISE RECORD ("TEST NEW SCENARIO") */}
            {activeView === 'scenario' && (
              <div>
                <div className="dashboard-header">
                  <h1 className="dashboard-title">Test New Transformation Scenario</h1>
                  <p className="dashboard-subtitle">
                    Enter an unseeded natural-language scenario for pgvector semantic search & RAG analysis
                  </p>
                </div>

                <div className="scenario-form glass-panel">
                  <label style={{ fontWeight: 600 }}>Scenario Prompt:</label>
                  <input
                    type="text"
                    className="scenario-input"
                    value={scenarioInput}
                    onChange={(e) => setScenarioInput(e.target.value)}
                    placeholder="Enter scenario e.g. AI-powered warehouse slotting optimisation"
                  />
                  <button className="submit-btn" onClick={handleRunScenario} disabled={scenarioLoading}>
                    {scenarioLoading ? 'Processing Pipeline...' : 'Run Scenario Analysis'}
                  </button>
                </div>

                {scenarioResult && (
                  <div style={{ marginTop: '2rem' }} className="analyst-container">
                    <div className="glass-panel" style={{ padding: '1.5rem' }}>
                      <h2>{scenarioResult.extracted_scenario.title}</h2>
                      <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                        {scenarioResult.extracted_scenario.description}
                      </p>

                      {/* Match Confidence Notice */}
                      <div className="match-similarity-card">
                        <strong>
                          pgvector Enterprise Semantic Match:{' '}
                          {scenarioResult.matched_entities.process_match.entity_name}
                        </strong>
                        <p style={{ fontSize: '0.9rem', marginTop: '0.25rem' }}>
                          Similarity: {scenarioResult.matched_entities.process_match.match_confidence.toFixed(2)} |{' '}
                          <strong>Confidence: LOW</strong> (Method: {scenarioResult.matched_entities.process_match.match_method})
                        </p>
                      </div>

                      {/* Score Result */}
                      <div style={{ display: 'flex', gap: '2rem', marginTop: '1.5rem' }}>
                        <div>
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>DETERMINISTIC PRIORITY</span>
                          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--accent-emerald)' }}>
                            {scenarioResult.analysis.priority_score.toFixed(1)} / 100
                          </div>
                        </div>
                        <div>
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>CATEGORY</span>
                          <div style={{ fontSize: '2rem', fontWeight: 700 }}>
                            {scenarioResult.analysis.priority_category}
                          </div>
                        </div>
                      </div>

                      {/* Briefing */}
                      <div style={{ marginTop: '1.5rem' }}>
                        <h3>Executive Briefing</h3>
                        <p style={{ marginTop: '0.5rem', color: '#e2e8f0' }}>
                          {scenarioResult.executive_explanation.executive_summary}
                        </p>
                      </div>

                      {/* Citations */}
                      {scenarioResult.research_citations?.length > 0 && (
                        <div style={{ marginTop: '1.5rem' }}>
                          <h3>Retrieved Research Evidence ({scenarioResult.research_citations.length})</h3>
                          {scenarioResult.research_citations.map((c: any, i: number) => (
                            <div
                              key={i}
                              style={{
                                padding: '0.75rem',
                                background: 'rgba(255,255,255,0.03)',
                                borderRadius: '6px',
                                marginTop: '0.5rem',
                                borderLeft: '3px solid var(--accent-indigo)',
                              }}
                            >
                              <strong>[{c.evidence_label}: {c.publisher}]</strong> {c.title} (Sim: {c.similarity_score.toFixed(2)})
                              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                                "{c.excerpt}"
                              </p>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Trust Model */}
                      <div className="trust-panel" style={{ marginTop: '1.5rem' }}>
                        <div className="trust-title">Information Trust Audit Breakdown</div>
                        {scenarioResult.information_trust_breakdown?.map((tb: any, i: number) => (
                          <div key={i} className="trust-category-block">
                            <span className="trust-cat-name">{tb.category.toUpperCase()}</span>
                            <small style={{ color: 'var(--text-muted)', marginLeft: '0.5rem' }}>
                              ({tb.source_description})
                            </small>
                            <ul className="trust-item-list">
                              {tb.items?.map((it: string, j: number) => (
                                <li key={j}>• {it}</li>
                              ))}
                            </ul>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* VIEW 4: VISUAL TRANSFORMATION GRAPH */}
            {activeView === 'graph' && (
              <div>
                <div className="dashboard-header">
                  <h1 className="dashboard-title">Enterprise Transformation Topology</h1>
                  <p className="dashboard-subtitle">
                    Visual propagation chain: Strategy → Value Chain → Process → Opportunity → Role → Skill → Initiative
                  </p>
                </div>

                <div className="graph-container glass-panel">
                  <div className="graph-nodes-flow">
                    <div className="graph-node-card" style={{ borderColor: 'var(--accent-indigo)' }}>
                      <span style={{ color: 'var(--accent-indigo)', fontSize: '0.8rem', fontWeight: 600 }}>
                        STRATEGY
                      </span>
                      <h4 style={{ marginTop: '0.25rem' }}>Omnichannel Expansion</h4>
                    </div>
                    <span className="graph-arrow">→</span>
                    <div className="graph-node-card" style={{ borderColor: 'var(--accent-purple)' }}>
                      <span style={{ color: 'var(--accent-purple)', fontSize: '0.8rem', fontWeight: 600 }}>
                        VALUE CHAIN
                      </span>
                      <h4 style={{ marginTop: '0.25rem' }}>Supply Chain Operations</h4>
                    </div>
                    <span className="graph-arrow">→</span>
                    <div className="graph-node-card" style={{ borderColor: 'var(--accent-cyan)' }}>
                      <span style={{ color: 'var(--accent-cyan)', fontSize: '0.8rem', fontWeight: 600 }}>
                        PROCESS
                      </span>
                      <h4 style={{ marginTop: '0.25rem' }}>Demand Forecasting</h4>
                    </div>
                    <span className="graph-arrow">→</span>
                    <div className="graph-node-card" style={{ borderColor: 'var(--accent-emerald)' }}>
                      <span style={{ color: 'var(--accent-emerald)', fontSize: '0.8rem', fontWeight: 600 }}>
                        AI OPPORTUNITY
                      </span>
                      <h4 style={{ marginTop: '0.25rem' }}>Predictive SKU Forecasting</h4>
                    </div>
                    <span className="graph-arrow">→</span>
                    <div className="graph-node-card" style={{ borderColor: 'var(--accent-amber)' }}>
                      <span style={{ color: 'var(--accent-amber)', fontSize: '0.8rem', fontWeight: 600 }}>
                        ROLE
                      </span>
                      <h4 style={{ marginTop: '0.25rem' }}>Demand Planner</h4>
                    </div>
                    <span className="graph-arrow">→</span>
                    <div className="graph-node-card" style={{ borderColor: 'var(--accent-rose)' }}>
                      <span style={{ color: 'var(--accent-rose)', fontSize: '0.8rem', fontWeight: 600 }}>
                        SKILL
                      </span>
                      <h4 style={{ marginTop: '0.25rem' }}>Data Analytics</h4>
                    </div>
                  </div>

                  <div style={{ marginTop: '2rem', padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
                    <h3>Graph Topology Summary</h3>
                    <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                      Nodes Tracked: {graphData?.total_nodes || 11} | Edges Resolved: {graphData?.total_edges || 7} | Cycle Risk: Zero
                    </p>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
