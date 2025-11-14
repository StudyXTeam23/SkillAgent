/**
 * ChatInterface - 主聊天界面（完整按照设计稿）
 */
import { useEffect, useRef } from 'react'
import { useChat } from '../../contexts/ChatContext'
import { MessageList } from './MessageList'
import { InputArea } from './InputArea'
import { useAgent } from '../../hooks/useAgent'

export function ChatInterface() {
  const { messages, isLoading } = useChat()
  const { sendMessage } = useAgent()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <>
      {/* Chat Area - 完全匹配设计稿 */}
      <div className="flex flex-1 flex-col overflow-y-auto px-6 pt-6">
        {/* Chat Messages */}
        <div className="flex flex-col gap-6">
          {messages.length === 0 ? (
            /* Welcome Message */
            <div className="flex items-end gap-3 max-w-2xl">
              <div 
                className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 shrink-0"
                style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuCxe92kEf7gMHjbEHfZQu3F-p4XUO0nyA37zYAuOz7CiVXM_3hgmQ9gTI6zw7siePySKKolumdfXax7FjZ1tuLAnsb5rDYnZjw4LaKpR0MpYWUilv2DSX2VlCD416jAvXmMW3d3TA0MfMgLOkvyyvAqiNcFnqdLIk1LOdKh1Axylm3hUbhf-JtzopMhBhZ5WxEDvTgpGF0E65VLCr805vqY4iosbw4L8Qmm-sViAPSF8dXyszl2XldUnwHCnAakeX7o04PO1S6iwT_m")' }}
              />
              <div className="flex flex-1 flex-col gap-1 items-start">
                <p className="text-text-light-secondary dark:text-text-dark-secondary text-sm font-medium">StudyX Agent</p>
                <p className="text-base font-normal leading-normal rounded-xl rounded-bl-none px-4 py-3 bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark text-text-light-primary dark:text-text-dark-primary">
                  开始和 AI 学习助手对话吧！你可以尝试：<br/>
                  💡 "给我几道微积分极限的练习题"<br/>
                  📚 "什么是牛顿第二定律？"<br/>
                  🧪 "解释一下光合作用"
                </p>
              </div>
            </div>
          ) : (
            <MessageList messages={messages} />
          )}
          <div ref={messagesEndRef} />
        </div>
        <div className="flex-grow" /> {/* Spacer to push content up */}
      </div>
      
      {/* Text Input Area */}
      <div className="px-6 pb-6 pt-4 bg-background-light dark:bg-background-dark">
        <InputArea onSend={sendMessage} isLoading={isLoading} />
      </div>
    </>
  )
}
