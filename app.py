'use client'

import { useEffect, useState, useRef, useCallback } from 'react'

const REDIRECT_DELAY = 5

// 🏢 ✅ USER DB SERVICE URL (Next.js API)
const HF_USER_SERVICE_URL = "https://bfa-next-api.vercel.app"

// Mobile approved list
const APPROVED_USERS_URL = `${HF_USER_SERVICE_URL}/api/mobile-users`

// Auto register
const AUTO_REGISTER_API = `${HF_USER_SERVICE_URL}/api/auto-register`

const DEFAULT_SEASON_PASS = "2026-08-20T23:59:59Z"

// Background AI Poster
const BG_IMAGE_URL = "welcomebg.png"
// Free ကြည့်ရန် လင့်ခ်
const FREE_WATCH_URL = "https://bamarthan.vercel.app"
// 💳 သက်တမ်းတိုးရန် Activation Page
const PAYMENT_PAGE_URL = "/activation"

export default function Page() {
  const [deviceID, setDeviceID] = useState(null)
  const [expiryDate, setExpiryDate] = useState(null)
  const [userName, setUserName] = useState(null)
  const [status, setStatus] = useState('loading')
  const [isExpired, setIsExpired] = useState(false)
  const [countdown, setCountdown] = useState(REDIRECT_DELAY)
  const [copied, setCopied] = useState(false)
  const [isOffline, setIsOffline] = useState(false)
  const timerRef = useRef(null)

  const generateFingerprintId = useCallback(() => {
    if (typeof window === 'undefined') return null
    let id = localStorage.getItem('zetflix_device_id_mob')
    if (id) return id

    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.textBaseline = "alphabetic"
      ctx.font = "14px Arial"
      ctx.fillText('BFA STREAM-MOBILE-2026', 2, 15)
      const b64 = canvas.toDataURL().replace("data:image/png;base64,", "")
      let hash = 0
      for (let i = 0; i < b64.length; i++) {
        hash = (hash << 5) - hash + b64.charCodeAt(i)
        hash |= 0
      }
      const platformInfo = navigator.userAgent + screen.width + screen.height
      let finalHash = hash
      for (let j = 0; j < platformInfo.length; j++) {
        finalHash = (finalHash << 5) - finalHash + platformInfo.charCodeAt(j)
      }
      const finalID = Math.abs(finalHash).toString().padStart(12, "0").slice(0, 12) + "mob"
      localStorage.setItem('zetflix_device_id_mob', finalID)
      return finalID
    }
    return "MOB-" + Math.random().toString(36).substr(2, 9).toUpperCase()
  }, [])

  const redirect = (id, expires, name) => {
    localStorage.setItem('zetflix_approved', 'true')
    localStorage.setItem('zetflix_device_id_mob', id)
    localStorage.setItem('zetflix_expiry', expires || '')
    if (name) localStorage.setItem('zetflix_user_name', name)
    window.location.href = '/About.html'
  }

  const checkAccess = useCallback(async (id) => {
    try {
      setIsOffline(false)
      setStatus('loading')

      // 🔄 1. mobile_approve_user.json ထဲက စစ်ဆေးခြင်း
      const res = await fetch(`${APPROVED_USERS_URL}?_t=${Date.now()}`, {
        cache: 'no-store',
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache'
        }
      })

      const approvedUsers = res.ok ? await res.json() : []
      let user = Array.isArray(approvedUsers)
        ? approvedUsers.find(u => String(u.id) === String(id))
        : null

      // 🔄 2. JSON ထဲမှာ မရှိသေးရင် auto_register ကို လှမ်းခေါ်ခြင်း
      if (!user) {
        try {
          const registerRes = await fetch(AUTO_REGISTER_API, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              id: String(id),
              type: "phone"
            })
          })

          if (registerRes.ok) {
            const regData = await registerRes.json()
            user = regData.user || { id: id, expires: DEFAULT_SEASON_PASS }
          } else {
            user = { id: id, expires: DEFAULT_SEASON_PASS }
          }
        } catch (regErr) {
          console.warn("Auto register bypass active:", regErr)
          user = { id: id, expires: DEFAULT_SEASON_PASS }
        }
      }

      // 🚀 3. User ရှိသွားပြီဆိုရင် သက်တမ်း စစ်ဆေးခြင်း (Timestamp Precision Logic)
      if (user) {
        setUserName(user.name || "Mobile User")
        setExpiryDate(user.expires)

        // Phone Time ကို UTC Timestamp ဖြင့် တွက်ချက်ခြင်း
        const currentTime = new Date().getTime()
        const rawExpiry = user.expires || DEFAULT_SEASON_PASS
        const expiryTime = new Date(rawExpiry).getTime()

        // Phone Date ကို အနာဂတ်ပြောင်းထားရင် ချက်ချင်း Expired ဖြစ်စေရန်
        if (isNaN(expiryTime) || currentTime > expiryTime) {
          setIsExpired(true)
          setStatus('denied')
        } else {
          setIsExpired(false)
          setStatus('approved')
          if (timerRef.current) clearInterval(timerRef.current)
          timerRef.current = setInterval(() => {
            setCountdown(prev => {
              if (prev <= 1) {
                clearInterval(timerRef.current)
                redirect(id, user.expires, user.name || "Mobile User")
                return 0
              }
              return prev - 1
            })
          }, 1000)
        }
      } else {
        setStatus('denied')
      }
    } catch (e) {
      console.error("Network Check Error:", e)
      setIsOffline(true)
      setStatus('denied')
    }
  }, [])

  useEffect(() => {
    const id = generateFingerprintId()
    setDeviceID(id)
    if (id) checkAccess(id)
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [generateFingerprintId, checkAccess])

  const handleCopy = () => {
    if (!deviceID) return
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(deviceID)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } else {
      const textArea = document.createElement("textarea")
      textArea.value = deviceID
      textArea.style.position = "fixed"
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      try {
        document.execCommand('copy')
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } catch (err) {
        console.error('Copy Error', err)
      }
      document.body.removeChild(textArea)
    }
  }

  if (status === 'loading') {
    return (
      <div className="fixed inset-0 z-[999] bg-slate-950 flex flex-col items-center justify-center p-6 text-white text-center w-full h-screen">
        <div className="relative flex h-14 w-14 items-center justify-center mb-6">
          <div className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400/20 opacity-75"></div>
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-yellow-400 border-r-transparent"></div>
        </div>
        <h2 className="text-2xl font-black tracking-widest text-yellow-400 uppercase italic">BFA STREAM</h2>
        <p className="text-white/40 text-[10px] mt-2 uppercase tracking-[0.3em] font-bold animate-pulse">လုံခြုံရေး စစ်ဆေးနေပါသည်...</p>
      </div>
    )
  }

  return (
    <div className="relative flex h-screen w-screen items-center justify-center overflow-hidden bg-slate-950 font-sans antialiased selection:bg-yellow-400 selection:text-black">

      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat transition-transform duration-1000 scale-105 opacity-75"
        style={{ backgroundImage: `url('${BG_IMAGE_URL}')` }}
      />

      <div className="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-slate-950/40 to-slate-900/20 backdrop-blur-[4px]" />

      <div className="relative z-10 w-full max-w-sm sm:max-w-md p-4 mx-auto">
        <div className="overflow-hidden rounded-3xl border border-white/10 bg-slate-900/80 p-6 sm:p-8 shadow-2xl backdrop-blur-xl text-center">

          <div className="mb-5 flex flex-col items-center">
            <span className="text-2xl sm:text-3xl font-black tracking-tighter text-yellow-400 leading-none drop-shadow-lg uppercase">
              BFA STREAM
            </span>
            <span className="mt-1.5 text-[9px] font-bold tracking-widest text-white/40 uppercase">
              Premium Gate Mobile
            </span>
          </div>

          <hr className="w-12 mx-auto border-t border-white/10 mb-5" />

          {status === 'approved' && (
            <div className="py-2 flex flex-col items-center justify-center animate-fadeIn">
              <div className="w-14 h-14 bg-green-500/10 border border-green-500/30 rounded-full flex items-center justify-center mb-4 text-green-400 text-xl shadow-[0_0_20px_rgba(34,197,94,0.15)]">
                ✓
              </div>

              <h2 className="text-sm font-bold text-white/95">ခွင့်ပြုချက် အောင်မြင်ပါသည်</h2>
              <p className="text-[11px] text-white/50 mt-0.5">
                မင်္ဂလာပါ <span className="text-green-400 font-bold">{userName}</span>, ပင်မစာမျက်နှာသို့ သွားနေသည်...
              </p>

              <div className="relative w-24 h-24 mx-auto my-6">
                <svg className="w-full h-full -rotate-90">
                  <circle cx="48" cy="48" r="42" className="stroke-white/5 fill-none" strokeWidth="5" />
                  <circle
                    cx="48" cy="48" r="42"
                    className="stroke-yellow-400 fill-none transition-all duration-1000"
                    strokeWidth="5"
                    strokeDasharray="263.8"
                    strokeDashoffset={263.8 - (263.8 * (countdown / REDIRECT_DELAY))}
                    strokeLinecap="round"
                  />
                </svg>
                <span className="absolute inset-0 flex items-center justify-center text-2xl font-black text-yellow-400">
                  {countdown}
                </span>
              </div>

              <button
                onClick={() => redirect(deviceID, expiryDate, userName)}
                className="w-full bg-yellow-400 hover:bg-yellow-300 text-black font-black py-3.5 text-xs rounded-xl transition-all shadow-lg shadow-yellow-400/20 active:scale-95 uppercase tracking-wider"
              >
                Enter Now
              </button>
            </div>
          )}

          {status === 'denied' && (
            <div className="text-left animate-fadeIn">
              {isOffline ? (
                <div className="text-center py-4">
                  <div className="w-16 h-16 bg-red-500/10 border border-red-500/30 rounded-full flex items-center justify-center mx-auto mb-4 text-red-400 shadow-[0_0_20px_rgba(239,68,68,0.15)]">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m0-8v4m-9 5h18c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2H3c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2z"></path>
                    </svg>
                  </div>
                  <h2 className="text-sm font-black text-white uppercase tracking-wide mb-1">Connection Lost</h2>
                  <p className="mb-6 text-[12px] text-white/60 leading-relaxed px-2">
                    အင်တာနက် ချိတ်ဆက်မှုကို စစ်ဆေးပြီး ပြန်လည်ကြိုးစားပါ။
                  </p>

                  <button
                    onClick={() => checkAccess(deviceID)}
                    className="w-full bg-yellow-400 hover:bg-yellow-300 text-black font-black py-3.5 text-xs rounded-xl transition-all shadow-lg shadow-yellow-400/20 active:scale-95 uppercase tracking-wider"
                  >
                    Retry Connection
                  </button>
                </div>
              ) : (
                <div>
                  <div className="flex items-center gap-2 mb-3 text-red-400">
                    <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
                    <h2 className="text-xs sm:text-sm font-black uppercase tracking-wide">ဝင်ရောက်ခွင့်မရှိပါ</h2>
                  </div>

                  <p className="mb-4 text-[12px] sm:text-[13px] text-white/80 leading-relaxed font-medium">
                    {isExpired
                      ? 'သင်၏ Premium သက်တမ်းကုန်ဆုံးသွားပါပြီ။ ဆက်လက်ကြည့်ရှုရန် ကျေးဇူးပြု၍ သက်တမ်းတိုးပေးပါ။'
                      : 'ဝဘ်ဆိုဒ်ကို အသုံးပြုရန် ခွင့်ပြုချက်မရှိသေးပါ။ ကျေးဇူးပြု၍ အောက်ပါ Device ID ကို ကူးယူပြီး တာဝန်ရှိသူထံ ပေးပို့ပါ။'}
                  </p>

                  <div className="mb-4 rounded-2xl bg-black/60 border border-white/10 p-3.5 flex items-center justify-between shadow-inner">
                    <p className="break-all font-mono text-xs text-yellow-400 font-bold tracking-wider select-all pr-2">
                      {deviceID || 'Generating...'}
                    </p>
                  </div>

                  <div className="flex flex-col gap-2.5">
                    {isExpired ? (
                      <a
                        href={`${PAYMENT_PAGE_URL}?id=${deviceID}`}
                        className="w-full rounded-xl bg-gradient-to-r from-amber-500 to-yellow-400 py-3.5 text-xs font-black text-black transition-all hover:from-amber-400 hover:to-yellow-300 active:scale-95 uppercase tracking-wider text-center block shadow-lg shadow-yellow-500/10"
                      >
                        💎 သက်တမ်းတိုးရန် (Payment သို့)
                      </a>
                    ) : (
                      <button
                        onClick={handleCopy}
                        className="w-full rounded-xl bg-white/10 border border-white/10 py-3.5 text-xs font-black text-white transition-all hover:bg-white/20 active:scale-95 uppercase tracking-wider text-center"
                      >
                        {copied ? 'ID ကူးယူပြီးပါပြီ ✓' : 'ခွင့်ပြုချက်ရယူရန် ID ကူးယူမည်'}
                      </button>
                    )}

                    <a
                      href={FREE_WATCH_URL}
                      className="w-full rounded-xl bg-white/5 border border-white/5 py-3.5 text-xs font-black text-white/60 transition-all hover:bg-white/10 hover:text-white active:scale-95 uppercase tracking-wider text-center block"
                    >
                      Free ဗားရှင်းဖြင့် ကြည့်ရှုရန်
                    </a>
                  </div>
                </div>
              )}
            </div>
          )}

        </div>
      </div>

      <footer className="absolute bottom-6 left-0 right-0 text-center opacity-25 text-[8px] text-white uppercase tracking-[0.4em] font-bold">
        BFA STREAM Mobile Control v2.3
      </footer>
    </div>
  )
}
