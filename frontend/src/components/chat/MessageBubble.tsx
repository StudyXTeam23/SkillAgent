/**
 * MessageBubble - 消息气泡（按照原始设计）
 */
import type { Message } from '../../contexts/ChatContext'
import { QuizCard } from '../artifacts/QuizCard'
import { ExplainCard } from '../artifacts/ExplainCard'
import { ErrorCard } from '../artifacts/ErrorCard'

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  const agentAvatar = 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuCxe92kEf7gMHjbEHfZQu3F-p4XUO0nyA37zYAuOz7CiVXM_3hgmQ9gTI6zw7siePySKKolumdfXax7FjZ1tuLAnsb5rDYnZjw4LaKpR0MpYWUilv2DSX2VlCD416jAvXmMW3d3TA0MfMgLOkvyyvAqiNcFnqdLIk1LOdKh1Axylm3hUbhf-JtzopMhBhZ5WxEDvTgpGF0E65VLCr805vqY4iosbw4L8Qmm-sViAPSF8dXyszl2XldUnwHCnAakeX7o04PO1S6iwT_m")'
  const userAvatar = 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuArOSw_thOdEPdwA2mvCtr7bEwI1o26yboOOAitTWIHYDPmbnNwTq9qItlBoeGCOr1aJjqMhNBQ6lKQ0-FywpKbLhS4HDngJqzdL16mCaOdDxYNZH0_JjfcAVaUUnkUUssz6tNH7d5-jAxm5SCFvP45wXOq1X3Pwznad2FF4YUy9U54XVc4pKeL7dCeWLUku3EEI8Ji5Xlx2TiG0YH8wH2sZucsahOVDTSIK3tjmHeMyEK779v0aYEOc-BEPveggYSTocakuyeLTCgr")'

  if (isUser) {
    return (
      <div className="flex items-end gap-3 justify-end max-w-2xl self-end">
        <div className="flex flex-1 flex-col gap-1 items-end">
          <p className="text-text-light-secondary dark:text-text-dark-secondary text-sm font-medium text-right">User</p>
          <p className="text-base font-normal leading-normal rounded-xl rounded-br-none px-4 py-3 bg-primary text-white">
            {message.content}
          </p>
        </div>
        <div 
          className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 shrink-0"
          style={{ backgroundImage: userAvatar }}
        />
      </div>
    )
  }

  return (
    <div className="flex items-end gap-3 max-w-2xl">
      <div 
        className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 shrink-0"
        style={{ backgroundImage: agentAvatar }}
      />
      <div className="flex flex-1 flex-col gap-1 items-start">
        <p className="text-text-light-secondary dark:text-text-dark-secondary text-sm font-medium">StudyX Agent</p>
        {message.content && !message.artifact && (
          <p className="text-base font-normal leading-normal rounded-xl rounded-bl-none px-4 py-3 bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark text-text-light-primary dark:text-text-dark-primary">
            {message.content}
          </p>
        )}
        {message.artifact && (
          <div className="w-full mt-2">
            {message.artifact.type === 'quiz_set' && <QuizCard data={message.artifact.data} />}
            {message.artifact.type === 'explanation' && <ExplainCard data={message.artifact.data} />}
            {message.artifact.type === 'error' && <ErrorCard message={message.artifact.data.message} />}
          </div>
        )}
      </div>
    </div>
  )
}
