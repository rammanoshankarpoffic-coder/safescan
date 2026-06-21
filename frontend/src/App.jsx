import { useEffect, useRef, useState, useCallback } from 'react'
import { Html5Qrcode } from 'html5-qrcode'
import './App.css'

// Backend API base. When demoing on your laptop with phone on the same
// Wi-Fi, replace 'localhost' with your laptop's local IP (e.g. 192.168.1.42).
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const SCANNER_ELEMENT_ID = 'qr-reader'

function App() {
  const [screen, setScreen] = useState('scan') // 'scan' | 'analyzing' | 'result' | 'error'
  const [result, setResult] = useState(null)
  const [errorMsg, setErrorMsg] = useState('')
  const scannerRef = useRef(null)
  const isRunningRef = useRef(false)

  const stopScanner = useCallback(async () => {
    if (scannerRef.current && isRunningRef.current) {
      try {
        await scannerRef.current.stop()
        isRunningRef.current = false
      } catch (e) {
        // already stopped, ignore
      }
    }
  }, [])

  const handleScanSuccess = useCallback(async (decodedText) => {
    if (!isRunningRef.current) return // ignore duplicate fires after stop
    await stopScanner()
    setScreen('analyzing')

    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payload: decodedText }),
      })
      if (!res.ok) throw new Error(`Server responded ${res.status}`)
      const data = await res.json()
      setResult(data)
      setScreen('result')
    } catch (err) {
      setErrorMsg(
        'Could not reach SafeScan server. Check that the backend is running and reachable on your network.'
      )
      setScreen('error')
    }
  }, [stopScanner])

  useEffect(() => {
    if (screen !== 'scan') return

    const qr = new Html5Qrcode(SCANNER_ELEMENT_ID)
    scannerRef.current = qr

    qr.start(
      { facingMode: 'environment' },
      { fps: 10, qrbox: { width: 240, height: 240 } },
      handleScanSuccess,
      () => {} // ignore per-frame "no QR found" errors
    )
      .then(() => {
        isRunningRef.current = true
      })
      .catch(() => {
        setErrorMsg(
          'Could not access camera. Please allow camera permission and reload.'
        )
        setScreen('error')
      })

    return () => {
      if (isRunningRef.current) {
        qr.stop().catch(() => {})
        isRunningRef.current = false
      }
    }
  }, [screen, handleScanSuccess])

  const scanAgain = () => {
    setResult(null)
    setErrorMsg('')
    setScreen('scan')
  }

  return (
    <div className="app">
      <header className="topbar">
        <span className="brand-mark">◈</span>
        <span className="brand-name">SafeScan</span>
      </header>

      {screen === 'scan' && (
        <ScanScreen />
      )}

      {screen === 'analyzing' && <AnalyzingScreen />}

      {screen === 'result' && (
        <ResultScreen result={result} onScanAgain={scanAgain} />
      )}

      {screen === 'error' && (
        <ErrorScreen message={errorMsg} onRetry={scanAgain} />
      )}
    </div>
  )
}

function ScanScreen() {
  return (
    <div className="scan-screen">
      <div id={SCANNER_ELEMENT_ID} className="camera-feed" />
      <div className="reticle">
        <span className="corner tl" />
        <span className="corner tr" />
        <span className="corner bl" />
        <span className="corner br" />
      </div>
      <p className="scan-hint">Point camera at a QR code</p>
      <p className="scan-sub">We check it before you pay — nothing is sent or paid automatically</p>
    </div>
  )
}

function AnalyzingScreen() {
  return (
    <div className="status-screen">
      <div className="spinner" />
      <p className="status-text">Checking this code…</p>
    </div>
  )
}

function riskMeta(level) {
  switch (level) {
    case 'LOW':
      return { label: 'LOOKS SAFE', className: 'risk-low' }
    case 'MEDIUM':
      return { label: 'BE CAUTIOUS', className: 'risk-medium' }
    case 'HIGH':
    default:
      return { label: 'DO NOT PROCEED', className: 'risk-high' }
  }
}

function ResultScreen({ result, onScanAgain }) {
  const meta = riskMeta(result.risk_level)

  return (
    <div className={`result-screen ${meta.className}`}>
      <div className="result-badge">
        <span className="result-level">{meta.label}</span>
        <span className="result-score">{result.trust_score}<span className="score-unit">/100</span></span>
      </div>

      <div className="result-type">
        <span className="type-label">Content type</span>
        <span className="type-value">{labelForType(result.payload_type)}</span>
      </div>

      <div className="reasons-block">
        <span className="reasons-title">Why</span>
        <ul className="reasons-list">
          {result.reasons.map((reason, i) => (
            <li key={i}>{reason}</li>
          ))}
        </ul>
      </div>

      <div className="payload-block">
        <span className="payload-label">Scanned content</span>
        <code className="payload-value">{result.payload}</code>
      </div>

      <button className="scan-again-btn" onClick={onScanAgain}>
        Scan another code
      </button>
    </div>
  )
}

function labelForType(type) {
  if (type === 'upi') return 'UPI Payment'
  if (type === 'url') return 'Web Link'
  return 'Plain Text'
}

function ErrorScreen({ message, onRetry }) {
  return (
    <div className="status-screen error">
      <p className="status-text">{message}</p>
      <button className="scan-again-btn" onClick={onRetry}>
        Try again
      </button>
    </div>
  )
}

export default App
