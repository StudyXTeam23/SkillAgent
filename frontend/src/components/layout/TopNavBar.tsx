/**
 * TopNavBar - 完全从设计稿 HTML 提取
 */

interface TopNavBarProps {
  sessionTitle?: string
}

export function TopNavBar({ sessionTitle = 'Calculus Practice Session' }: TopNavBarProps) {
  return (
    <header className="flex h-16 items-center justify-between whitespace-nowrap border-b border-solid border-border-light dark:border-border-dark px-6 bg-surface-light dark:bg-surface-dark">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-bold tracking-tight">{sessionTitle}</h2>
      </div>
      <div className="flex flex-1 items-center justify-end gap-4">
        <button className="flex cursor-pointer items-center justify-center overflow-hidden rounded-lg size-10 bg-primary/10 text-text-light-primary dark:text-text-dark-primary hover:bg-primary/20 transition-colors">
          <span className="material-symbols-outlined text-xl">notifications</span>
        </button>
        <button className="flex cursor-pointer items-center justify-center overflow-hidden rounded-lg size-10 bg-primary/10 text-text-light-primary dark:text-text-dark-primary hover:bg-primary/20 transition-colors">
          <span className="material-symbols-outlined text-xl">bolt</span>
        </button>
        <div 
          className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10"
          style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuC2JV0TerXdmHAVpbSKv_E1GuCwolwncFI-4GV6gTe4KD7jb6L14FEWUoI9GNNTmFjCICvExlwaH0u-Xlc__WwIhFeFn3tGycB_um-i2WDCBZ8qh8z4mzXJSai0ODWV21ZaxGiyMm-Xot9-QBjSTEmRiy_zgJShKMe01fF7msbIDwkAsrstdzzcpXlnafKBGO39znKCb-jbgC-p4Eakjg_qCdJ4FqHjX2gefcJUbHapvopm943I8lcboavCnjZrtm0h5-VQbnuXjwps")' }}
        />
      </div>
    </header>
  )
}
