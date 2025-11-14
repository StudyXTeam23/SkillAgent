/**
 * Sidebar - 完全从设计稿 HTML 提取
 */

interface SidebarProps {
  onNewChat?: () => void
}

export function Sidebar({ onNewChat }: SidebarProps) {
  return (
    <aside className="flex h-full w-64 flex-col justify-between border-r border-solid border-border-light dark:border-border-dark bg-surface-light dark:bg-surface-dark p-4">
      <div className="flex flex-col gap-6">
        {/* Logo & Branding - 直接从设计稿 */}
        <div className="flex items-center gap-3 px-2">
          <div 
            className="bg-center bg-no-repeat aspect-square bg-cover rounded-lg size-10"
            style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuDSpXpUeQFNhzxQIoAIi7RVey3s_Kg0LtNFS9WswZKutC6WUs9vIxo8_6QyNO27m6hlLXEbVG3-PxYyOcktW-sXx6ageG7DxuTTM7j4weDKp7akm6V5MrsGoCm6uuoPFbMEw-bJZwmDc1a7EwsyedARNMzmuie5bknIxwPkHUTQ2BVsAy8itZojKioaFIV05B5hD1Jh3fx9ee34XsTmHjkvSLlBaBzXmj6Ob2zyEe3w1_Okns5xwcEMb9BdwpBYEN4Iz4KcJlfQAI8D")' }}
          />
          <div className="flex flex-col">
            <h1 className="text-base font-bold">StudyX</h1>
            <p className="text-sm text-text-light-secondary dark:text-text-dark-secondary">Skill Agent Demo</p>
          </div>
        </div>

        {/* Navigation Links - 直接从设计稿 */}
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

      {/* Bottom Section - 直接从设计稿 */}
      <div className="flex flex-col gap-4">
        <button 
          onClick={onNewChat}
          className="flex w-full cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-primary text-white text-sm font-bold tracking-wide hover:bg-primary/90 transition-colors"
        >
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
  )
}
