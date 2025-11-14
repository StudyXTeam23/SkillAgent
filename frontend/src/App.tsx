/**
 * App - 完全照搬设计稿 HTML
 */
import { ThemeProvider } from './contexts/ThemeContext'
import { ChatProvider, useChatDispatch } from './contexts/ChatContext'
import { useChat } from './contexts/ChatContext'
import { useAgent } from './hooks/useAgent'
import { useEffect, useRef, useState } from 'react'
import './index.css'

function ChatContent() {
  const { messages, isLoading } = useChat()
  const { sendMessage } = useAgent()
  const dispatch = useChatDispatch()
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      sendMessage(input.trim())
      setInput('')
    }
  }

  const handleNewChat = () => {
    dispatch({ type: 'CLEAR_MESSAGES' })
  }

  return (
    <div className="flex h-screen w-full">
      {/* SideNavBar - 完全复制设计稿 */}
      <aside className="flex h-full w-64 flex-col justify-between border-r border-border-light dark:border-border-dark bg-surface-light dark:bg-surface-dark p-4">
        <div className="flex flex-col gap-6">
          <div className="flex items-center gap-3 px-2">
            <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-lg size-10" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuDSpXpUeQFNhzxQIoAIi7RVey3s_Kg0LtNFS9WswZKutC6WUs9vIxo8_6QyNO27m6hlLXEbVG3-PxYyOcktW-sXx6ageG7DxuTTM7j4weDKp7akm6V5MrsGoCm6uuoPFbMEw-bJZwmDc1a7EwsyedARNMzmuie5bknIxwPkHUTQ2BVsAy8itZojKioaFIV05B5hD1Jh3fx9ee34XsTmHjkvSLlBaBzXmj6Ob2zyEe3w1_Okns5xwcEMb9BdwpBYEN4Iz4KcJlfQAI8D")' }} />
            <div className="flex flex-col">
              <h1 className="text-base font-bold">StudyX</h1>
              <p className="text-sm text-text-light-secondary dark:text-text-dark-secondary">Skill Agent Demo</p>
            </div>
          </div>
          <div className="flex flex-col gap-1">
            <a className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 transition-colors" href="#">
              <span className="material-symbols-outlined text-xl">dashboard</span>
              <p className="text-sm font-medium">Dashboard</p>
            </a>
            <a className="flex items-center gap-3 px-3 py-2 rounded-lg bg-primary/10 text-primary" href="#">
              <span className="material-symbols-outlined text-xl">calculate</span>
              <p className="text-sm font-bold">Calculus Practice</p>
            </a>
            <a className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 transition-colors" href="#">
              <span className="material-symbols-outlined text-xl">lightbulb</span>
              <p className="text-sm font-medium">Concept Explanation</p>
            </a>
            <a className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 transition-colors" href="#">
              <span className="material-symbols-outlined text-xl">functions</span>
              <p className="text-sm font-medium">Integration by Parts</p>
            </a>
          </div>
        </div>
        <div className="flex flex-col gap-4">
          <button onClick={handleNewChat} className="flex w-full cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-primary text-white text-sm font-bold tracking-wide hover:bg-primary/90 transition-colors">
            <span className="truncate">New Chat</span>
          </button>
          <div className="flex flex-col gap-1">
            <a className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 transition-colors" href="#">
              <span className="material-symbols-outlined text-xl">settings</span>
              <p className="text-sm font-medium">Settings</p>
            </a>
            <a className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 transition-colors" href="#">
              <span className="material-symbols-outlined text-xl">help</span>
              <p className="text-sm font-medium">Help</p>
            </a>
          </div>
        </div>
      </aside>

      {/* Main Content Area - 完全复制设计稿 */}
      <main className="flex flex-1 flex-col">
        {/* TopNavBar - 完全复制设计稿 */}
        <header className="flex h-16 items-center justify-between whitespace-nowrap border-b border-solid border-border-light dark:border-border-dark px-6 bg-surface-light dark:bg-surface-dark">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-bold tracking-tight">Calculus Practice Session</h2>
          </div>
          <div className="flex flex-1 items-center justify-end gap-4">
            <button className="flex cursor-pointer items-center justify-center overflow-hidden rounded-lg size-10 bg-primary/10 text-text-light-primary dark:text-text-dark-primary hover:bg-primary/20 transition-colors">
              <span className="material-symbols-outlined text-xl">notifications</span>
            </button>
            <button className="flex cursor-pointer items-center justify-center overflow-hidden rounded-lg size-10 bg-primary/10 text-text-light-primary dark:text-text-dark-primary hover:bg-primary/20 transition-colors">
              <span className="material-symbols-outlined text-xl">bolt</span>
            </button>
            <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuC2JV0TerXdmHAVpbSKv_E1GuCwolwncFI-4GV6gTe4KD7jb6L14FEWUoI9GNNTmFjCICvExlwaH0u-Xlc__WwIhFeFn3tGycB_um-i2WDCBZ8qh8z4mzXJSai0ODWV21ZaxGiyMm-Xot9-QBjSTEmRiy_zgJShKMe01fF7msbIDwkAsrstdzzcpXlnafKBGO39znKCb-jbgC-p4Eakjg_qCdJ4FqHjX2gefcJUbHapvopm943I8lcboavCnjZrtm0h5-VQbnuXjwps")' }} />
          </div>
        </header>

        {/* Chat Area - 完全复制设计稿 */}
        <div className="flex flex-1 flex-col overflow-y-auto px-6 pt-6">
          <div className="flex flex-col gap-6">
            {messages.length === 0 ? (
              <div className="flex items-end gap-3 max-w-2xl">
                <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 shrink-0" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuCxe92kEf7gMHjbEHfZQu3F-p4XUO0nyA37zYAuOz7CiVXM_3hgmQ9gTI6zw7siePySKKolumdfXax7FjZ1tuLAnsb5rDYnZjw4LaKpR0MpYWUilv2DSX2VlCD416jAvXmMW3d3TA0MfMgLOkvyyvAqiNcFnqdLIk1LOdKh1Axylm3hUbhf-JtzopMhBhZ5WxEDvTgpGF0E65VLCr805vqY4iosbw4L8Qmm-sViAPSF8dXyszl2XldUnwHCnAakeX7o04PO1S6iwT_m")' }} />
                <div className="flex flex-1 flex-col gap-1 items-start">
                  <p className="text-text-light-secondary dark:text-text-dark-secondary text-sm font-medium">StudyX Agent</p>
                  <p className="text-base font-normal leading-normal rounded-xl rounded-bl-none px-4 py-3 bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark text-text-light-primary dark:text-text-dark-primary">
                    开始和 AI 学习助手对话吧！
                  </p>
                </div>
              </div>
            ) : (
              messages.map((msg) => (
                msg.role === 'user' ? (
                  <div key={msg.id} className="flex items-end gap-3 justify-end max-w-2xl self-end">
                    <div className="flex flex-1 flex-col gap-1 items-end">
                      <p className="text-text-light-secondary dark:text-text-dark-secondary text-sm font-medium text-right">User</p>
                      <p className="text-base font-normal leading-normal rounded-xl rounded-br-none px-4 py-3 bg-primary text-white">
                        {msg.content}
                      </p>
                    </div>
                    <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 shrink-0" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuArOSw_thOdEPdwA2mvCtr7bEwI1o26yboOOAitTWIHYDPmbnNwTq9qItlBoeGCOr1aJjqMhNBQ6lKQ0-FywpKbLhS4HDngJqzdL16mCaOdDxYNZH0_JjfcAVaUUnkUUssz6tNH7d5-jAxm5SCFvP45wXOq1X3Pwznad2FF4YUy9U54XVc4pKeL7dCeWLUku3EEI8Ji5Xlx2TiG0YH8wH2sZucsahOVDTSIK3tjmHeMyEK779v0aYEOc-BEPveggYSTocakuyeLTCgr")' }} />
                  </div>
                ) : (
                  <div key={msg.id} className="flex items-end gap-3 max-w-2xl">
                    <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 shrink-0" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuCxe92kEf7gMHjbEHfZQu3F-p4XUO0nyA37zYAuOz7CiVXM_3hgmQ9gTI6zw7siePySKKolumdfXax7FjZ1tuLAnsb5rDYnZjw4LaKpR0MpYWUilv2DSX2VlCD416jAvXmMW3d3TA0MfMgLOkvyyvAqiNcFnqdLIk1LOdKh1Axylm3hUbhf-JtzopMhBhZ5WxEDvTgpGF0E65VLCr805vqY4iosbw4L8Qmm-sViAPSF8dXyszl2XldUnwHCnAakeX7o04PO1S6iwT_m")' }} />
                    <div className="flex flex-1 flex-col gap-1 items-start">
                      <p className="text-text-light-secondary dark:text-text-dark-secondary text-sm font-medium">StudyX Agent</p>
                      <p className="text-base font-normal leading-normal rounded-xl rounded-bl-none px-4 py-3 bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark text-text-light-primary dark:text-text-dark-primary">
                        {msg.content}
                      </p>
                    </div>
                  </div>
                )
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
          <div className="flex-grow"></div>
        </div>

        {/* Text Input Area - 完全复制设计稿 */}
        <div className="px-6 pb-6 pt-4 bg-background-light dark:bg-background-dark">
          <div className="relative">
            <input 
              className="w-full h-12 px-4 pr-12 rounded-lg bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark focus:ring-2 focus:ring-primary focus:outline-none transition-shadow text-text-light-primary dark:text-text-dark-primary placeholder-text-light-secondary dark:placeholder-text-dark-secondary"
              placeholder="Ask a calculus question or type your answer..."
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            />
            <button 
              onClick={handleSend}
              className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center justify-center size-8 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors"
            >
              <span className="material-symbols-outlined text-xl">send</span>
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}

function App() {
  return (
    <ThemeProvider>
      <ChatProvider>
        <div className="bg-background-light dark:bg-background-dark font-display text-text-light-primary dark:text-text-dark-primary">
          <ChatContent />
        </div>
      </ChatProvider>
    </ThemeProvider>
  )
}

export default App
