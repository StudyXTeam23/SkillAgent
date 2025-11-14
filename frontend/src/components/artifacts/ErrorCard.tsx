/**
 * ErrorCard - 错误提示卡片
 */

interface ErrorCardProps {
  message: string
}

export function ErrorCard({ message }: ErrorCardProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 max-w-2xl">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <svg
            className="w-6 h-6 text-red-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-red-900 mb-1">出错了</h3>
          <p className="text-sm text-red-700">{message}</p>
        </div>
      </div>
    </div>
  )
}

