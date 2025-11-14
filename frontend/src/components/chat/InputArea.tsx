/**
 * InputArea - 完全从设计稿 HTML 提取
 */
import { useState } from 'react'
import type { KeyboardEvent } from 'react'

interface InputAreaProps {
  onSend: (message: string) => void
  isLoading: boolean
}

export function InputArea({ onSend, isLoading }: InputAreaProps) {
  const [input, setInput] = useState('')

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSend(input.trim())
      setInput('')
    }
  }

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="relative">
      <input 
        className="w-full h-12 px-4 pr-12 rounded-lg bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark focus:ring-2 focus:ring-primary focus:outline-none transition-shadow text-text-light-primary dark:text-text-dark-primary placeholder-text-light-secondary dark:placeholder-text-dark-secondary"
        placeholder="Ask a calculus question or type your answer..."
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyPress}
        disabled={isLoading}
      />
      <button 
        className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center justify-center size-8 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors disabled:opacity-50"
        onClick={handleSend}
        disabled={!input.trim() || isLoading}
      >
        <span className="material-symbols-outlined text-xl">send</span>
      </button>
    </div>
  )
}
